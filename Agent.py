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

from Verbs import VERBS
from ObjFrame import *
from helpers import clean

logger = logging.getLogger('Agent')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


class Agent:
    # The default constructor for your Agent. Make sure to execute any
    # processing necessary before your Agent starts solving problems here.
    #
    # Do not add any variables to this signature; they will not be used by
    # main().
    def __init__(self):
        self.attributes = dict()
        self.problems_count = 0
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
        self.problems_count += 1
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
        A, B, C = problem.figures['A'], problem.figures['B'], problem.figures['C']
        self.add_frames(A)
        self.add_frames(B)
        self.add_frames(C)
        a1, a2, a3, a4, a5, a6 = [problem.figures[str(i)] for i in range(1,7)]
        if problem.problemType == '3x3':
            logger.warn("3x3 isn't done yet")
            return -1

        a = self.generate_deltas(problem.figures['A'], problem.figures['B'])
        # self.build_sem_net(A, B)
        # print "breakpoint"
        return -1

    def build_sem_net(self, from_figs, to_figs):
        sem_net = {fig.name: [] for fig in from_figs.objects}
        available_fig_attrs = deepcopy(to_figs.attributes)
        for figure in from_figs.objects.values():
            for verbname, verb in VERBS.items():
                if verb.method(figure).attributes in available_fig_attrs:
                    sem_net[figure.name].append((verbname, available_fig_attrs))

    #
    #
    def generate_deltas(self, from_fig, to_fig):
        all_objs = {}
        all_objs.update(from_fig.objects)
        all_objs.update(to_fig.objects)
        all_combinations = product(from_fig.objects.values(), to_fig.objects.values())

        to_keys = to_fig.objects.keys()
        from_keys = from_fig.objects.keys()
        agent_task_cost_matrix = {key: dict.fromkeys(to_keys) for key in from_keys}

        for first, second in all_combinations:
            transforms = list(self.find_transforms(first, second))
            if transforms:
                agent_task_cost_matrix[first.name][second.name] = min(transforms, key=lambda verb: verb.cost)


    def find_transforms(self, first, second):
        for method_name, verb in VERBS.items():
            if self.obj_eq(verb.method(second), first):
                yield verb

    def obj_eq(self, first, second):
        return first.attributes == second.attributes

    def add_frames(self, raven_figure):
        raven_figure.frames = {}
        for name, obj in raven_figure.objects.items():
            raven_figure.frames[obj.name] = ObjFrame(**obj.clean_attributes)

    def __del__(self):
        self.attributes['above'] = {}
        self.attributes['below'] = {}
        self.attributes['inside'] = {}
        self.attributes['left_of'] = {}
        self.attributes['right_of'] = {}
        self.attributes['overlaps'] = {}
        pprint(self.attributes)
        print(self.problems_count)