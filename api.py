import json

from flask import Flask, make_response, request, jsonify
import config
from store import r
import annotation
import stats

app = Flask(__name__)


def iter_tmp(bottom_left, top_right):
    def position_in_area(p):
        return p[0] >= bottom_left[0] and p[1] >= bottom_left[1] and p[0] <= top_right[0] and p[1] <= top_right[1]

    tmp_set = r.smembers('f:tmp')
    return [tmp for tmp in tmp_set if position_in_area(annotation.get_lamppost_position(tmp))]


@app.route('/tmp')
def get_tmp():
    lat1 = request.args.get('lat1')
    long1 = request.args.get('long1')
    lat2 = request.args.get('lat2')
    long2 = request.args.get('long2')
    if lat1 is None or lat2 is None or long1 is None or long2 is None:
        raise Exception("Wrong parameters")
    found_tmp = iter_tmp((float(lat1), float(long1)), (float(lat2), float(long2)))
    all_tmp = []
    for tmp in found_tmp:
        position = annotation.get_lamppost_position(tmp)
        if position is not None:
            all_tmp.append({'id': tmp, 'latitude': position[0], 'longitude': position[1]})
    return jsonify(lampposts=all_tmp)


@app.route('/objects')
def get_objects():
    return jsonify(lampposts=list(r.smembers('f')))


def extract_annotation(ann):
    x, ts = ann
    return dict({'timestamp': ts}, **x)


@app.route('/objects/<fid>')
def get_object(fid):
    if fid in r.smembers('f'):
        object_dict = {'id': fid, 'attributes': {}}
        for attr in annotation.get_lamppost_attributes(fid):
            object_dict['attributes'][attr] = stats.get_agreement_status(fid, attr)

        o_uri = annotation.get_lampost_uri(fid)
        if o_uri is not None:
            object_dict['uri'] = o_uri

        position = annotation.get_lamppost_position(fid)
        if position is not None:
            object_dict.update({'latitude': position[0], 'longitude': position[1]})

        return jsonify(object_dict)

    return make_response('object not found', 404)


@app.route('/objects/<fid>/<attr>')
def get_attribute(fid, attr):
    if fid in r.smembers('f'):
        attrs = annotation.get_lamppost_attributes(fid)
        if attr in attrs:

            object_dict = {'id': fid, 'attribute': attr, 'annotations': []}

            o_uri = annotation.get_lampost_uri(fid)
            if o_uri is not None:
                object_dict['uri'] = o_uri

            position = annotation.get_lamppost_position(fid)
            if position is not None:
                object_dict.update({'latitude': position[0], 'longitude': position[1]})

            anns = [extract_annotation(ann) for ann in annotation.get_attribute_annotations(fid, attr)]
            for ann in anns:
                object_dict['annotations'].append({'value': ann['value'], 'timestamp': ann['timestamp']})

            return jsonify(object_dict)

    return make_response('object not found', 404)


def start():
    app.run(host='0.0.0.0', port=config.API_PORT, debug=False, use_reloader=False)
