def reverse_string(s):
    return s[::-1]

# filename: test_reverse_string.py
import unittest

class TestReverseString(unittest.TestCase):
    def test_reverse_string(self):
        self.assertEqual(reverse_string(""), "")
        self.assertEqual(reverse_string("hello"), "olleh")
        self.assertEqual(reverse_string("Python"), "nohtyP")

if __name__ == "__main__":
    unittest.main()