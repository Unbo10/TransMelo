import unittest
from src.utilities.data_structures.lList import LList

class TestLinkedList(unittest.TestCase):

    def test_empty_list(self):
        test_llist = LList()
        self.assertEqual(len(test_llist), 0)
        self.assertEqual(str(test_llist), "[]")
        test_llist.append(1)
        self.assertEqual(len(test_llist), 1)
        self.assertEqual(str(test_llist), "[1]")

    def test_append_elements(self):
        test_llist = LList()
        for i in range(10):
            test_llist.append(i)
        self.assertEqual(len(test_llist), 10)
        self.assertEqual(test_llist[0], 0)
        self.assertEqual(test_llist[9], 9)

    def test_iteration(self):
        test_llist = LList()
        for i in range(10):
            test_llist.append(i)
        elements = [element for element in test_llist]
        self.assertEqual(elements, [i for i in range(10)])

    def test_set_item(self):
        test_llist = LList()
        for i in range(10):
            test_llist.append(i)
        test_llist[5] = 25
        self.assertEqual(test_llist[5], 25)
        with self.assertRaises(IndexError):
            test_llist[10] = 0

    def test_str_representation(self):
        test_llist = LList()
        for i in range(10):
            test_llist.append(i)
        self.assertEqual(str(test_llist), "[0 -> 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8 -> 9]")

if __name__ == "__main__":
    unittest.main()