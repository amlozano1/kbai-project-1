__author__ = 'anthony'

from collections import namedtuple
from copy import deepcopy
from ObjFrame import Angle, Shape, Alignment, Fill
from helpers import normalize_degrees

Verb = namedtuple('Verb', ['method', 'cost'])

# This list contains possible transitions. (function, current_cost)
VERBS = []

def rotate_90_left(frame):
    """
    """
    rotated = deepcopy(frame)
    rotated.angle = Angle(normalize_degrees(frame.angle.value - 90))
    return rotated

def rotate_90_right(frame):
    """
    """
    rotated = deepcopy(frame)
    rotated.angle = Angle(normalize_degrees(frame.angle.value + 90))
    return rotated

def mirror_up_down(frame):
    rotated = deepcopy(frame)
    angle = rotated.angle.value
    angle = normalize_degrees(0 - angle)
    rotated.angle = Angle(angle)
    if rotated.alignment is not Alignment.center:
        if rotated.alignment is Alignment.bottom_left:
            rotated.alignment = Alignment.top_left
        elif rotated.alignment is Alignment.bottom_right:
            rotated.alignment = Alignment.top_right
        elif rotated.alignment is Alignment.top_right:
            rotated.alignment = Alignment.bottom_right
        elif rotated.alignment is Alignment.top_left:
            rotated.alignment = Alignment.bottom_left
        else:
            raise ValueError('Unexpected Alignment')
    return rotated

def mirror_left_right(frame):
    """
    """
    rotated = deepcopy(frame)
    angle = rotated.angle.value
    angle = normalize_degrees(90 + normalize_degrees(90 - angle))
    rotated.angle = Angle(angle)
    if rotated.alignment is not Alignment.center:
        if rotated.alignment is Alignment.bottom_left:
            rotated.alignment = Alignment.bottom_right
        elif rotated.alignment is Alignment.bottom_right:
            rotated.alignment = Alignment.bottom_left
        elif rotated.alignment is Alignment.top_right:
            rotated.alignment = Alignment.top_left
        elif rotated.alignment is Alignment.top_left:
            rotated.alignment = Alignment.top_right
        else:
            raise ValueError('Unexpected Alignment')
    return rotated

def fill_shape_factory(fill):
    def to_fill(frame):
        frame = deepcopy(frame)
        frame.fill = fill
        return frame
    return to_fill

for fill in Fill:
    to_fill = fill_shape_factory(fill)
    VERBS.append(Verb(to_fill,1))

def to_new_shape_factory(shape):
        def to_new_shape(frame):
            frame = deepcopy(frame)
            frame.shape = shape
            return frame
        return to_new_shape

for shape in Shape:
    to_new_shape = to_new_shape_factory(shape)
    VERBS.append(Verb(to_new_shape, 5))

def unchanged(frame):
    """
    This method, It does nothing!
    :param frame
    :return: the frame passed in the argument
    """
    return deepcopy(frame)



VERBS.extend([Verb(unchanged, 0),
         Verb(mirror_left_right, 1),
         Verb(mirror_up_down, 1),
         Verb(rotate_90_left, 2),
         Verb(rotate_90_right, 2),
        ])
VERBS.sort(key=lambda x: x[1])


