import unittest

class TestSuite(unittest.TestCase):
    def test_suite(self):
        self.assertEqual(test_main(), None)

if __name__ == "__main__":
    unittest.main()