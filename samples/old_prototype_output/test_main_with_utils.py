import unittest

class TestMainWithUtils(unittest.TestCase):
    def test_main_with_utils(self):
        self.assertEqual(main(), None)

if __name__ == "__main__":
    unittest.main()