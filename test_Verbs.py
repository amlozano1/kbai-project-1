from unittest import TestCase
from Verbs import *
from RavensObject import RavensObject

__author__ = 'anthony'


class Test_mirror_angle(TestCase):
    def test_mirror_angle_180_360(self):
        a = RavensObject('1')
        a.attributes['angle'] = '180'

        expected = RavensObject('2')
        expected.attributes['angle'] = '0'
        self.assertEqual(mirror_angle(a).attributes, expected.attributes)

    def test_mirror_angle1_181(self):
        a = RavensObject('1')
        a.attributes['angle'] = '1'

        expected = RavensObject('2')
        expected.attributes['angle'] = '181'
        self.assertEqual(mirror_angle(a).attributes, expected.attributes)

    def test_mirror_angle_360_180(self):
        a = RavensObject('1')
        a.attributes['angle'] = '360'

        expected = RavensObject('2')
        expected.attributes['angle'] = '180'
        self.assertEqual(mirror_angle(a).attributes, expected.attributes)
