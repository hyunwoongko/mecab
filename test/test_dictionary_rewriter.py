import os
import subprocess
import unittest

from mecab.utils.string_utils import tokenize, tokenize2, tokenizeCSV
from mecab.dictionary_rewriter import RewritePattern, RewriteRules, DictionaryRewriter, PosIDGenerator


class TestDarts(unittest.TestCase):

    def test_rewrite_pattern_set_pattern_sucess(self):
        rewrite_pattern = RewritePattern()
        is_success = rewrite_pattern.set_pattern("*,*,*,*,*,*,*,*", "$1,$2,$3,$4,$5,$6,$7,$8")
        self.assertEqual(rewrite_pattern.spat, ["*","*","*","*","*","*","*","*"])
        self.assertEqual(rewrite_pattern.dpat, ["$1","$2","$3","$4","$5","$6","$7","$8"])
        self.assertEqual(is_success, True)
        
    def test_rewrite_pattern_set_pattern_fail(self):
        rewrite_pattern = RewritePattern()
        is_success = rewrite_pattern.set_pattern("*,*,*,*,*,*,*,*", "$1,$2,$3,$4,$5,$6,$7")
        self.assertEqual(rewrite_pattern.spat, ["*","*","*","*","*","*","*","*"])
        self.assertEqual(rewrite_pattern.dpat, ["$1","$2","$3","$4","$5","$6","$7"])
        self.assertEqual(is_success, False)
    
    def test_rewrite_rules(self):
        rewrite_rule = RewriteRules()
        self.assertEqual(len(rewrite_rule), 0)
        rewrite_rule.append_rewrite_rule("*,*,*,*,*,*,*,*\t$1,$2,$3,$4,$5,$6,$7,$8")
        self.assertEqual(len(rewrite_rule), 1)
        self.assertEqual(rewrite_rule[-1].spat, ["*","*","*","*","*","*","*","*"])
        self.assertEqual(rewrite_pattern[-1].dpat, ["$1","$2","$3","$4","$5","$6","$7","$8"])

if __name__ == '__main__':
    unittest.main()
