def is_palindrome(s):
    return s == s[::-1]

# filename: test_utils.py
import unittest

class TestUtils(unittest.TestCase):
    def test_is_palindrome(self):
        self.assertTrue(is_palindrome(""))
        self.assertTrue(is_palindrome("racecar"))
        self.assertFalse(is_palindrome("hello"))

if __name__ == "__main__":
    unittest.main()