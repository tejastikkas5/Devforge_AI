import unittest

class TestSuiteWithUtils(unittest.TestCase):
    def test_suite_with_utils(self):
        self.assertEqual(test_main_with_utils(), None)

if __name__ == "__main__":
    unittest.main()