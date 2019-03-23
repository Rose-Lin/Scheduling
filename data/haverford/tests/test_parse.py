import unittest
import sys
# from unittest import mock
sys.path.append('../')
from parse import parser

class TestParser(unittest.TestCase):

    def test_conflict_pair(self):
        mock_parser = parser()
        hc_classes = [111, 108, 359,714,1]
        pref_dict ={1: [111, 108, 359, 714], 2:[1]}
        correct_result = {111: {108: 1, 359: 1, 714: 1, 1: 0}, 108: {111: 1, 359: 1, 714: 1, 1: 0}, 359: {111: 1, 108: 1, 714: 1, 1: 0}, 714: {111: 1, 108: 1, 359: 1, 1: 0}, 1: {111: 0, 108: 0, 359: 0, 714: 0}}
        result = mock_parser.conflict_pair(hc_classes, pref_dict)
        maximum = 1
        self.assertEqual(result[0], correct_result)
        self.assertEqual(result[1], maximum)
    
    def test_sorted_conflict_pair(self):
        mock_parser = parser()

if __name__ == '__main__':
    unittest.main()