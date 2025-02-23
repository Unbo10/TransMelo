import unittest

from src.utilities.data_structures import IntArr

class TestIntArr(unittest.TestCase):

    def test_empty_array(self):
        # Test creating an empty IntArr
        empty_arr = IntArr()
        self.assertEqual(len(empty_arr), 0)  # Assert the size of the empty array is 0
        self.assertEqual(empty_arr.__repr__(), "[]")  # Assert the correct string representation

    def test_array_with_capacity(self):
        # Test creating an IntArr with a specific size
        arr = IntArr(5)
        self.assertEqual(len(arr), 5)  # Assert the size of the array is 5
        self.assertEqual(arr.__repr__(), "[0, 0, 0, 0, 0]")  # Assert initial values are 0

    def test_set_and_get_item(self):
        # Test setting and getting items in the IntArr
        arr = IntArr(5)
        arr[2] = 25  # Set the 3rd element to 25
        self.assertEqual(arr[2], 25)  # Assert the 3rd element is 25
        arr[4] = 50  # Set the 5th element to 50
        self.assertEqual(arr[4], 50)  # Assert the 5th element is 50

    def test_repr(self):
        # Test the __repr__ method
        arr = IntArr(4)
        arr[0] = 10
        arr[1] = 20
        arr[2] = 30
        arr[3] = 40
        self.assertEqual(arr.__repr__(), "[10, 20, 30, 40]")  # Assert the string representation

    def test_size(self):
        # Test the size of the array
        arr = IntArr(3)
        self.assertEqual(len(arr), 3)  # Assert the size is 3

    def test_contains(self):
        # Test the __contains__ method
        arr = IntArr(5)
        arr[1] = 15
        arr[3] = 30
        self.assertIn(15, arr)  # Assert 15 is in the array
        self.assertIn(30, arr)  # Assert 30 is in the array
        self.assertNotIn(25, arr)  # Assert 25 is not in the array

if __name__ == '__main__':
    unittest.main()
