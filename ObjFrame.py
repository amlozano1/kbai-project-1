__author__ = 'anthony'

from enum import Enum
from helpers import clean
from collections import namedtuple

class Alignment(Enum):
    bottom_left = 1
    bottom_right = 2
    top_left = 3
    top_right = 4
    center = 5  #Center can also mean something like 'unaligned'. This is important.


class Angle(Enum):
    _0 = 0
    _45 = 45
    _90 = 90
    _135 = 135
    _180 = 180
    _225 = 225
    _270 = 270
    _315 = 315


class Fill(Enum):
    no = 1
    left_half = 2
    right_half = 3
    top_half = 4
    bottom_half = 5
    yes = 6


class Height(Enum):
    huge = 1
    large = 2
    small = 3


class Width(Enum):
    huge = 1
    large = 2
    small = 3


class Shape(Enum):
    circle = 1
    diamond = 2
    heart = 3
    octagon = 4
    pac_man = 5
    pentagon = 6
    plus = 7
    rectangle = 8
    triangle = 11
    square = 12
    star = 13
    right_triangle = 14
    unknown = 15


class Size(Enum):
    huge = 1
    large = 2
    small = 3
    medium = 4
    very_large = 5
    very_small = 6

Shape_Change = namedtuple('Shape_Change', 'from_ to weight')

FrameDelta = namedtuple('FrameDelta', 'positional_changes shape_changes positional_change_count shape_change_count total_changes')

class ObjFrame:
    def __init__(self, name=None,
                 above=None,
                 left_of=None,
                 overlaps=None,
                 inside=None,
                 shape=Shape.unknown,
                 alignment=Alignment.center,
                 fill=Fill.no,
                 angle=Angle._0,
                 size=Size.small,
                 width=Width.small,
                 height=Height.small):

        if above is None:
            self.above = frozenset()
        else:
            self.above = frozenset(above.split(','))
        if left_of is None:
            self.left_of = frozenset()
        else:
            self.left_of = frozenset(left_of.split(','))
        if overlaps is None:
            self.overlaps = frozenset()
        else:
            self.overlaps = frozenset(overlaps.split(','))
        if inside is None:
            self.inside = frozenset()
        else:
            self.inside = frozenset(inside.split(','))

        self.name = name
        self.shape = shape
        self.alignment = alignment
        self.fill = fill
        self.angle = angle
        self.size = size
        self.width = width
        self.height = height

        if isinstance(shape, str):
            self.shape = getattr(Shape, clean(shape))
        if isinstance(alignment, str):
            self.alignment = getattr(Alignment, clean(alignment))
        if isinstance(fill, str):
            self.fill = getattr(Fill, clean(fill))
        if isinstance(angle, str):
            self.angle = getattr(Angle, '_' + str(angle))
        if isinstance(size, str):
            self.size = getattr(Size, clean(size))
        if isinstance(width, str):
            self.width = getattr(Width, clean(width))
        if isinstance(height, str):
            self.height = getattr(Height, clean(height))

    def __eq__(self, other):
        if other is None:
            return False
        checks = (self.above == other.above,
                  self.left_of == other.left_of,
                  self.overlaps == other.overlaps,
                  self.inside == other.inside,
                  self.shape == other.shape,
                  self.alignment == other.alignment,
                  self.fill == other.fill,
                  self.size == other.size,
                  self.height == other.height,
                  self.width == other.width,)
        if not all(checks):
            return False

        # Angle is meaningless for these shapes.
        if self.shape in (Shape.diamond, Shape.square, Shape.circle, Shape.octagon):
            return True
        else:
            return self.angle == other.angle

    def __key(self):
        # Angle is meaningless for these shapes.
        if self.shape in (Shape.diamond, Shape.square, Shape.circle, Shape.octagon):
            return (self.above,
                self.left_of,
                self.overlaps,
                self.inside,
                self.shape,
                self.alignment,
                self.fill,
                self.size,
                self.height,
                self.width,)
        else:
            return (self.above,
                self.left_of,
                self.overlaps,
                self.inside,
                self.shape,
                self.alignment,
                self.fill,
                self.angle,
                self.size,
                self.height,
                self.width,)

    def __hash__(self):
        return hash(self.__key())

    def diff(self, other):
        """
        diff
        :param other: the other frame to compare with.
        :return: A frame with only the differences between two frames.
        """
        removed_above = self.above - other.above
        removed_left_of = self.left_of - other.left_of
        removed_overlaps = self.overlaps - other.overlaps
        removed_inside = self.inside - other.inside

        added_above = other.above - self.above
        added_left_of = other.left_of - self.left_of
        added_overlaps = other.overlaps - self.overlaps
        added_inside = other.inside - self.inside

        if self.shape != other.shape:
            shape_change = Shape_Change(self.shape, other.shape, 5)
        else:
            shape_change = None

        if self.alignment != other.alignment:
            alignment_change = Shape_Change(self.alignment, other.alignment, 1)
        else:
            alignment_change = None

        if self.fill != other.fill:
            fill_change = Shape_Change(self.fill, other.fill, abs(self.fill.value - other.fill.value))
        else:
            fill_change = None

        if self.angle != other.angle:
            angle_change = Shape_Change(self.angle, other.angle, abs(self.angle.value - other.angle.value) / 45 ) #divide by 45 to normalize it
        else:
            angle_change = None

        if self.size != other.size:
            size_change = Shape_Change(self.size, other.size, abs(self.size.value - other.size.value))
        else:
            size_change = None

        if self.height != other.height:
            height_change = Shape_Change(self.height, other.height, abs(self.height.value - other.height.value))
        else:
            height_change = None

        if self.width != other.width:
            width_change = Shape_Change(self.width, other.width, abs(self.width.value - other.width.value))
        else:
            width_change = None

        positional_changes = [removed_above,
                              removed_left_of,
                              removed_overlaps,
                              removed_inside,
                              added_above,
                              added_left_of,
                              added_overlaps,
                              added_inside,]

        shape_changes = [shape_change,
                         alignment_change,
                         fill_change,
                         angle_change,
                         size_change,
                         height_change,
                         width_change,]


        positional_change_count = 0
        for set in positional_changes:
            positional_change_count += len(set)

        shape_change_count = 0
        for change in shape_changes:
            if change is not None:
                shape_change_count += change.weight

        total_changes = positional_change_count + shape_change_count
        return FrameDelta(positional_changes, shape_changes, positional_change_count, shape_change_count, total_changes)
        #return total_changes

    def fill_positions(self, frames):
        new_above = set()
        for string in self.above:
            new_above.add(frames[string])
        self.above = frozenset(new_above)

        new_left_of = set()
        for string in self.left_of:
            new_left_of.add(frames[string])
        self.left_of = frozenset(new_left_of)

        new_overlaps = set()
        for string in self.overlaps:
            new_overlaps.add(frames[string])
        self.overlaps = frozenset(new_overlaps)

        new_inside = set()
        for string in self.inside:
            new_inside.add(frames[string])
        self.inside = frozenset(new_inside)

    def __repr__(self):
        return self.name