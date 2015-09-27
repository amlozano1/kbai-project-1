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
from pprint import pprint
from copy import deepcopy
from itertools import product
import logging
import sys
import multiprocessing
from Verbs import VERBS
from ObjFrame import *
from helpers import clean


logger = logging.getLogger('Agent')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

process_pool = multiprocessing.Pool()  # should be the number of CPUs on system. Gotta Go Fast.


Delta = namedtuple("Delta", "fro to verbs")

MAX_VERB_COMBINATIONS = 4  # Exponentially expensive work factor for Agent to search for transformations until it gives up

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

        A_B_assignments = self.get_assignments(problem.figures['A'], problem.figures['B'])
        A_C_assignments = self.get_assignments(problem.figures['A'], problem.figures['C'])

        A_B_deltas = self.get_deltas(A_B_assignments, problem.figures['A'], problem.figures['B'])
        A_C_deltas = self.get_deltas(A_C_assignments, problem.figures['A'], problem.figures['C'])


        # These are potentially useful but eat up a TON of CPU time.
        # key_range = [str(i) for i in range(1, 7)]
        # B_a_assignments = {key: (self.get_assignments(problem.figures['B'], problem.figures[key])) for key in key_range}
        # C_a_assignments = {key: (self.get_assignments(problem.figures['C'], problem.figures[key])) for key in key_range}

        #B_a_deltas = [self.get_deltas(B_a_assignments[key], problem.figures['B'], problem.figures[key]) for key in key_range]
        #C_a_deltas = [self.get_deltas(C_a_assignments[key], problem.figures['C'], problem.figures[key]) for key in key_range]

        B_to_a_expected_frames = set()
        for delta in A_C_deltas:
            expected = deepcopy(problem.figures['B'].frames[A_B_assignments[delta.fro.name]])
            for verb in delta.verbs:
                expected = verb.method(expected)
            B_to_a_expected_frames.add(expected)
        C_to_a_expected_frames = set()
        for delta in A_B_deltas:
            expected = deepcopy(problem.figures['C'].frames[A_C_assignments[delta.fro.name]])
            for verb in delta.verbs:
                expected = verb.method(expected)
            C_to_a_expected_frames.add(expected)


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
        else:
            answer = -1

        correct_answer = problem.checkAnswer(answer)
        # self.build_sem_net(A, B)
        correct = "Correct" if correct_answer == answer else "Wrong"
        logger.debug("Ending problem {}, Answered {}, {}".format(self.problems_count, answer, correct))
        self.problems_count += 1
        return answer

    def add_all_frames(self, problem):
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

    # def build_sem_net(self, from_figs, to_figs):
    #     sem_net = {fig.name: [] for fig in from_figs.objects}
    #     available_fig_attrs = deepcopy(to_figs.attributes)
    #     for figure in from_figs.objects.values():
    #         for verbname, verb in VERBS.items():
    #             if verb.method(figure).attributes in available_fig_attrs:
    #                 sem_net[figure.name].append((verbname, available_fig_attrs))

    def get_deltas(self, assignments, from_fig, to_fig):
        deltas = set()
        for assigner, assigned in assignments.items():
            if assigner is None or assigned is None:
                continue
            assigner_frame = from_fig.frames[assigner]
            assigned_frame = to_fig.frames[assigned]
            find_verbs = self.find_verbs(assigner_frame, assigned_frame)
            if find_verbs is not None:
                deltas.add(Delta(assigner_frame, assigned_frame, find_verbs))
        return frozenset(deltas)

    def find_verbs(self, first_frame, second_frame):
        """
        :Note This is where we spend all our computation time... Optimize here.
        Searches through in order list of all verbs that can be
        applied to figures to try and find some list of verbs that creates the transformation. Verbs are arranged by
        cost. Verb combinations are roughly arranged by cost, but actually done in lexicographic order, which is hopefully
        'good enough'. Future improvement ideas: make this a generator with Yield so that the Agent can spend time
        looking for more potential solutions, and if one of those potential solutions turns out to be correct change
        the verb cost factors accordingly in order to 'learn' which verbs are preferable to others
        :param first_frame: the frame we are transforming from
        :param second_frame: the frame we are transforming to
        :return: a list of verbs which when applied in order will change first_frame to second_frame.

        :var MAX_VERB_COMBINATIONS This is the max depth the Agent will search for until giving up. 3 would mean 3 verbs
        in sequence.
        """
        i = 1
        while i < MAX_VERB_COMBINATIONS:
            for verbs in product(VERBS, repeat=i):
                new = deepcopy(first_frame)
                for verb in verbs:
                    new = verb.method(new)
                    if new == second_frame:
                        return verbs
            i+=1
        return None

    def get_assignments(self, from_fig, to_fig):
        all_combinations = product(from_fig.frames.values(), to_fig.frames.values())

        to_keys = to_fig.objects.keys()
        from_keys = from_fig.objects.keys()
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
        #go through matrix, sorted by total cost, and make assignments. When you run out, the rest get assigned None.
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

    def add_frames(self, raven_figure):
        raven_figure.frames = {}
        for name, obj in raven_figure.objects.items():
            raven_figure.frames[obj.name] = ObjFrame(name=obj.name, **obj.clean_attributes)
        for frame in raven_figure.frames.values():
            frame.fill_positions(raven_figure.frames)

    def __del__(self):
        self.attributes['above'] = {}
        self.attributes['inside'] = {}
        self.attributes['left_of'] = {}
        self.attributes['overlaps'] = {}
        pprint(self.attributes)
        print(self.problems_count)