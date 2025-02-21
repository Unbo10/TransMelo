import unittest

from src.utilities.data_structures.strArr import StrArr

class TestStrArr(unittest.TestCase):

    def setUp(self):
        self.str_arr = StrArr(10)  # Initialize with a capacity of 10

    def test_set_and_get_item(self):
        self.str_arr[0] = "hello"
        self.assertEqual(self.str_arr[0], "hello")

    def test_set_and_get_multiple_items(self):
        self.str_arr[0] = "hello"
        self.str_arr[1] = "world"
        self.assertEqual(self.str_arr[0], "hello")
        self.assertEqual(self.str_arr[1], "world")

    def test_set_item_out_of_bounds(self):
        with self.assertRaises(IndexError):
            self.str_arr[10] = "out_of_bounds"

    def test_get_item_out_of_bounds(self):
        with self.assertRaises(IndexError):
            _ = self.str_arr[10]

    def test_get_uninitialized_item(self):
        self.assertEqual(self.str_arr[0], "")

    def test_repr(self):
        self.str_arr[0] = "hello"
        self.str_arr[1] = "world"
        self.assertEqual(repr(self.str_arr), '[\'hello\', \'world\']')

    def test_memory_cleanup(self):
        self.str_arr[0] = "hello"
        self.str_arr[1] = "world"
        del self.str_arr

    def test_iteration(self):
        """Test if iteration over StrArr works correctly"""
        #* Set up
        self.str_arr[0] = "alpha"
        self.str_arr[1] = "beta"
        self.str_arr[2] = "gamma"

        expected_values = ["alpha", "beta", "gamma"]
        iterator = iter(self.str_arr)

        for expected in expected_values:
            self.assertEqual(next(iterator), expected)  # Compare each yielded value

        # Ensure iteration stops correctly by calling `next()` past the last element
        with self.assertRaises(StopIteration):
            next(iterator)


    def test_empty_iteration(self):
        """Test iteration over an empty StrArr"""
        empty_arr = StrArr(5)  # No values set
        iterator = iter(empty_arr)

        # Ensure `StopIteration` is raised immediately
        with self.assertRaises(StopIteration):
            next(iterator)


    def test_partial_iteration(self):
        """Ensure iteration stops at the correct size"""
        self.str_arr[0] = "alpha"
        self.str_arr[1] = "beta"
        self.str_arr[2] = "gamma"
        self.str_arr[3] = "delta"

        expected_values = ["alpha", "beta", "gamma", "delta"]
        iterator = iter(self.str_arr)

        for expected in expected_values:
            self.assertEqual(next(iterator), expected)  # Corrected: No double next()

        # Ensure iteration stops correctly
        with self.assertRaises(StopIteration):
            next(iterator)



    

if __name__ == '__main__':
    unittest.main()