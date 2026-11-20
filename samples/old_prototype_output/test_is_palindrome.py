import unittest

class TestIsPalindrome(unittest.TestCase):
    def test_is_palindrome(self):
        # Test with a normal palindrome
        self.assertTrue(is_palindrome("A man a plan a canal Panama"))

        # Test with a normal palindrome with spaces
        self.assertTrue(is_palindrome("No lemon, no melon"))

        # Test with a palindrome that is not a palindrome
        self.assertFalse(is_palindrome("Hello, World!"))

        # Test with a non-string input
        self.assertRaises(TypeError, is_palindrome, 123)

if __name__ == "__main__":
    unittest.main()