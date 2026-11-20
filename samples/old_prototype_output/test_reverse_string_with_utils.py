import unittest

class TestReverseStringWithUtils(unittest.TestCase):
    def test_reverse_string_with_utils(self):
        self.assertEqual(reverse_string(""), "")
        self.assertEqual(reverse_string("racecar"), "racecar")
        self.assertFalse(reverse_string("hello"))

if __name__ == "__main__":
    unittest.main()