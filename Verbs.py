__author__ = 'anthony'

from collections import namedtuple
from copy import deepcopy
from ObjFrame import Angle
Verb = namedtuple('Verb', ['method', 'cost'])

def mirror_angle(frame):
    """
    """
    mirror = deepcopy(frame)
    mirror.angle = Angle(frame.angle.value - 4 if 3 < frame.angle.value < 8 else frame.angle.value + 4)


def unchanged(raven_obj):
    """
    This method, It does nothing!
    :param frame
    :return: the frame passed in the argument
    """
    return raven_obj

# This dictionary contains possible transitions. key: tuple => name: (function, current_cost)
VERBS = [Verb(unchanged, 0),
         Verb(mirror_angle, 1),
        ]


