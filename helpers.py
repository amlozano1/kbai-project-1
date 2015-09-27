__author__ = 'anthony'
from copy import deepcopy


def clean(bad_string):
    return bad_string.replace('-', '_').replace(' ', '_')

def normalize_degrees(deg):
    deg = deg % 360
    if deg < 0:
        deg += 360
    return deg

def verb_chain_search(verbs, first_frame, second_frame):
        new = deepcopy(first_frame)
        for verb in verbs:
            new = verb.method(new)
            if new == second_frame:
                return verbs