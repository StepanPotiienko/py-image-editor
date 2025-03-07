import unittest
import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from file_processor import FileProcessor


class TestDefaultStringMethods(unittest.TestCase):
    def test_uppercase_convertion(self):
        self.assertEqual("foo".upper(), "FOO")


class TestFileProcessor(unittest.TestCase):
    processor = FileProcessor()

    def test_image_save(self):
        path = self.processor.open_image()
        self.assertTrue(isinstance(path, str))  # if the method fails it returns False


if __name__ == "__main__":
    unittest.main()
