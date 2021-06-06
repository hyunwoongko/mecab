import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import subprocess
import unittest

from mecab.utils.string_utils import tokenize, tokenize2, tokenizeCSV
from mecab.dictionary_rewriter import RewritePattern, RewriteRules, DictionaryRewriter, PosIDGenerator, FeatureSet


class TestDarts(unittest.TestCase):

    def test_rewrite_pattern_set_pattern_sucess(self):
        rewrite_pattern = RewritePattern()
        is_success = rewrite_pattern.set_pattern("*,*,*,*,*,*,*,*", "$1,$2,$3,$4,$5,$6,$7,$8")
        self.assertEqual(rewrite_pattern.spat, ["*","*","*","*","*","*","*","*"])
        self.assertEqual(rewrite_pattern.dpat, ["$1","$2","$3","$4","$5","$6","$7","$8"])
        self.assertEqual(is_success, True)
    
    def test_rewrite_rules(self):
        rewrite_rule = RewriteRules()
        self.assertEqual(len(rewrite_rule), 0)
        rewrite_rule.append_rewrite_rule("*,*,*,*,*,*,*,* \t$1,$2,$3,$4,$5,$6,$7,$8")
        self.assertEqual(len(rewrite_rule), 1)
        self.assertEqual(rewrite_rule[-1].spat, ["*","*","*","*","*","*","*","*"])
        self.assertEqual(rewrite_rule[-1].dpat, ["$1","$2","$3","$4","$5","$6","$7","$8"])
    
    def test_PosIDGenerator(self):
        posid = PosIDGenerator()
        test_file_path = os.path.join(
            os.path.dirname(__file__),
            "test_data",
            "cost_train",
            "seed",
            "pos-id.def"
        )

        posid.open(test_file_path)
        test_unk_file_path = os.path.join(
            os.path.dirname(__file__),
            "test_data",
            "cost_train",
            "seed",
            "unk.def"
        )
        with open(test_unk_file_path, 'r') as f:
            for row in f.read():
                features = tokenizeCSV(row, 5)
                if len(features) < 5:
                    continue

                output = posid.id(features[4])
                self.assertEqual(output, 1)

    def test_rewrite(self):
        size = 7
        input = [
            "記号",
            "一般",
            "*",
            "*",
            "*",
            "*",
            "*",
        ]

        rewrite_rule = RewriteRules()
        new_item = RewritePattern()
        new_item.set_pattern("*", "1")
        rewrite_rule.append(new_item)

        output, is_success = rewrite_rule.rewrite(size, input)
        self.assertEqual(is_success, True)
        self.assertEqual(output, "1")
    
    def test_dictionary_rewriter(self):
        test_rewrite_file_path = os.path.join(
            os.path.dirname(__file__),
            "dictionary_test",
            "rewrite.def"
        )
        print(test_rewrite_file_path)
        dict_rewriter = DictionaryRewriter()
        dict_rewriter.open(test_rewrite_file_path)
        self.assertEqual(dict_rewriter.unigram_rewrite[0].spat, ["*","*","*","*","*","*","*","*"])
        self.assertEqual(dict_rewriter.unigram_rewrite[0].dpat, ["$1","$2","$3","$4","$5","$6","$7","$8"])
        self.assertEqual(dict_rewriter.unigram_rewrite[1].spat, ["*","*","*","*","*","*","*"])
        self.assertEqual(dict_rewriter.unigram_rewrite[1].dpat, ["$1","$2","$3","$4","$5","$6","$7","*"])

        feature = "BOS/EOS,*,*,*,*,*,*,*,*"
        feature_set = FeatureSet("", "", "")

        is_success = dict_rewriter.rewrite2(feature, feature_set)
        self.assertEqual(is_success, True)
    

if __name__ == '__main__':
    unittest.main()
