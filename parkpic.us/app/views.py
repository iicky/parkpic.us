from flask import Flask, jsonify, make_response, Markup
from flask import redirect, render_template, request, send_file
from app import app
import pandas as pd
import pymongo
import secrets as sec

import parkpic as pp


@app.route('/')
def park_input():
    return render_template("input.html", message="")


@app.route('/explore', methods=['GET', 'POST'])
def park_output():

    # Get GET variables
    parkname = request.args.get('parkname')
    eps = request.args.get('eps')
    min_samples = request.args.get('min_samples')
    show = request.args.get('show')

    # Check to see if parkname is in database
    if not pp.parks.in_db(parkname):
        message = "Please enter a valid parkname."
        return render_template("input.html",
                               message=message)
    # Park info
    parkcode = pp.parks.parkname_to_code(parkname)
    park = pp.Park(parkcode)
    photo_count = park.photo_count

    # Clusters
    if photo_count > 0:
        clusters = pp.Clusters(parkcode, eps, min_samples)
        cluster_count = clusters.cluster_count
    else:
        clusters, cluster_count = 0, 0

    photomsg = 'Click a scene marker to explore.'
    if cluster_count == 0:
        photomsg = 'There are no scenes to explore for this park.'

    return render_template("output.html",
                           parkname=parkname,
                           parkcode=parkcode,
                           nophotos=photo_count,
                           lat=park.latitude,
                           lon=park.longitude,
                           noclusters=cluster_count,
                           show=show,
                           photomsg=photomsg
                           )


@app.route('/autocomplete', methods=['GET'])
def autocomplete():

    keyword = request.args.get('keyword')
    results = {}
    parks = list(pp.db.parks.find(
                    {'parkname': {'$regex': '^'+keyword,
                                  '$options': '-i'}},
                    {'parkname': 1, '_id': 0}
                ).sort('parkname', pymongo.ASCENDING))
    i = 0
    for p in parks:
        results[i] = p['parkname']
        i += 1
    return jsonify(data=results)


@app.route('/boundary', methods=['GET'])
def boundary():
    ''' Returns park boundary JSON
    '''
    parkcode = request.args.get('parkcode')
    park = pp.Park(parkcode)

    return jsonify(boundaries=park.map_boundary())


@app.route('/individual', methods=['GET'])
def individual_markers():
    ''' Returns individual markers JSON
    '''
    parkcode = request.args.get('parkcode')
    clusters = pp.Clusters(parkcode)

    return jsonify(indmarkers=clusters.ind_markers())


@app.route('/center', methods=['GET'])
def center_markers():
    ''' Returns center markers JSON
    '''
    parkcode = request.args.get('parkcode')
    clusters = pp.Clusters(parkcode)

    return jsonify(cenmarkers=clusters.cen_markers())


@app.route('/carousel', methods=['GET'])
def carousel():
    ''' Returns photo carousel JSON
    '''
    parkcode = request.args.get('parkcode')
    clusters = pp.Clusters(parkcode)

    return jsonify(carousel=clusters.carousel())


@app.route('/about')
def park_about():
    ''' About page
    '''
    return render_template("about.html")


@app.route('/contact')
def park_contact():
    ''' Contact page
    '''
    return render_template("contact.html")


@app.route('/resume')
def park_resume():
    ''' Resume page
    '''
    return send_file('static/media/MPScherrer-Resume.pdf',
                     'MPScherrer-Resume.pdf')


@app.route('/igexplore', methods=['GET', 'POST'])
def igpark_output():

    # Get GET variables
    parkname = request.args.get('parkname')
    eps = request.args.get('eps')
    eps = eps if eps is not None else 0.01
    min_samples = request.args.get('min_samples')
    min_samples = min_samples if min_samples is not None else 10
    show = request.args.get('show')

    # Park info
    parkcode = pp.parks.parkname_to_code(parkname)
    park = pp.Park(parkcode)
    photo_count = park.igphoto_count

    clusters = pp.IGClusters(parkcode, eps, min_samples)
    cluster_count = clusters.cluster_count

    photomsg = 'Click a scene marker to explore.'

    return render_template("igoutput.html",
                           parkname=parkname,
                           eps=eps,
                           min_samples=min_samples,
                           parkcode=parkcode,
                           nophotos=photo_count,
                           lat=park.latitude,
                           lon=park.longitude,
                           noclusters=cluster_count,
                           show=show,
                           photomsg=photomsg
                           )


@app.route('/igindividual', methods=['GET'])
def igindividual_markers():
    ''' Returns individual markers JSON
    '''
    parkcode = request.args.get('parkcode')
    eps = request.args.get('eps')
    eps = eps if eps is not None else 0.01
    min_samples = request.args.get('min_samples')
    min_samples = min_samples if min_samples is not None else 10

    clusters = pp.IGClusters(parkcode, eps, min_samples)
    return jsonify(indmarkers=clusters.ind_markers())


@app.route('/igcenter', methods=['GET'])
def igcenter_markers():
    ''' Returns center markers JSON
    '''
    parkcode = request.args.get('parkcode')
    eps = request.args.get('eps')
    eps = eps if eps is not None else 0.01
    min_samples = request.args.get('min_samples')
    min_samples = min_samples if min_samples is not None else 10

    clusters = pp.IGClusters(parkcode, eps, min_samples)
    return jsonify(cenmarkers=clusters.cen_markers())
