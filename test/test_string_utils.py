import os
import subprocess
import unittest

from mecab.utils.string_utils import tokenize, tokenize2, tokenizeCSV


class TestDarts(unittest.TestCase):

    def test_tokenize_csv(self):
        row = tokenizeCSV("*,*,*,*,*,*,*,*", ",", 512)
        self.assertEqual(row, ["*","*","*","*","*","*","*","*"])


if __name__ == '__main__':
    unittest.main()
