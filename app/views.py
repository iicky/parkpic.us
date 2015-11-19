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

class Geo:
    ''' Park geometry handling
    '''
    def __init__(self):
        self.parkshapes = fiona.open('app/static/nps_boundary/nps_boundary.shp', 'r')

    def getParkGeometry(self, parkcode):
        ''' Returns the geometry for a park
        '''
        with self.parkshapes as p:
            for feat in p:
                if feat['properties']['UNIT_CODE'] == parkcode:
                    return feat['geometry']

        return "None"

    def isPointInPark(self, parkcode, lon, lat):
        ''' Returns whether a point is within a park area
        '''
        geom = self.getParkGeometry(parkcode)
        shape = shapely.geometry.asShape(geom)
        point = shapely.geometry.Point(lon,lat)
        return shape.contains(point)

    def printGooglePolySolo(self, parkcode):
        ''' Returns JSON formatted coordinates for parkname
        '''
        coords = []

        geom = self.getParkGeometry(parkcode)['coordinates']
        for g in geom[0]:
            coords.append({'lat': g[1], 'lng': g[0]})
        return json.dumps(coords)

    def printGooglePoly(self, parkcode):
        ''' Returns JSON formatted coordinates for parkname
        '''
        js = ''
        geom = self.getParkGeometry(parkcode)['coordinates']

        try:
            for g in geom:
                coords = []
                for c in g[0]:
                    coords.append({'lat': c[1], 'lng': c[0]})
                js += "var parkarea = %s;\n" % str(json.dumps(coords))
                js += """var parkpath = new google.maps.Polyline({
                        path: parkarea,
                        geodesic: true,
                        strokeColor: '#FF6600',
                        strokeOpacity: 1.0,
                        strokeWeight: 1
                        });
                        parkpath.setMap(map);\n
                    """
            return js
        except:
            coords = []
            for g in geom[0]:
                coords.append({'lat': g[1], 'lng': g[0]})
            js += "var parkarea = %s;\n" % str(json.dumps(coords))
            js += """var parkpath = new google.maps.Polyline({
                    path: parkarea,
                    geodesic: true,
                    strokeColor: '#FF6600',
                    strokeOpacity: 1.0,
                    strokeWeight: 1
                    });
                    parkpath.setMap(map);\n
                """
            return js

class Photo:
    ''' Photo class
    '''
    def __init__(self, id):

        con = mdb.connect(user=sec.mysqluser, host=sec.mysqlhost, passwd=sec.mysqlpwd, db="parkpic", charset='utf8')
        try:
            with con.cursor() as cur:
                sql = """SELECT `latitude`, `longitude`, `square_link`, `tags`, `autotags`, `photopage`, `taken`
                        FROM `photos` WHERE id=\"%s\";""" % id
                cur.execute(sql)
                rows = cur.fetchone()
        finally:
            con.close()

        self.id = id
        self.lat = rows[0]
        self.lon = rows[1]
        self.square_link = rows[2]
        self.tags = rows[3]
        self.autotags = rows[4]
        self.photopage = rows[5]
        self.taken = rows[6]

def getParkPhotos(parkname):
    ''' Returns photos from a park
    '''
    photos = []

    con = mdb.connect(user=sec.mysqluser, host=sec.mysqlhost, passwd=sec.mysqlpwd, db="parkpic", charset='utf8')
    try:
        with con.cursor() as cur:
            sql = """SELECT `id` FROM `photos` WHERE `parkname`="%s" AND `in_park`="True";""" % parkname
            cur.execute(sql)
            rows = cur.fetchall()
            for r in rows:
                photos.append(Photo(r[0]))
    finally:
        con.close()

    return photos

def isParkInDB(parkname):
    ''' Returns true if parkname in Database
    '''
    con = mdb.connect(user=sec.mysqluser, host=sec.mysqlhost, passwd=sec.mysqlpwd, db="parkpic", charset='utf8')

    with con:
        cur = con.cursor()
        sql = "SELECT `parkname` FROM `parks` WHERE parkname=\"%s\";" % parkname
        cur.execute(sql)
        row = cur.fetchone()
        if row == None:
            return False
        return True

def getParkInfo(parkname):
    ''' Returns information about the park from Database
    '''
    con = mdb.connect(user=sec.mysqluser, host=sec.mysqlhost, passwd=sec.mysqlpwd, db="parkpic", charset='utf8')

    with con:
        cur = con.cursor()
        sql = "SELECT `latitude`, `longitude`, `parkcode` FROM `parks` WHERE parkname=\"%s\";" % parkname
        cur.execute(sql)
        row = cur.fetchone()
        lat = row[0]
        lon = row[1]
        parkcode = row[2]

    return lat, lon, parkcode

def clusterPhotos(photos, eps=0.01, min_samples=10):

    ids = []
    lats = []
    lons = []
    squares = []
    tags = []
    autotags = []
    pages = []
    takens = []

    for p in photos:
        ids.append(p.id)
        lats.append(float(p.lat))
        lons.append(float(p.lon))
        squares.append(p.square_link),
        tags.append(p.tags),
        autotags.append(p.autotags),
        pages.append(p.photopage)
        takens.append(p.taken)


    df = pd.DataFrame({'id':ids,
                       'lat':lats,
                       'lon':lons,
                       'square':squares,
                       'tags':tags,
                       'autotags':autotags,
                       'pages':pages,
                       'taken':takens
                      })

    locations = df.as_matrix(columns=('lon', 'lat'))

    db = DBSCAN(eps=float(eps), min_samples=int(min_samples)).fit(locations)
    labels = db.labels_
    df['label'] = labels

    return df, labels.max()+1

def getClusterPhotos(clusters):

    out = {}

    for i in range(0,clusters.label.max()+1):
        cdates = clusters[clusters.label== i].sort(['taken'], ascending=False)
        square = cdates.square
        out[i] = []
        for s in square:
            out[i].append(s)

    return json.dumps(out)

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
    centers = clusters.groupby('label').mean()
    for i in range(0, len(centers.lat)-1):
        cl = str(i+1)
        lat = centers.lat[i]
        lon = centers.lon[i]

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
        cdates = clusters[clusters.label== i].sort(['taken'], ascending=False)
        recents = cdates.square[0:3]
        cphotos = len(cdates.square)
        for r in recents:
            outimg += "<img src='%s' class='img'>" % r


        # Output JavaScript for each marker
        outscript += """
                        var marker_%s = new google.maps.Marker({
                            position: new google.maps.LatLng(%s, %s),
                            map: map,
                            icon: "static/icons/cen/number_%s.png"
                        });\n
                        markers.push(marker_%s);
                    """ % (cl, lat, lon, cl, cl)

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
        outscript += """
                        google.maps.event.addListener(marker_%s, 'click',
                        getInfoCallback(map, "%s"));
                        \n\n
                    """ % (cl, textboxhtml)

    return outscript

def writeIndMarkersJS(clusters):

    outscript = ""

    for i in range(0, len(clusters.label)):

        lat = clusters.lat[i]
        lon = clusters.lon[i]
        square = clusters.square[i]
        tags = clusters.tags[i]

        if clusters.label[i] == -1:
            cl = "Noise"
            png = 'X'
        else:
            cl = str(clusters.label[i]+1)
            png = "number_"+cl

        outscript += """var marker_i%s = new google.maps.Marker({
                        position: new google.maps.LatLng(%s, %s),
                        map: map,
                        icon: "static/icons/ind/%s.png"
                        });
                        google.maps.event.addListener(marker_i%s, 'click',
                        getInfoCallback(map, "<b>Cluster %s</b><br><img src='%s'><br>Tags:<br>%s"));\n\n
                    """ % (i, lat, lon, png, i, cl, square, tags)

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

    lat, lon, parkcode = getParkInfo(parkname)
    photos = getParkPhotos(parkname)

    if len(photos) > 0:
        clusters, noclusters = clusterPhotos(photos, eps, min_samples)

        # Return photo carousel JSON
        carousel = getClusterPhotos(clusters)

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
    boundary = Geo().printGooglePoly(parkcode)

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

@app.route('/autocomplete',methods=['GET'])
def autocomplete():

    keyword = request.args.get('keyword')
    con = mdb.connect(user=sec.mysqluser, host=sec.mysqlhost, passwd=sec.mysqlpwd, db="parkpic", charset='utf8')
    results = {}
    with con.cursor() as cur:
        sql = """SELECT `parkname` FROM `parks` WHERE `parkname`
                 LIKE \"%s%%\" AND `type`='National'
                 AND parkcode NOT IN ('DENA','GAAR','GLBA','KATM','LACL','WRST')
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

@app.route('/image')
def imagetest():

    # Get GET variables
    parkname = request.args.get('parkname')
    eps = request.args.get('eps')
    min_samples = request.args.get('min_samples')

    photos = getParkPhotos(parkname)
    clusters, noclusters = clusterPhotos(photos, eps, min_samples)
    carousel = getClusterPhotos(clusters)


    return render_template("imagetest.html", carousel=Markup(carousel))

@app.route('/map')
def maptest():
    return render_template("maptest.html")