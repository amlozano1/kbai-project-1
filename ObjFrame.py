__author__ = 'anthony'

from enum import Enum
from helpers import clean


class Alignment(Enum):
    bottom_left = 1
    bottom_right = 2
    top_left = 3
    top_right = 4
    center = 5


class Angle(Enum):
    _0 = 0
    _135 = 135
    _180 = 180
    _225 = 225
    _270 = 270
    _315 = 315
    _45 = 45
    _90 = 90


class Fill(Enum):
    left_half = 1
    no = 2
    right_half = 3
    top_half = 4
    yes = 5


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
    right = 9
    triangle = 10
    square = 11
    star = 12
    right_triangle = 13
    unknown = 14


class Size(Enum):
    huge = 1
    large = 2
    small = 3
    medium = 4
    very_large = 5
    very_small = 6


class ObjFrame:
    def __init__(self, above=None,
                 below=None,
                 left_of=None,
                 right_of=None,
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
            above = set()
        if below is None:
            below = set()
        if left_of is None:
            left_of = set()
        if right_of is None:
            right_of = set()
        if overlaps is None:
            overlaps = set()
        if inside is None:
            inside = set()
        if isinstance(shape, str):
            shape = getattr(Shape, clean(shape))
        if isinstance(alignment, str):
            alignment = getattr(Alignment, clean(alignment))
        if isinstance(fill, str):
            fill = getattr(Fill, clean(fill))
        if isinstance(angle, str):
            angle = getattr(Angle, '_' + str(angle))
        if isinstance(size, str):
            size = getattr(Size, clean(size))
        if isinstance(width, str):
            width = getattr(Width, clean(width))
        if isinstance(height, str):
            height = getattr(Height, clean(height))

        def __eq__(self, other):
            return ((self.above == other.above) and
                    (self.below == other.below) and
                    (self.left_of == other.left_of) and
                    (self.right_of == other.right_of) and
                    (self.overlaps == other.overlaps) and
                    (self.inside == other.inside) and
                    (self.shape == other.shape) and
                    (self.alignment == other.alignment) and
                    (self.fill == other.fill) and
                    (self.angle == other.angle) and
                    (self.size == other.size) and
                    (self.height == other.height) and
                    (self.width == other.width))

        def diff(self, other):
            """
            diff
            :param other: the other frame to compare with.
            :return: A frame with only the differences between two frames.
            """
            removed_above = self.above - other.above
            removed_below = self.below - other.below
            removed_left_of = self.left_of - other.left_of
            removed_right_of = self.right_of - other.right_of
            removed_overlaps = self.overlaps - other.overlaps
            removed_inside = self.inside - other.inside

            added_above = other.above - self.above
            added_below = other.below - self.below
            added_left_of = other.left_of - self.left_of
            added_right_of = other.right_of - self.right_of
            added_overlaps = other.overlaps - self.overlaps
            added_inside = other.inside - self.inside

            shape_change = self.shape, other.shape if self.shape != other.shape else None
            alignment_change = self.alignment, other.alignment if self.alignment != other.alignment else None
            fill_change = self.fill, other.fill if self.fill != other.fill else None
            angle_change = self.angle, other.angle if self.angle != other.angle else None
            size_change = self.size, other.size if self.size != other.size else None
            height_change = self.height, other.height if self.height != other.height else None
            width_change = self.width, other.width if self.width != other.width else None

            positional_changes = [removed_above,
                                  removed_below,
                                  removed_left_of,
                                  removed_right_of,
                                  removed_overlaps,
                                  removed_inside,
                                  added_above,
                                  added_below,
                                  added_left_of,
                                  added_right_of,
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
                    shape_change_count += 1

            total_changes = positional_change_count + shape_change_count
            #return positional_changes, shape_changes, positional_change_count, shape_change_count, total_changes
            return total_changes

