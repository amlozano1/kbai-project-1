__author__ = 'anthony'
from itertools import product

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


def get_assignments(from_fig, to_fig):
    """
    diffs each frame between two figures and decides which frames go with the other figure's frames
    :param from_fig: A RPM figure that has some frames in it
    :param to_fig: A RPM figure that has some frames in it
    :return: A mapping of each frame in from_fig to each frame in to_fig. If there aren;t enough to map them all,
        the mapping assigns None to those with the highest probability of being deleted.
    """
    all_combinations = product(from_fig.frames.values(), to_fig.frames.values())

    to_keys = sorted(to_fig.objects.keys())
    from_keys = sorted(from_fig.objects.keys())
    agent_task_cost_matrix = {key: dict.fromkeys(to_keys) for key in from_keys}
    diffs = {key: dict.fromkeys(to_keys) for key in from_keys}

    for first, second in all_combinations:
        diffs[first.name][second.name] = first.diff(second)
        agent_task_cost_matrix[first.name][second.name] = diffs[first.name][second.name].total_changes

    costs = {}
    for first in from_fig.frames.values():
        costs[first.name] = sum(agent_task_cost_matrix[first.name].values())
    assignments = {}
    assigned_already = []
    # go through matrix, sorted by total cost, and make assignments. When you run out, the rest get assigned None.
    for key, values in sorted(agent_task_cost_matrix.items(), key=lambda key_val_tup: costs[key_val_tup[0]]):
        for assigned in assigned_already:
            del values[assigned]
        if values:
            min_key = min(values, key=values.get)
        else:
            min_key = None
        assignments[key] = min_key
        if min_key is not None:
            assigned_already.append(min_key)

    return assignments