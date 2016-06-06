from scipy import stats
import numpy as np
import annotation
import calendar
from datetime import datetime as dt, timedelta as delta
from store import r


def values_to_int(l):
    v_dict = {}
    count = 0
    for elm in l:
        if elm not in v_dict:
            v_dict[elm] = count
            count += 1
        yield v_dict[elm]


def check_agreement(fid):
    time_threshold = calendar.timegm((dt.utcnow() - delta(hours=1)).timetuple())
    anns = annotation.get_lamppost_annotations(fid, begin=time_threshold)

    known_attrs = annotation.get_lamppost_attributes(fid)
    for attr in known_attrs:
        orig_value = r.hget('f:orig:{}'.format(fid), attr)
        print 'checking attribute {} of {}...'.format(attr, fid)
        attr_annotations = map(lambda (auuid, ts): annotation.parse_annotation(auuid), anns)
        attr_annotations = filter(lambda x: x['attribute'] == attr, attr_annotations)
        if len(attr_annotations) >= 3:
            attr_values = map(lambda x: x['value'], attr_annotations)
            if orig_value is not None:
                print 'considering original value for attribute {} of lamppost {}: {}'.format(attr, fid, orig_value)
                attr_values = attr_values + [orig_value] * 10
            f_uri = attr_annotations[0].get('uri', None)
            value_array = np.array(attr_values)
            numeric = False
            numeric_array = None
            if attr == 'heading' or attr == 'pitch':
                numeric_array = np.array(list(map(lambda x: float(x), attr_values)))
                std = stats.tstd(numeric_array)
                numeric = True
            else:
                std = stats.tstd(np.array(list(values_to_int(attr_values))))
            if numeric and std < 0.5:
                mean = stats.trim_mean(numeric_array, 0.1)
                print 'got an agreement on numeric attribute {} of lamppost {}: {}'.format(attr, fid, mean)
                yield {'attribute': attr, 'value': str(mean), 'uri': f_uri}
            elif not numeric and std < 1.0:
                if len(stats.mode(value_array).mode) == 1:
                    mode = stats.mode(value_array).mode[0]
                    print 'got an agreement on discrete attribute {} of lamppost {}: {}'.format(attr, fid, mode)
                    yield {'attribute': attr, 'value': mode, 'uri': f_uri}
            else:
                print 'no agreement for {} attribute in lamppost {}: {}'.format(attr, fid, std)
        else:
            print 'not enough annotations for attribute {} of lamppost {}'.format(attr, fid)

