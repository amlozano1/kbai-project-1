__author__ = 'anthony'

from collections import namedtuple

Verb = namedtuple('Verb', ['method', 'cost'])

def mirror_angle(raven_obj):
    """
    Takes a string representing some angle in degrees and rotates it 180 degress
    :param raven_obj: some figure with and angle representing degrees
    :return: a flipped figure
    """
    if 'angle' in raven_obj.attributes:
        angle = raven_obj.attributes['angle']
        raven_obj.attributes['angle'] = str(((int(angle) + 180) % 360) + 360 % 360)
    else:
        raven_obj.attributes['angle'] = '180'
    return raven_obj

def unchanged(raven_obj):
    """
    This method, It does nothing!
    :param raven_obj: a figure
    :return: the figure passed in the argument
    """
    return raven_obj

# This dictionary contains possible transitions. key: tuple => name: (function, current_cost)
VERBS = {'unchanged': Verb(unchanged, 0),
         'mirror':  Verb(mirror_angle, 1),
        }


