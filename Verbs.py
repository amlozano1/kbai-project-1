__author__ = 'anthony'
"""
Master list of atomic transitions that can be applied to shapes in RPM figures.
"""
from collections import namedtuple
from PIL.ImageChops import *
from copy import deepcopy
from ObjFrame import Angle, Shape, Alignment, Fill, Size
from helpers import normalize_degrees

Verb = namedtuple('Verb', ['method', 'cost'])

# This list contains possible transitions. (function, current_cost)
VERBS = []
binary_verbs = []

def unchanged(first, second):
    """
    This method, It does nothing!
    :param image
    :return: the frame passed in the argument
    """
    return first.copy()

VERBS.extend([Verb(unchanged, 0),
              ])


# begin binary verbs

def logical_xor_inverted(first, second):
    """
    This behaves like a logical xor, except treating black as "True" and white as "False"
    :param first:
    :param second:
    :return:
    """
    return invert(logical_xor(first, second))

binary_verbs.extend([Verb(logical_or, 1),
                     Verb(logical_and, 1),
                     Verb(logical_xor, 1),
                     Verb(logical_xor_inverted, 1),
                     Verb(difference, 1),
                     Verb(multiply, 1)
                     ])
