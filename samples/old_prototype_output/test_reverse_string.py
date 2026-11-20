import unittest

class TestReverseString(unittest.TestCase):
    def test_reverse_string(self):
        self.assertEqual(reverse_string(""), "")
        self.assertEqual(reverse_string("hello"), "olleh")
        self.assertEqual(reverse_string("Python"), "nohtyP")

if __name__ == "__main__":
    unittest.main()

# filename: test_utils.py
import unittest

class TestUtils(unittest.TestCase):
    def test_is_palindrome(self):
        self.assertTrue(is_palindrome(""))
        self.assertTrue(is_palindrome("racecar"))
        self.assertFalse(is_palindrome("hello"))

if __name__ == "__main__":
    unittest.main()

# filename: test_main.py
import unittest

class TestMain(unittest.TestCase):
    def test_main(self):
        self.assertEqual(main(), None)

if __name__ == "__main__":
    unittest.main()

# filename: test_main_with_utils.py
import unittest

class TestMainWithUtils(unittest.TestCase):
    def test_main_with_utils(self):
        self.assertEqual(main(), None)

if __name__ == "__main__":
    unittest.main()

# filename: test_reverse_string_with_utils.py
import unittest

class TestReverseStringWithUtils(unittest.TestCase):
    def test_reverse_string_with_utils(self):
        self.assertEqual(reverse_string(""), "")
        self.assertEqual(reverse_string("racecar"), "racecar")
        self.assertFalse(reverse_string("hello"))

if __name__ == "__main__":
    unittest.main()

# filename: test_suite_with_utils.py
import unittest

class TestSuiteWithUtils(unittest.TestCase):
    def test_suite_with_utils(self):
        self.assertEqual(test_main_with_utils(), None)

if __name__ == "__main__":
    unittest.main()