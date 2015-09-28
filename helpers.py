__author__ = 'anthony'


def clean(bad_string):
    """
    Some strings that come out of attributes have things that python can't use in keywords like spaces or dashes.
    This fucntion replaces them with underscores so they can be used
    :param bad_string: String to replace on
    :return: a cleaned string
    """
    return bad_string.replace('-', '_').replace(' ', '_')


def normalize_degrees(deg):
    """
    takes any angle in degrees and returns an equivalent angle in the range [0,359]
    :param deg: some angle to normalize
    :return: int between 0 and 259, inclusive.
    """
    deg %= 360
    if deg < 0:
        deg += 360
    return deg


def inner_angle(first, second):
    """
    Gets the inner difference between two angles. IE if given 0 and 315, gives 45 instead of 315
    :param first: first angle
    :param second: second angle
    :return: a value between 0 and 180, inclusive.
    """
    return 180 - abs(abs(first - second) - 180)
