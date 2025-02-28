import unittest

from src.utilities.data_structures.dictionary import Dictionary


class TestDictionary(unittest.TestCase):
    def setUp(self):
        """Set up a new dictionary before each test"""
        self.my_dict = Dictionary(capacity=5)  # Small size to force collisions
        # print(self.my_dict)

    def test_insert_and_get(self):
        """Test inserting and retrieving values"""
        self.my_dict.insert("Station A", 120)
        self.my_dict.insert("Station B", 230)

        self.assertEqual(self.my_dict.get("Station A"), 120)
        self.assertEqual(self.my_dict.get("Station B"), 230)

    def test_update_value(self):
        """Test updating an existing key"""
        self.my_dict.insert("Station A", 120)
        self.my_dict.insert("Station A", 150)  # Update value
        self.my_dict.insert("Station B", 230)
        self.my_dict.insert("Station C", 340)
        self.my_dict.insert("Station D", 450)
        self.my_dict.insert("Station E", 560)
        self.my_dict.insert("Station F", 670)  # Beyond initial size
        self.my_dict.insert("Station G", 780)  # Beyond initial size
        self.my_dict.insert("Station H", 890)  # Beyond initial size
        # print(self.my_dict)

        self.assertEqual(self.my_dict.get("Station A"), 150)
        self.assertEqual(self.my_dict.get("Station B"), 230)
        self.assertEqual(self.my_dict.get("Station C"), 340)
        self.assertEqual(self.my_dict.get("Station D"), 450)
        self.assertEqual(self.my_dict.get("Station E"), 560)
        self.assertEqual(self.my_dict.get("Station F"), 670)
        self.assertEqual(self.my_dict.get("Station G"), 780)
        self.assertEqual(self.my_dict.get("Station H"), 890)

    def test_collision_handling(self):
        """Test handling of collisions"""
        # These keys should hash to the same index in a small table
        self.my_dict.insert("Aa", 10)  # Different keys, but may collide
        self.my_dict.insert("BB", 20)  # Different keys, but may collide

        self.assertEqual(self.my_dict.get("Aa"), 10)
        self.assertEqual(self.my_dict.get("BB"), 20)

    def test_remove(self):
        """Test removing a key"""
        self.my_dict.insert("Station A", 120)
        self.my_dict.insert("Station B", 230)

        self.assertTrue(self.my_dict.remove("Station A"))
        with self.assertRaises(KeyError):
            _ = self.my_dict["Station A"]  # Should raise KeyError after deletion
        self.assertEqual(self.my_dict.get("Station B"), 230)  # Should still exist

    def test_remove_non_existent_key(self):
        """Test trying to remove a key that doesn't exist"""
        with self.assertRaises(KeyError):
            self.my_dict.remove("NonExistentKey")

    def test_get_non_existent_key(self):
        """Test retrieving a non-existent key"""
        with self.assertRaises(KeyError):
            _ = self.assertIsNone(self.my_dict.get("Station X"))

    def test_getitem_and_setitem(self):
        """Test the __getitem__ and __setitem__ methods for dict-like syntax"""
        self.my_dict["Station A"] = 120
        self.my_dict["Station B"] = 230

        self.assertEqual(self.my_dict["Station A"], 120)
        self.assertEqual(self.my_dict["Station B"], 230)

        # Test updating with bracket notation
        self.my_dict["Station A"] = 150
        self.assertEqual(self.my_dict["Station A"], 150)

        # Test KeyError for non-existent key
        with self.assertRaises(KeyError):
            _ = self.my_dict["NonExistentKey"]

    def test_contains(self):
        """Test the __contains__ method"""
        self.my_dict.insert("Station A", 120)

        self.assertTrue("Station A" in self.my_dict)
        self.assertFalse("Station X" in self.my_dict)

    def test_len(self):
        """Test if the __len__ method returns the correct number of items"""
        # Add several items
        self.my_dict.insert("Station A", 120)
        self.my_dict.insert("Station B", 230)
        self.my_dict.insert("Station C", 340)

        # len() should return the number of key-pair values
        self.assertEqual(len(self.my_dict), 3)

        # Remove an item
        self.my_dict.remove("Station B")

        # Length should decrease
        self.assertEqual(len(self.my_dict), 2)

    def test_iter(self):
        """Test the __iter__ method for iteration over keys"""
        keys = ["Station A", "Station B", "Station C"]
        values = [120, 230, 340]

        # Insert test data
        for k, v in zip(keys, values):
            self.my_dict[k] = v

        # Check dict comprehension works
        collected_items = {k: self.my_dict[k] for k in self.my_dict}
        expected_items = dict(zip(keys, values))
        self.assertEqual(collected_items, expected_items)


if __name__ == "__main__":
    unittest.main()
