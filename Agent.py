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
from copy import deepcopy
from collections import defaultdict
import logging
import sys

from PIL import Image

from Verbs import binary_verbs
from helpers import rmsdiff_2011, find_blobs

logger = logging.getLogger('Agent')
# Dear most esteemed grader, you can turn off the output by changing this to logging.INFO or higher.
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
        self.problems_count = 1
        self.blob_lib = []
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
        if name.find("Problem B") != -1:
            return -1
        a = problem.figures['A']
        b = problem.figures['B']
        c = problem.figures['C']
        if problem.problemType == '3x3':
            d = problem.figures['D']
            e = problem.figures['E']
            f = problem.figures['F']
            g = problem.figures['G']
            h = problem.figures['H']

        problem.matrix = [a, b, c, d, e, f, g, h]
        problem.answers = [problem.figures['1'],
                           problem.figures['2'],
                           problem.figures['3'],
                           problem.figures['4'],
                           problem.figures['5'],
                           problem.figures['6'],
                           problem.figures['7'],
                           problem.figures['8'],]

        solution_votes = defaultdict(int)

        self.load_images_bw(problem)
        if name.find("Problem E") != -1:
            transition_A_B_C = self.find_binary_verbs(a.image, b.image, c.image)
            transition_D_E_F = self.find_binary_verbs(a.image, b.image, c.image)
            if (transition_A_B_C is not None and
                transition_D_E_F is not None and
                transition_A_B_C == transition_D_E_F):
                expected = transition_A_B_C.method(g.image, h.image)
                for answer in problem.answers:
                    #answer.image.show("answer")
                    #expected.show("expected")
                    answer.rms = rmsdiff_2011(expected, answer.image)
                solution = min(problem.answers, key=lambda answer: answer.rms).name
                logger.debug('Found answer from ABC and DEF transitions ({}), {}'.format(transition_A_B_C, solution))
            else:

                pass
        else:
            for fig_name, figure in sorted(problem.figures.items()):
                blobs = find_blobs(figure.image)
                figure.blobs = self.get_blob_ids(blobs)

            blob_counts = defaultdict(int)
            for figure in problem.matrix:
                for blob in figure.blobs:
                    blob_counts[blob] += 1
            for answer in problem.answers:
                new_counts = deepcopy(blob_counts)
                for blob in answer.blobs:
                    new_counts[blob] += 1
                counts = list(new_counts.values())
                some_count = counts[0]
                if all([count == some_count for count in counts]):
                    solution_votes[answer.name] += 1
                    logger.debug('Found answer from counting blobs, {}'.format(answer.name))
                if all([count % 3 == 0 for count in counts]):
                    solution_votes[answer.name] += 1
                    logger.debug('Found answer from balancing matrix, {}'.format(answer.name))
                if all([1 == count for count in counts]):
                    solution_votes[answer.name] += 1
                    logger.debug('Found answer from uniquifying matrix, {}'.format(answer.name))
            if solution_votes:
                solution = max(solution_votes.keys(), key=lambda x: solution_votes[x])
                logger.debug("Giving answer {}.".format(solution))
            else:
                logger.debug("Skipped")
                solution = -1


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
    def find_binary_verbs(first, second, expected):
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

    def get_blob_ids(self, blobs):
        blob_ids = []
        for blob in blobs:
            if not self.blob_lib:
                blob_ids.append(len(self.blob_lib))
                self.blob_lib.append(blob)
            else:
                closest = min([(rmsdiff_2011(blob, blob_orig), blob_id) for blob_id, blob_orig in enumerate(self.blob_lib)])
                if closest[0] < 20:
                    blob_ids.append(closest[1])
                else:
                    blob_ids.append(len(self.blob_lib))
                    self.blob_lib.append(blob)
        return blob_ids

    def check_set(self, set1, set2, partial_set3, problem):
        """
        unused strategy that can check if any two rows of 3 create a 'set' (including diagnols).
        This strategy was obsoleted by the balancing matrix strategy.
        """
        a, b, c = set1
        d, e, f = set2
        g, h = partial_set3
        ABC_blob_list = sorted(a + b + c)
        DEF_blob_list = sorted(d + e + f)

        if ABC_blob_list == DEF_blob_list:
            for answer in problem.answers:
                if sorted(answer.blobs + g + h) == ABC_blob_list:
                    solution = answer.name
                    return solution
        return -1