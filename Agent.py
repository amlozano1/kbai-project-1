# Your Agent for solving Raven's Progressive Matrices. You MUST modify this file.
#
# You may also create and submit new files in addition to modifying this file.
#
# Make sure your file retains methods with the signatures:
# def __init__(self)
# def Solve(self,problem)
#
# These methods will be necessary for the project's main method to run.

# Install Pillow and uncomment this line to access image processing.
from PIL import Image
from PIL.ImageChops import difference
from pprint import pformat
from copy import deepcopy
from itertools import combinations
import logging
import sys

from Verbs import VERBS, binary_verbs
from ObjFrame import *
from helpers import clean, get_assignments, rmsdiff_2011, find_blobs

logger = logging.getLogger('Agent')
# Dear most esteemed grader, you can turn off the output by changing this to logging.INFO or higher.
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

Delta = namedtuple("Delta", "fro to verbs")

# Exponentially expensive work factor for Agent to search for transformations until it gives up
MAX_VERB_COMBINATIONS = 3


class Agent:
    # The default constructor for your Agent. Make sure to execute any
    # processing necessary before your Agent starts solving problems here.
    #
    # Do not add any variables to this signature; they will not be used by
    # main().
    def __init__(self):
        self.attributes = dict()
        self.problems_count = 1
        self.show_images = False


    # The primary method for solving incoming Raven's Progressive Matrices.
    # For each problem, your Agent's Solve() method will be called. At the
    # conclusion of Solve(), your Agent should return an integer representing its
    # answer to the question: "1", "2", "3", "4", "5", or "6". These integers
    # are also the Names of the individual RavensFigures, obtained through
    # RavensFigure.getName() (as Strings).
    #
    # In addition to returning your answer at the end of the method, your Agent
    # may also call problem.checkAnswer(int givenAnswer). The parameter
    # passed to checkAnswer should be your Agent's current guess for the
    # problem; checkAnswer will return the correct answer to the problem. This
    # allows your Agent to check its answer. Note, however, that after your
    # agent has called checkAnswer, it will *not* be able to change its answer.
    # checkAnswer is used to allow your Agent to learn from its incorrect
    # answers; however, your Agent cannot change the answer to a question it
    # has already answered.
    #
    # If your Agent calls checkAnswer during execution of Solve, the answer it
    # returns will be ignored; otherwise, the answer returned at the end of
    # Solve will be taken as your Agent's answer to this problem.
    #
    # Make sure to return your answer *as an integer* at the end of Solve().
    # Returning your answer as a string may cause your program to crash.
    def Solve(self, problem):
        solution = '-1'
        # logger.debug(pformat(VERBS))
        logger.debug("-" * 79)
        logger.debug("Starting problem {}".format(problem.name))

        name = problem.name

        a = problem.figures['A']
        b = problem.figures['B']
        c = problem.figures['C']
        if problem.problemType == '3x3':
            d = problem.figures['D']
            e = problem.figures['E']
            f = problem.figures['F']
            g = problem.figures['G']
            h = problem.figures['H']

        problem.answers = [problem.figures['1'],
                           problem.figures['2'],
                           problem.figures['3'],
                           problem.figures['4'],
                           problem.figures['5'],
                           problem.figures['6'],
                           problem.figures['7'],
                           problem.figures['8'],]

        self.load_images_bw(problem)

        # transition_A_B_C = self.find_binary_verbs(a.image, b.image, c.image)
        # transition_D_E_F = self.find_binary_verbs(a.image, b.image, c.image)
        # if (transition_A_B_C is not None and
        #     transition_D_E_F is not None and
        #     transition_A_B_C == transition_D_E_F):
        #     expected = transition_A_B_C.method(g.image, h.image)
        #     for answer in problem.answers:
        #         #answer.image.show("answer")
        #         #expected.show("expected")
        #         answer.rms = rmsdiff_2011(expected, answer.image)
        #     solution = min(problem.answers, key=lambda answer: answer.rms).name
        #     logger.debug('Found answer from ABC and DEF transitions ({}), {}'.format(transition_A_B_C, solution))
        # else:
        #
        #     pass
        for name, figure in sorted(problem.figures.items()):
            figure.blobs = find_blobs(figure.image)
        if problem.checkAnswer(solution) == int(solution):
            logger.debug("Correct!")
        else:
            logger.debug("Incorrect...")
        return solution

    def load_images_bw(self, problem):
        """
        loads each image from disk in black and white mode with 2 colors. Stashes the result in figure.image
        """
        for name, figure in problem.figures.items():
            figure.image = Image.open(figure.visualFilename)
            figure.image = figure.image.convert('1')


    @staticmethod
    def find_verbs(first, second):
        """
        :Note This is where we spend all our computation time... Optimize here.
        Searches through in order list of all verbs that can be applied to figures to try and find some list of verbs
        that creates the transformation. Verbs are arranged by cost. Verb combinations are roughly arranged by cost,
        but actually done in lexicographic order, which is hopefully 'good enough'. Future improvement ideas: make this
        a generator with Yield so that the Agent can spend time looking for more potential solutions, and if one of
        those potential solutions turns out to be correct change the verb cost factors accordingly in order to 'learn'
        which verbs are preferable to others.
        :param first: the image we are transforming from
        :param second: the image we are transforming to
        :return: a list of verbs which when applied in order will change first to second.

        :var MAX_VERB_COMBINATIONS This is the max depth the Agent will search for until giving up. 3 would mean 3 verbs
        in sequence.
        """
        i = 1
        while i < MAX_VERB_COMBINATIONS:
            verb_combinations = list(combinations(VERBS, i))
            new = first.copy()
            for verbs in verb_combinations:
                for verb in verbs:
                    new = verb.method(new, second)
                rms = rmsdiff_2011(new, second)
                if rms < .1:
                    return verbs
            i += 1
        return None

    @staticmethod
    def find_binary_verbs(first, second, expected):
        """
        :Note This is where we spend all our computation time... Optimize here.
        Searches through in order list of all verbs that can be applied to figures to try and find some list of verbs
        that creates the transformation. Verbs are arranged by cost. Verb combinations are roughly arranged by cost,
        but actually done in lexicographic order, which is hopefully 'good enough'. Future improvement ideas: make this
        a generator with Yield so that the Agent can spend time looking for more potential solutions, and if one of
        those potential solutions turns out to be correct change the verb cost factors accordingly in order to 'learn'
        which verbs are preferable to others.
        :param first: the image we are transforming from
        :param second: the image we are transforming to
        :return: a list of verbs which when applied in order will change first to second.

        :var MAX_VERB_COMBINATIONS This is the max depth the Agent will search for until giving up. 3 would mean 3 verbs
        in sequence.
        """
        i = 1
        for verb in binary_verbs:
            result = verb.method(first, second)
            # result.show("result")
            # expected.show("expected")
            rms = rmsdiff_2011(result, expected)
            if rms < 32:
                return verb
        i += 1
        return None