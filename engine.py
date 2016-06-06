import consume
import annotation
from threading import Thread
from time import sleep
from datetime import datetime as dt, timedelta as delta
import calendar
import stats
from publish import publish
from store import r
import config

# def consensus_test_callback(method, properties, body):
#     print method
#     print properties
#     print body

consume.start_channel(config.RABBIT_EXCHANGE, 'annotations.raw', 'consensus_input', annotation.annotation_callback)


# consume.start_channel('farolapp', 'annotations.consensus', 'consensus_test', consensus_test_callback)


def get_current_aggreement(fid, attr):
    return r.hget('f:aggr:{}'.format(fid), attr)


def set_current_aggreement(fid, attr, value):
    return r.hset('f:aggr:{}'.format(fid), attr, value)


def calculate_pollution(color, wattage, covered):
    if covered == 'false':
        return 'high'
    if color == 'blue':
        return 'high'
    elif color == 'yellow':
        if float(wattage) >= 100.0:
            return 'medium'
        return 'low'
    elif color == 'white':
        if float(wattage) >= 100.0:
            return 'high'
        return 'medium'

    return 'medium'


def check_annotations():
    while True:
        known_lampposts = annotation.get_lampposts()
        print 'monitoring {} lampposts.'.format(len(known_lampposts))
        for fid in known_lampposts:
            print "checking '{}'...".format(fid)
            f_uri = r.get('f:uri:{}'.format(fid))
            agreements = stats.check_agreement(fid)
            agreed_color = None
            agreed_wattage = None
            agreed_cover = None
            position = annotation.get_lamppost_position(fid)
            position_dict = {}
            if position is not None:
                position_dict['latitude'] = position[0]
                position['longitude'] = position[1]
            for agreement in agreements:
                agreement['id'] = fid
                attribute = agreement['attribute']
                if attribute == 'color':
                    agreed_color = agreement['value']
                if attribute == 'wattage':
                    agreed_wattage = agreement['value']
                if attribute == 'covered':
                    agreed_cover = agreement['value']
                value = get_current_aggreement(fid, attribute)
                if value != agreement['value']:
                    if f_uri is not None:
                        agreement['uri'] = f_uri
                    publish(agreement.update(position_dict))
                    set_current_aggreement(fid, attribute, agreement['value'])
                    annotation.delete_temporal(fid)
            try:
                if agreed_color and agreed_cover and agreed_wattage:
                    pollution = calculate_pollution(agreed_color, agreed_wattage, agreed_cover)
                    current_pollution = get_current_aggreement(fid, 'pollution')
                    if current_pollution is None or current_pollution != pollution:
                        set_current_aggreement(fid, 'pollution', pollution)
                        data = {'id': fid, 'attribute': 'pollution', 'value': str(pollution)}
                        if f_uri is not None:
                            data['uri'] = f_uri
                        publish(data.update(position_dict))
            except Exception as e:
                print e.message

        sleep(3)


monitor = Thread(target=check_annotations)
monitor.daemon = True
monitor.start()

monitor.join()
