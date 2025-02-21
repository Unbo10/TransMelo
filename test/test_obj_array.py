import unittest

from src.utilities.data_structures import ObjArr, IntArr

class TestObjArr(unittest.TestCase):

    def test_empty_obj_arr(self):
        # Test creating an empty ObjArr
        empty_arr = ObjArr()
        self.assertEqual(len(empty_arr), 0)  # Assert the size of the empty ObjArr is 0
        self.assertEqual(empty_arr.__repr__(), "[]")  # Assert the correct string representation

    def test_obj_arr_with_capacity(self):
        # Test creating an ObjArr with a specific size
        arr_of_arrs = ObjArr(3)
        self.assertEqual(len(arr_of_arrs), 3)  # Assert the size of ObjArr is 3
        self.assertEqual(arr_of_arrs.__repr__(), "[None, None, None]")  # Assert the initial state (None)

    def test_nested_array_assignment(self):
        # Test assigning IntArr objects to ObjArr
        arr_of_arrs = ObjArr(3)
        for i in range(3):
            temp = IntArr(3)
            for j in range(3):
                temp[j] = j + i  # Fill the IntArr with values
            arr_of_arrs[i] = temp  # Assign the IntArr to the ObjArr
        # Check that the elements were assigned correctly
        self.assertEqual(arr_of_arrs[0][0], 0)
        self.assertEqual(arr_of_arrs[1][0], 1)
        self.assertEqual(arr_of_arrs[2][0], 2)
        self.assertEqual(arr_of_arrs[0][1], 1)
        self.assertEqual(arr_of_arrs[1][1], 2)
        self.assertEqual(arr_of_arrs[2][1], 3)

    def test_obj_arr_repr(self):
        # Test the string representation of ObjArr with nested arrays
        arr_of_arrs = ObjArr(3)
        for i in range(3):
            temp = IntArr(3)
            for j in range(3):
                temp[j] = j + i
            arr_of_arrs[i] = temp
        # Check the string representation of ObjArr after assignment
        expected_repr = "[[0, 1, 2], [1, 2, 3], [2, 3, 4]]"
        self.assertEqual(arr_of_arrs.__repr__(), expected_repr)

    def test_obj_arr_iteration(self):
        # Test the iteration over ObjArr
        arr_of_arrs = ObjArr(3)
        for i in range(3):
            temp = IntArr(3)
            for j in range(3):
                temp[j] = j + i
            arr_of_arrs[i] = temp
        
        # Collect elements using iteration
        collected_elements = [elem for elem in arr_of_arrs]
        
        # Check that the elements were iterated correctly
        self.assertEqual(collected_elements[0].__repr__(), "[0, 1, 2]")
        self.assertEqual(collected_elements[1].__repr__(), "[1, 2, 3]")
        self.assertEqual(collected_elements[2].__repr__(), "[2, 3, 4]")

if __name__ == '__main__':
    unittest.main()
