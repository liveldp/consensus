import json
from uuid import uuid4
from datetime import datetime
from store import r
import calendar
from query import query


def annotation_callback(method, properties, body):
    try:
        annotation = json.loads(body)
    except Exception as e:
        raise ValueError(e.message)

    print 'Received raw annotation: ' + str(annotation)
    store_annotation(annotation)


def parse_annotation(auuid):
    return r.hgetall('annotations:{}'.format(auuid))


def store_annotation(ann_dict):
    ts = calendar.timegm(datetime.utcnow().timetuple())
    auuid = uuid4()
    fid = ann_dict['id']
    attr = ann_dict['attribute']
    with r.pipeline(transaction=True) as p:
        if fid.startswith('tmp'):
            p.sadd('f:tmp', fid)
        p.sadd('f', fid)
        p.hmset('annotations:{}'.format(auuid), ann_dict)
        # p.zadd('annotations', ts, auuid)
        p.zadd('f:annotations:{}'.format(fid), ts, auuid)
        p.sadd('f:attrs:{}'.format(fid), attr)
        orig_value = r.hget('f:orig:{}'.format(fid), attr)
        f_uri = ann_dict.get('uri', None)
        if f_uri is not None:
            p.set('f:uri:{}'.format(fid), f_uri)
            if orig_value is None:
                query_value = query(f_uri, attr)
                if query_value is not None:
                    p.hset('f:orig:{}'.format(fid), attr, str(query_value))

        f_lat = ann_dict.get('latitude', None)
        f_long = ann_dict.get('longitude', None)
        if f_lat is not None and f_long is not None:
            p.set('f:pos:{}'.format(fid), (f_lat, f_long))

        p.execute()


def get_lampposts():
    return r.smembers('f')


def get_lamppost_attributes(fid):
    return r.smembers('f:attrs:{}'.format(fid))


# def get_annotations(max=100, offset=0, begin=None, end=None):
#     begin = '-inf' if begin is None else begin
#     end = '+inf' if end is None else end
#
#     ann_uuids = r.zrangebyscore('annotations', begin, end, withscores=True, num=max,
#                                 start=offset)
#
#     return ann_uuids


def get_lamppost_annotations(fid, max=100, offset=0, begin=None, end=None):
    begin = '-inf' if begin is None else begin
    end = '+inf' if end is None else end

    ann_uuids = r.zrangebyscore('f:annotations:{}'.format(fid), begin, end, withscores=True, num=max,
                                start=offset)

    return ann_uuids


def get_attribute_annotations(fid, attr):
    f_annotations = map(lambda (auuid, ts): (parse_annotation(auuid), ts), get_lamppost_annotations(fid))
    attr_annotations = filter(lambda (x, ts): x['attribute'] == attr, f_annotations)
    return attr_annotations


def get_lamppost_position(fid):
    pos = r.get('f:pos:{}'.format(fid))
    if pos is not None:
        pos = eval(pos)

    return pos


def get_lampost_uri(fid):
    return r.get('f:uri:{}'.format(fid))


def delete_temporal(fid):
    fid_keys = r.keys('*{}*'.format(fid))
    with r.pipeline(transaction=True) as p:
        p.srem('f:tmp', fid)
        p.srem('f', fid)
        for fk in fid_keys:
            p.delete(fk)
        p.execute()
