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
from pprint import pformat
from copy import deepcopy
from itertools import combinations
import logging
import sys

from Verbs import VERBS, add, Verb, delete
from ObjFrame import *
from helpers import clean, get_assignments

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
        # logger.debug(pformat(VERBS))
        logger.debug("-" * 79)
        logger.debug("Starting problem {}".format(self.problems_count))

        name = problem.name



        # Keep track of all unique attributes seen in Agent Memory
        for figure in problem.figures.values():
            for raven_object in figure.objects.values():
                raven_object.clean_attributes = {}
                for attribute, value in raven_object.attributes.items():
                    # Dashes/spaces mess with Python kwarg unpacking. Clean them up
                    attribute = clean(attribute)
                    value = clean(value)
                    raven_object.clean_attributes[attribute] = value
                    self.attributes.setdefault(attribute, set())
                    self.attributes[attribute].add(value)

        # Build frames
        self.add_all_frames(problem)
        if problem.problemType == '3x3':
            logger.warn("3x3 isn't done yet")
            self.problems_count += 1
            return -1
        if not problem.hasVerbal:
            logger.warn("Visual isn't done yet")
            return -1

        A_B_assignments = get_assignments(problem.figures['A'], problem.figures['B'])
        A_C_assignments = get_assignments(problem.figures['A'], problem.figures['C'])

        A_B_deltas = self.get_deltas(A_B_assignments, problem.figures['A'], problem.figures['B'])
        A_C_deltas = self.get_deltas(A_C_assignments, problem.figures['A'], problem.figures['C'])

        # These are potentially useful but eat up a TON of CPU time. Kept here for posterity.
        # key_range = [str(i) for i in range(1, 7)]
        # B_a_assignments = {key: (self.get_assignments(problem.figures['B'], problem.figures[key])) for key in key_range}
        # C_a_assignments = {key: (self.get_assignments(problem.figures['C'], problem.figures[key])) for key in key_range}

        # B_a_deltas = [self.get_deltas(B_a_assignments[key], problem.figures['B'], problem.figures[key]) for key in key_range]
        # C_a_deltas = [self.get_deltas(C_a_assignments[key], problem.figures['C'], problem.figures[key]) for key in key_range]

        B_to_a_expected_frames = self.apply_deltas(A_C_deltas, A_B_assignments, problem.figures['B'].frames)
        C_to_a_expected_frames = self.apply_deltas(A_B_deltas, A_C_assignments, problem.figures['C'].frames)

        if set(problem.figures['1'].frames.values()) == B_to_a_expected_frames:
            answer = 1
        elif set(problem.figures['2'].frames.values()) == B_to_a_expected_frames:
            answer = 2
        elif set(problem.figures['3'].frames.values()) == B_to_a_expected_frames:
            answer = 3
        elif set(problem.figures['4'].frames.values()) == B_to_a_expected_frames:
            answer = 4
        elif set(problem.figures['5'].frames.values()) == B_to_a_expected_frames:
            answer = 5
        elif set(problem.figures['6'].frames.values()) == B_to_a_expected_frames:
            answer = 6
        else:  # If the Agent couldn't generate the answer and check with B_to_a, it can try C_to_a...
            if set(problem.figures['1'].frames.values()) == C_to_a_expected_frames:
                answer = 1
            elif set(problem.figures['2'].frames.values()) == C_to_a_expected_frames:
                answer = 2
            elif set(problem.figures['3'].frames.values()) == C_to_a_expected_frames:
                answer = 3
            elif set(problem.figures['4'].frames.values()) == C_to_a_expected_frames:
                answer = 4
            elif set(problem.figures['5'].frames.values()) == C_to_a_expected_frames:
                answer = 5
            elif set(problem.figures['6'].frames.values()) == C_to_a_expected_frames:
                answer = 6
            else:
                answer = 5  # No guessing penalty, so just guess 5. TODO, change to -1 when there is a guessing penalty.

        correct_answer = problem.checkAnswer(answer)
        correct = "Correct" if correct_answer == answer else "Wrong"
        logger.debug("Ending problem {}, Answered {}, {}".format(self.problems_count, answer, correct))
        self.problems_count += 1
        return answer

    def apply_deltas(self, deltas, assignments, frames):
        """
        Applies a list of deltas to a set of a figures frames given assignments.
        :param deltas: list of deltas to run
        :param assignments: a mapping that lists which frames must have deltas applied
        :param frames: the frames to apply the deltas to
        :return: a new set of frames with the deltas applied.
        """
        expected_frames = set()
        for delta in deltas:
            if delta.fro.name not in assignments:
                expected = delta.verbs[0].method(delta.fro)  # This frame was added
            elif assignments[delta.fro.name] is None:
                expected = None
            else:
                expected = deepcopy(frames[assignments[delta.fro.name]])
                for verb in delta.verbs:
                    expected = verb.method(expected)
            if expected is not None:
                expected_frames.add(expected)
        return expected_frames

    def add_frames(self, raven_figure):
        raven_figure.frames = {}
        for name, obj in raven_figure.objects.items():
            raven_figure.frames[obj.name] = ObjFrame(name=obj.name, **obj.clean_attributes)
        for frame in raven_figure.frames.values():
            frame.fill_positions(raven_figure.frames)

    def add_all_frames(self, problem):
        """
        Helper that adds frames for each figure in the problem.
        """
        A, B, C = problem.figures['A'], problem.figures['B'], problem.figures['C']
        a1, a2, a3, a4, a5, a6 = [problem.figures[str(i)] for i in range(1, 7)]
        self.add_frames(A)
        self.add_frames(B)
        self.add_frames(C)
        self.add_frames(a1)
        self.add_frames(a2)
        self.add_frames(a3)
        self.add_frames(a4)
        self.add_frames(a5)
        self.add_frames(a6)

    def get_deltas(self, assignments, from_fig, to_fig):
        """
        Given assignments from_fig to_fig, finds deltas between them.
        """
        deltas = set()
        found_deltas = []
        for assigner, assigned in assignments.items():
            if assigned is None:
                assigner_frame = from_fig.frames[assigner]
                deltas.add(Delta(assigner_frame, assigned, (Verb(delete, 5),)))
                found_deltas.append(assigned)
            else:
                assigner_frame = from_fig.frames[assigner]
                assigned_frame = to_fig.frames[assigned]
                find_verbs = self.find_verbs(assigner_frame, assigned_frame)
                if find_verbs is not None:
                    deltas.add(Delta(assigner_frame, assigned_frame, find_verbs))
                    found_deltas.append(assigned)
        unfound_deltas = [value for key, value in to_fig.frames.items() if key not in found_deltas]
        for value in unfound_deltas:
            deltas.add(Delta(value, value, (Verb(add, 5),)))
        return frozenset(deltas)

    @staticmethod
    def find_verbs(first_frame, second_frame):
        """
        :Note This is where we spend all our computation time... Optimize here.
        Searches through in order list of all verbs that can be applied to figures to try and find some list of verbs
        that creates the transformation. Verbs are arranged by cost. Verb combinations are roughly arranged by cost,
        but actually done in lexicographic order, which is hopefully 'good enough'. Future improvement ideas: make this
        a generator with Yield so that the Agent can spend time looking for more potential solutions, and if one of
        those potential solutions turns out to be correct change the verb cost factors accordingly in order to 'learn'
        which verbs are preferable to others.
        :param first_frame: the frame we are transforming from
        :param second_frame: the frame we are transforming to
        :return: a list of verbs which when applied in order will change first_frame to second_frame.

        :var MAX_VERB_COMBINATIONS This is the max depth the Agent will search for until giving up. 3 would mean 3 verbs
        in sequence.
        """
        i = 1
        while i < MAX_VERB_COMBINATIONS:
            verb_combinations = list(combinations(VERBS, i))
            for verbs in verb_combinations:
                new = deepcopy(first_frame)
                for verb in verbs:
                    new = verb.method(new)
                    if new == second_frame:
                        return verbs
            i += 1
        return None

    def __del__(self):
        self.attributes['above'] = {}
        self.attributes['inside'] = {}
        self.attributes['left_of'] = {}
        self.attributes['overlaps'] = {}
        logger.debug(pformat(self.attributes))
        logger.debug(self.problems_count)
