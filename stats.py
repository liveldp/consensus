from scipy import stats
import numpy as np
import annotation
import calendar
from datetime import datetime as dt, timedelta as delta
from store import r

lmh_map = {
    'low': 0,
    'medium': 1,
    'high': 2
}


def values_to_int(l, mapping=lmh_map):
    v_dict = {}
    count = 0

    for elm in l:
        try:
            yield int(elm)
        except Exception:
            if elm not in v_dict:
                if mapping is not None and elm in mapping:
                    v_dict[elm] = mapping[elm]
                else:
                    v_dict[elm] = count
                count += 1
            yield v_dict[elm]


def check_agreement(fid):
    time_threshold = calendar.timegm((dt.utcnow() - delta(days=7)).timetuple())
    anns = annotation.get_lamppost_annotations(fid, begin=time_threshold)

    known_attrs = annotation.get_lamppost_attributes(fid)
    for attr in known_attrs:
        orig_value = r.hget('f:orig:{}'.format(fid), attr)
        attr_annotations = map(lambda (auuid, ts): annotation.parse_annotation(auuid), anns)
        attr_annotations = filter(lambda x: x['attribute'] == attr, attr_annotations)
        n_attr_annotations = len(attr_annotations)
        if n_attr_annotations > 0:
            # print "   - '{}' [total={}]".format(attr, n_attr_annotations),
            if n_attr_annotations >= 2:
                attr_values = map(lambda x: x['value'], attr_annotations)
                if orig_value is not None:
                    # print "[original value={}]:".format(orig_value),
                    attr_values = attr_values + [orig_value] * 10
                # else:
                #     print ":",
                f_uri = attr_annotations[0].get('uri', None)
                value_array = np.array(attr_values)
                numeric = False
                if attr == 'heading' or attr == 'pitch':
                    numeric_array = np.array(list(map(lambda x: float(x), attr_values)))
                    std = stats.tstd(numeric_array)
                    mean = stats.trim_mean(numeric_array, 0.1)
                    numeric = True
                else:
                    int_classes = list(values_to_int(attr_values))
                    std = stats.tstd(np.array(int_classes))
                    mean = stats.trim_mean(int_classes, 0.0)
                convergence = std / abs(mean) if mean != 0 else std
                r.hset('f:cons:{}:{}'.format(fid, attr), 'dispersion', convergence)
                if numeric and convergence < 0.1:
                    # print "AGREEMENT on '{}', values={}".format(mean, numeric_array)
                    with r.pipeline(transaction=True) as p:
                        p.hset('f:cons:{}:{}'.format(fid, attr), 'value', mean)
                        p.execute()
                    yield {'attribute': attr, 'value': str(mean), 'uri': f_uri}
                elif not numeric and convergence < 0.2:
                    if len(stats.mode(value_array).mode) == 1:
                        mode = stats.mode(value_array).mode[0]
                        # print "AGREEMENT on '{}', values={}".format(mode, attr_values)
                        with r.pipeline(transaction=True) as p:
                            p.hset('f:cons:{}:{}'.format(fid, attr), 'value', mean)
                            p.execute()
                        yield {'attribute': attr, 'value': mode, 'uri': f_uri}
                else:
                    r.hdel('f:cons:{}:{}'.format(fid, attr), 'value')
                    # print "DISPERSION factor of {}%, values={}".format(
                    #     convergence * 100, attr_values)
            # else:
            #     print "NOT ENOUGH annotations"


def get_agreement_status(fid, attr):
    return r.hgetall('f:cons:{}:{}'.format(fid, attr))
