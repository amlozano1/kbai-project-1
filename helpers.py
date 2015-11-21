__author__ = 'anthony'
from itertools import product
import math
from PIL import ImageChops, ImageFilter, Image
def threshold_255(x):
    return 0 if x < 128 else 255


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

def rmsdiff_2011(im1, im2):
    """
    Calculate the root-mean-square difference between two images. A value close to zero means a good match.
    From: https://code.activestate.com/recipes/577630-comparing-two-images/ with modifications.
    :param im1:
    :param im2:
    :return:
    """
    median_filter = ImageFilter.MedianFilter(size=5)
    diff = ImageChops.difference(im1, im2).filter(median_filter)
    #diff.show()
    h = diff.histogram()
    sq = (value*(idx**2) for idx, value in enumerate(h))
    sum_of_squares = sum(sq)
    rms = math.sqrt(sum_of_squares/float(im1.size[0] * im1.size[1]))
    return rms

def find_blobs(im):
    lable_table = {}
    rows, cols = im.size
    label_buffer = []
    data = list(im.getdata())
    no_label = 0 # 0 is reserved for "No label"
    left_lbl = no_label
    label_idx = 1
    for idx, pixel in enumerate(data):
        x, y = idx // im.size[0], idx % im.size[1]
        left_lbl = label_buffer[-1] if idx % cols != 0 else 0
        if pixel == 255:
            label_buffer.append(0)
        else:
            if idx < cols:
                if left_lbl == 0:
                    label_buffer.append(label_idx)
                    lable_table[label_idx] = {label_idx}
                    label_idx += 1
                else:
                    label_buffer.append(left_lbl)
            else:
                neighbor_lbls = label_buffer[idx - rows - 1:idx - rows + 2]
                neighbor_lbls.append(left_lbl)
                neighbor_lbls = [y for y in neighbor_lbls if y != 0] # remove all zeros
                # We care about the labels marked X in the picture below, Any will do so we grab the max:
                #  XXX
                #  X*.
                #  ...

                new_label = min(neighbor_lbls) if neighbor_lbls else 0
                if new_label == 0:
                    label_buffer.append(label_idx)
                    lable_table[label_idx] = {label_idx}
                    label_idx += 1
                else:
                    label_buffer.append(new_label)
                    other_lbls = {y for y in neighbor_lbls if y != label_buffer[-1]}
                    if other_lbls:
                        lable_table[new_label] |= other_lbls
                        for label in list(other_lbls):
                            lable_table[new_label] |= lable_table[label]
    skip = set()
    blobs = []
    for label, same_as in lable_table.items():
        if label in skip:
            continue
        else:
            blobs.append(list(same_as))
            skip |= same_as
    blob_ims = []
    for blob in blobs:
        image_data = []
        for label in label_buffer:
            if label in blob:
                image_data.append(0)
            else:
                image_data.append(255)
        image = Image.new(im.mode, im.size)
        image.putdata(image_data)
        # image.show()
        blob_ims.append(image)
    return blob_ims