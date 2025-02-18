import sys, os, unittest
from src.utilities.data_structures import BoolArr


class TestBoolArr(unittest.TestCase):

    def test_empty_array(self):
        empty_arr = BoolArr()
        self.assertEqual(len(empty_arr), 0)
        self.assertEqual(empty_arr.__repr__(), "[]")

    def test_array_with_capacity(self):
        arr = BoolArr(4)
        self.assertEqual(len(arr), 4)
        self.assertEqual(arr.__repr__(), "[False, False, False, False]")

    def test_set_and_get_item(self):
        arr = BoolArr(4)
        arr[2] = True
        self.assertTrue(arr[2])

    def test_repr(self):
        arr = BoolArr(3)
        arr[0] = True
        arr[1] = False
        arr[2] = True
        self.assertEqual(arr.__repr__(), "[True, False, True]")

if __name__ == '__main__':
    unittest.main()