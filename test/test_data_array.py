import unittest
from unittest.mock import patch
import os
from src.utilities.data_getter.data_array import create_data_array

class TestFileHandling(unittest.TestCase):
    @patch('src.utilities.data_getter.data_array.create_data_array')
    def test_create_data_array_with_correct_file_path(self, mock_create_data_array):
        # Get the absolute path of the current directory (where test.py is located)
        directorio_test = os.path.dirname(os.path.abspath(__file__))

        # Build the relative path from test.py to the 'data' folder and the CSV file
        ruta_relativa = os.path.join(directorio_test, "..", "data", "20250211.csv")

        # Convert the relative path to an absolute path
        ruta_absoluta = os.path.abspath(ruta_relativa)

        # Call the function with the absolute path
        create_data_array(file_name=ruta_absoluta)

        # Verify that create_data_array was called with the correct absolute file path
        mock_create_data_array.assert_called_once_with(file_name=ruta_absoluta)

    @patch('src.utilities.data_getter.data_array.create_data_array')
    def test_file_path_construction(self, mock_create_data_array):
        # Test the correct construction of the file path
        directorio_test = os.path.dirname(os.path.abspath(__file__))
        ruta_relativa = os.path.join(directorio_test, "..", "data", "20250211.csv")
        ruta_absoluta = os.path.abspath(ruta_relativa)

        # Check if the file path is as expected
        expected_path = os.path.join(directorio_test, "..", "data", "20250211.csv")
        self.assertEqual(ruta_relativa, expected_path)

        # Ensure the absolute path is constructed correctly
        self.assertEqual(ruta_absoluta, os.path.abspath(expected_path))

if __name__ == '__main__':
    unittest.main()
