from flask import Flask, jsonify, render_template, request, redirect, url_for, send_from_directory, send_file, make_response, Markup
from app import app
from collections import Counter
import fiona
import json
import numpy as np
import os
import pandas as pd
import pymysql as mdb
import re
import secrets as sec
import shapely.geometry
from sklearn.cluster import DBSCAN
import sqlalchemy as sql


def getParkPhotos(parkname):
    ''' Returns photos from a park
    '''
    enginestr = 'mysql+pymysql://%s:%s@%s/parkpic?charset=utf8&use_unicode=1' % (sec.mysqluser, sec.mysqlpwd, sec.mysqlhost)
    engine = sql.create_engine(enginestr)

    query = """SELECT * FROM photos WHERE parkname="%s" 
            AND in_park="True" 
            AND canblog="1";""" % (parkname)
    photos = pd.read_sql(query, engine, params={'encoding':'utf8'})

    photos['latitude'] = photos.latitude.astype('float')
    photos['longitude'] = photos.longitude.astype('float')
    
    return photos

def isParkInDB(parkname):
    ''' Returns true if parkname in Database
    '''
    enginestr = 'mysql+pymysql://%s:%s@%s/parkpic?charset=utf8&use_unicode=1' % (sec.mysqluser, sec.mysqlpwd, sec.mysqlhost)
    engine = sql.create_engine(enginestr)
    
    query = "SELECT `parkname` FROM `parks` WHERE parkname=\"%s\";" % parkname
    result = list(engine.execute(query))

    if len(result) == 0:
        return False
    return True

def getParkInfo(parkname):
    ''' Returns information about the park from Database
    '''
    enginestr = 'mysql+pymysql://%s:%s@%s/parkpic?charset=utf8&use_unicode=1' % (sec.mysqluser, sec.mysqlpwd, sec.mysqlhost)
    engine = sql.create_engine(enginestr)
    
    query = "SELECT `latitude`, `longitude`, `boundary` FROM `parks` WHERE parkname=\"%s\";" % parkname
    result = list(engine.execute(query))
    return result[0]

def clusterPhotos(photos, eps=0.01, min_samples=10):
    ''' Performs the DBSCAN clustering of photos 
    '''
    locations = photos.as_matrix(columns=('longitude', 'latitude'))
    db = DBSCAN(eps=float(eps), min_samples=int(min_samples)).fit(locations)
    labels = db.labels_    
    photos['core'] = [True if i in db.core_sample_indices_ else False for i in range(0, len(labels))]
    photos['label'] = labels

    return photos, labels.max()+1

def getClusterPhotosJSON(clusters):
    ''' Returns the photo link for each cluster in JSON format
    '''
    out = {}
    for i in range(0,clusters.label.max()+1):
        cdates = clusters[clusters.label== i].sort_values(by='taken', ascending=False)
        cdates = cdates[['square_link', 'taken', 'username', 'photopage']]
        out[i] = json.loads(cdates.to_json(orient="records", force_ascii=False), "ISO-8859-1")

    return json.dumps(out, ensure_ascii=False)

def getClusterAutotags(clusters):
    ''' Returns the the autotags and frequencies for each cluster
            Input: pandas DataFrame
            Output: ctags - dictionary of tag lists per cluster
                    ccounts - dictionary of tag frequencies per cluster
    '''
    ctags = {}
    ccounts = {}

    for i in range(0,clusters.label.max()+1):
        ctags[i] = []
        for t in clusters.autotags[clusters.label == i]:
            if not t == None and not t == "None":
                t = re.split(", ", t)
                ctags[i].extend(t)
        ctags[i] = [tag for tag in ctags[i] if tag != "outdoor" and tag != "indoor"]
        ccounts[i] = Counter(ctags[i])

    return ctags, ccounts

def calcJaccardIndex(a, b):
    ''' Returns the Jaccard Similarity Index between two cluster's tags
    '''
    if len(set(a)) == 0 and len(set(b)) == 0:
        return 0
    else:
        shared = len(set(a).intersection(b))
        return shared / float(len(set(a)) + len(set(b)) - shared)

def calcClusterSimilarities(clustertags):
    ''' Returns a numpy matrix of Jaccard Similarities between clusters
    '''
    jacindex = np.zeros(shape=(len(clustertags),len(clustertags)))

    for a in clustertags:
        for b in clustertags:
                if not a == b:
                    ji = round(calcJaccardIndex(clustertags[a], clustertags[b]),2)
                    jacindex[a][b] = ji
                else:
                    jacindex[a][b] = "-1"
    return jacindex

def writeCenMarkersJS(clusters):
    ''' Creates the Google Maps JavaScript for the cluster center markers
    '''
    outscript = ""

    # Autotag frequencies for each cluster
    clustertags, clustercounts = getClusterAutotags(clusters)

    # Calculates the Jaccard similarity matrix for each cluster
    jacSims = calcClusterSimilarities(clustertags)

    # Calculate the mean latitude and longitude for each cluster
    #centers = clusters[clusters['core']!=False].groupby('label').mean()
    centers = clusters.groupby('label').mean()

    for i in range(0, len(centers.latitude)-1):
        cl = str(i+1)
        lat = round(centers.latitude[i],2)
        lon = round(centers.longitude[i],2)

        # Gets the string for the 5 most common tags for a cluster
        outtags = ""
        toptags = clustercounts[i].most_common(5)
        for t in toptags:
            outtags += "<b>%s</b>  %s<br>" % (t[0].capitalize(), t[1])

       # Gets the top 3 most similar clusters by Jaccard index
        outsim = ""
        simC = sorted(range(len(jacSims[i])), key=lambda z: jacSims[i][z], reverse=True)[:5]
        for s in simC:
            if s == i and len(simC) == 1:
                outsim += "None"
            if not s == i:
                outsim += """<a class='simscene' id='%s'>Scene %s</a> %s%%<br>""" % (s, str(s+1), int(jacSims[i][s]*100))

        # Gets the top photos for each cluster
        outimg = ""
        cdates = clusters[clusters.label== i].sort_values(by='taken', ascending=False)
        recents = cdates.square_link[0:3]
        cphotos = len(cdates.square_link)
        cusers = cdates.username.nunique()
        for r in recents:
            outimg += "<img src='%s' class='img'>" % r

         # Output JavaScript for each marker
        outscript += """
                        var Position = new google.maps.LatLng(%s, %s);
                        var marker_%s = new google.maps.Marker({
                            position: Position,
                            map: map,
                            icon: "static/icons/cen/number_%s.png"
                        });\n
                        markers.push(marker_%s);
                        markerBounds.extend(Position);
                    """ % (centers.latitude[i], centers.longitude[i], cl, cl, cl)

        # Add click handle for each marker
        outscript += """
                        marker_%s.addListener('click', function() {
                            document.getElementById("clusterid").innerHTML = "Scene %s";
                            document.getElementById("autotags").innerHTML = "%s";
                            primeCarousel(%s);
                            document.getElementById("similarto").innerHTML = "Similar";
                            document.getElementById("similars").innerHTML = "%s";
                        });
                    """ % (cl, cl, outtags, int(cl)-1, outsim)

        # Add infobox for each marker
        textboxhtml = "<span class='text-muted markerhead'>Scene %s</span><br><br>" % (cl)
        textboxhtml += "<span class='text-muted'><span class='markertext'>Latitude:</span> %s</span><br>" % (round(lat,2))
        textboxhtml += "<span class='text-muted'><span class='markertext'>Longitude:</span> %s</span><br>" % (round(lon,2))
        textboxhtml += "<span class='text-muted'><span class='markertext'># Photos:</span> %s</span><br>" % (cphotos)
        textboxhtml += "<span class='text-muted'><span class='markertext'># Users:</span> %s</span><br>" % (cusers)

        outscript += """
                        google.maps.event.addListener(marker_%s, 'click',
                        getInfoCallback(map, "%s"));
                        \n\n
                    """ % (cl, textboxhtml)

    return outscript

def writeIndMarkersJS(clusters):

    outscript = ""
    for i in range(0, len(clusters.label)):

        lat = clusters.latitude[i]
        lon = clusters.longitude[i]
        square = clusters.square_link[i]

        if clusters.label[i] == -1:
            cl = "Noise"
            png = 'X'
        else:
            cl = str(clusters.label[i]+1)
            png = "number_"+cl

        # Write individual markers
        outscript += """
                        var Position = new google.maps.LatLng(%s, %s);
                        var marker_i%s = new google.maps.Marker({
                            position: Position,
                            map: map,
                            icon: "static/icons/ind/%s.png" 
                        });
                        markerBounds.extend(Position);
                    """ % (lat, lon, i, png)

        textboxhtml = "<img src='%s'><br><br>" % square
        textboxhtml += "<span class='text-muted'><span class='markertext'>Cluster:</span> %s</span><br>" % cl
        textboxhtml += "<span class='text-muted'><span class='markertext'>Latitude:</span> %s</span><br>" % (round(lat,2))
        textboxhtml += "<span class='text-muted'><span class='markertext'>Longitude:</span> %s</span><br>" % (round(lon,2))
        textboxhtml += "<span class='text-muted'><span class='markertext'>Core Point:</span> %s</span><br>" % clusters.core[i]

        # Infobox for markers
        outscript += """
                        google.maps.event.addListener(marker_i%s, 'click', 
                        getInfoCallback(map, "%s"));\n\n
                    """ % (i, textboxhtml)

    return outscript

def getMarkers(clusters, show):
    ''' Get full list of markers based on show parameter
    '''

    markers = ""

    if show == "ind" or show == "all":
        markers += writeIndMarkersJS(clusters)

    if show == "cen" or show == "all":
        markers += writeCenMarkersJS(clusters)

    return markers

def printGooglePoly(boundary):
    ''' Returns JSON formatted coordinates for parkname
    '''
    js = ''
    geom = json.loads(boundary)['coordinates']
    
    for i in range(0, len(geom)):
        try:
            coords = [{'lat':c[1], 'lng':c[0]} for coord in geom[i] for c in coord]
        except:
            coords = [{'lat':c[1], 'lng':c[0]} for c in geom[i]]

        js += """
                var parkarea_%s = %s;
                var parkpath_%s = new google.maps.Polyline({
                     path: parkarea_%s,
                     geodesic: true,
                     strokeColor: '#FF6600',
                     strokeOpacity: 1.0,
                     strokeWeight: 1
                 });
                parkpath_%s.setMap(map);
            """ % (i, json.dumps(coords), i, i, i)

    return js

@app.route('/')
def park_input(the_result=""):
    return render_template("input.html", the_result="")

@app.route('/explore', methods=['GET', 'POST'])
def park_output():

    # Get GET variables
    parkname = request.args.get('parkname')
    eps = request.args.get('eps')
    min_samples = request.args.get('min_samples')
    show = request.args.get('show')

    # Check to see if parkname is in database
    if not isParkInDB(parkname):
        return render_template("input.html", the_result="Please enter a valid parkname.")

    lat, lon, boundary = getParkInfo(parkname)
    photos = getParkPhotos(parkname)

    if len(photos) > 0:
        clusters, noclusters = clusterPhotos(photos, eps, min_samples)

        # Return photo carousel JSON
        carousel = getClusterPhotosJSON(clusters)

        # Get appropriate markers
        markers = getMarkers(clusters, show)
    else:
        clusters, noclusters = 0, 0
        markers = []
        carousel = []

    photomsg = 'Click a scene marker to explore.'
    if noclusters == 0:
        photomsg = 'There are no scenes to explore for this park.'

    # Return park boundaries JavaScript
    boundary = printGooglePoly(boundary)

    return render_template("output.html",
                            parkname=parkname,
                            nophotos=len(photos),
                            lat=lat,
                            lon=lon,
                            noclusters=noclusters,
                            markers=Markup(markers),
                            carousel=Markup(carousel),
                            boundary=Markup(boundary),
                            photomsg=photomsg
                            )

@app.route('/autocomplete', methods=['GET'])
def autocomplete():

    keyword = request.args.get('keyword')
    con = mdb.connect(user=sec.mysqluser, host=sec.mysqlhost, passwd=sec.mysqlpwd, db="parkpic", charset='utf8')
    results = {}
    with con.cursor() as cur:
        sql = """SELECT `parkname` FROM `parks` WHERE `parkname`
                 LIKE \"%s%%\" AND `type`='National'
                 ORDER BY `parkname`;
                 """ % keyword
        cur.execute(sql)
        rows = cur.fetchall()
        i = 0
        for r in rows:
            results[i] = r[0]
            i += 1

    return jsonify(data=results)

@app.route('/about')
def park_about():
    return render_template("about.html")

@app.route('/contact')
def park_contact():
    return render_template("contact.html")

@app.route('/resume')
def park_resume():
    return send_file('static/media/MPScherrer-Resume.pdf', 'MPScherrer-Resume.pdf')
