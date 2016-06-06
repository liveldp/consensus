import json

from flask import Flask, make_response, request, jsonify
import config
from store import r
import annotation

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


def start():
    app.run(host='0.0.0.0', port=config.API_PORT, debug=False, use_reloader=False)
