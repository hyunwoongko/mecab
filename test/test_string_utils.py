import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import os
import subprocess
import unittest

from mecab.utils.string_utils import tokenize, tokenize2, tokenizeCSV


class TestDarts(unittest.TestCase):

    def test_tokenize_csv(self):
        row = tokenizeCSV("*,*,*,*,*,*,*,*", ",", 512)
        self.assertEqual(row, ["*","*","*","*","*","*","*","*"])
    
    def test_tokenize(self):
        row = tokenize("*,,*,*,*,*,*,*,*", ",")
        self.assertEqual(row, ["*","","*","*","*","*","*","*","*"])
    
    def tokenize2(self):
        row = tokenize("*,,*,*,*,*,*,*,*", ",", 512)
        self.assertEqual(row, ["*","*","*","*","*","*","*","*"])


if __name__ == '__main__':
    unittest.main()
