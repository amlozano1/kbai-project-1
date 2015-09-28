__author__ = 'anthony'
"""
Master list of atomic transitions that can be applied to shapes in RPM figures.
"""
from collections import namedtuple
from copy import deepcopy
from ObjFrame import Angle, Shape, Alignment, Fill, Size
from helpers import normalize_degrees

Verb = namedtuple('Verb', ['method', 'cost'])

# This list contains possible transitions. (function, current_cost)
VERBS = []


# Begin Factories - Each factory creates a range of verbs for something (usually an enum) and then adds it to the list.
def fill_shape_factory(fill):
    """
    Generates the varios fill verbs
    """

    def to_fill(frame):
        frame = deepcopy(frame)
        frame.fill = fill
        return frame

    return to_fill


for fill in Fill:
    to_fill = fill_shape_factory(fill)
    VERBS.append(Verb(to_fill, 2))


def size_change_factory(size):
    """
    Generates size change verbs. TODO make this generate their costs as well.
    """

    def change_size(frame):
        frame = deepcopy(frame)
        frame.size = size
        return frame

    return change_size


for size in Size:
    change_size = size_change_factory(size)
    VERBS.append(Verb(change_size, 3))


def to_new_shape_factory(shape):
    """
    Generates shape change verbs.
    """

    def to_new_shape(frame):
        frame = deepcopy(frame)
        frame.shape = shape
        return frame

    return to_new_shape


for shape in Shape:
    to_new_shape = to_new_shape_factory(shape)
    VERBS.append(Verb(to_new_shape, 5))


# End Factories.

# Begin single verbs - these are added to the list at the end all at once.
def rotate_90_left(frame):
    rotated = deepcopy(frame)
    rotated.angle = Angle(normalize_degrees(frame.angle.value - 90))
    return rotated


def rotate_90_right(frame):
    rotated = deepcopy(frame)
    rotated.angle = Angle(normalize_degrees(frame.angle.value + 90))
    return rotated


def mirror_up_down(frame):
    """
    Attempts to mirror a shape accross the X axis. This is meaningless for some shapes and impossible to do for a verbal
    description for others (usually shapes with no symmetry about the axis of reflection)..
    """
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
    Attempts to mirror a shape accross the Y axis. This is meaningless for some shapes and impossible to do for a verbal
    description for others (usually shapes with no symmetry about the axis of reflection).
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


def unchanged(frame):
    """
    This method, It does nothing!
    :param frame
    :return: the frame passed in the argument
    """
    return deepcopy(frame)


VERBS.extend([Verb(unchanged, 0),
              Verb(mirror_left_right, 1),
              Verb(mirror_up_down, 1.1),
              Verb(rotate_90_left, 1.5),
              Verb(rotate_90_right, 1.6),
              ])
VERBS.sort(key=lambda x: x[1])  # sort by cost before exporting.


# End single verbs

# Unlisted verbs.
def add(frame):
    """
    Add is not included in VERBS since it is a special case and requires unique handling
    :param frame: frame to add
    :return: a copy of that frame.
    """
    return deepcopy(frame)


def delete(frame):
    """
    Delete is not included in VERBS since it is a special case and requires unique handling
    :param frame: frame to add
    :return: a copy of that frame.
    """
    return None
