import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import os
import subprocess
import unittest

from mecab.utils.string_utils import tokenize, tokenize2, tokenizeCSV, escape_csv_element


class TestDarts(unittest.TestCase):

    def test_tokenize_csv(self):
        row = tokenizeCSV("*,,,*,*,*,*,*,*,*", 512)
        self.assertEqual(row, ["*", "", "", "*","*","*","*","*","*","*"])

        row = tokenizeCSV("DEFAULT,0,0,0,記号,一般,*,*,*,*,*", 5)
        self.assertEqual(row, ["DEFAULT","0","0","0","記号,一般,*,*,*,*,*"])
    
    def test_tokenize(self):
        row = tokenize("*,,*,*,*,*,*,*,*", ",")
        self.assertEqual(row, ["*","","*","*","*","*","*","*","*"])
    
    def test_tokenize2(self):
        row = tokenize2("*,,*,*,*,*,*,*,*", ",", 512)
        self.assertEqual(row, ["*","*","*","*","*","*","*","*"])
    
    def test_escape_csv_element(self):
        text, is_success = escape_csv_element(",")
        self.assertEqual(text, "\",\"")
        self.assertEqual(is_success, True)

if __name__ == '__main__':
    unittest.main()
