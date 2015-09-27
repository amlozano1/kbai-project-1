__author__ = 'anthony'



def clean(bad_string):
    return bad_string.replace('-', '_').replace(' ', '_')

def normalize_degrees(deg):
    deg = deg % 360
    if deg < 0:
        deg += 360
    return deg