import os
import unittest

from unittest.mock import patch

from src.utilities.data_getter.data_array import create_data_array
from src.utilities.data_structures.strArr import StrArr
from src.utilities.data_structures.objArr import ObjArr
from src.utilities.objects.route_list import k16

class TestFileHandling(unittest.TestCase):
    @patch('src.utilities.data_getter.data_array.create_data_array')
    def test_create_data_array_with_correct_file_path(self, mock):
        # Get the absolute path of the current directory (where test.py is located)
        test_directory = os.path.dirname(os.path.abspath(__file__))

        # Build the relative path from test.py to the 'data' folder and the CSV file
        relative_path = os.path.join(test_directory, "..", "data", "20250211.csv")

        # Convert the relative path to an absolute path
        absolute_route = os.path.abspath(relative_path)

        # Call the function with the absolute path
        route = k16()
        arr = create_data_array(file_name=absolute_route, route=route, start_time=1, end_time=2, filter_entrances=True)

        print("Data array:", arr)

        #*Verify that array is empty, since between 1 and 2, nobody entered the
        #*stations of the K16 route
        self.assertEqual(ObjArr(0), arr)

    @patch('src.utilities.data_getter.data_array.create_data_array')
    def test_file_path_construction(self, mock):
        # Test the correct construction of the file path
        test_directory = os.path.dirname(os.path.abspath(__file__))
        relative_path = os.path.join(test_directory, "..", "data", "20250211.csv")
        absolute_route = os.path.abspath(relative_path)

        # Check if the file path is as expected
        expected_path = os.path.join(test_directory, "..", "data", "20250211.csv")
        self.assertEqual(relative_path, expected_path)

        # Ensure the absolute path is constructed correctly
        self.assertEqual(absolute_route, os.path.abspath(expected_path))

if __name__ == '__main__':
    unittest.main()
