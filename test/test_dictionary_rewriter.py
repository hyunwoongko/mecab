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
        self.assertEqual(len(dict_rewriter.unigram_rewrite), 2)
        self.assertEqual(dict_rewriter.unigram_rewrite[0].spat, ["*", "*", "*", "*", "*", "*", "*", "*"])
        self.assertEqual(dict_rewriter.unigram_rewrite[0].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "$7", "$8"])
        self.assertEqual(dict_rewriter.unigram_rewrite[1].spat, ["*", "*", "*", "*", "*", "*", "*"])
        self.assertEqual(dict_rewriter.unigram_rewrite[1].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "$7", "*"])

        self.assertEqual(len(dict_rewriter.left_rewrite), 41)
        self.assertEqual(dict_rewriter.left_rewrite[0].spat, ["(助詞|助動詞)", "*", "*", "*", "*", "*", "(ない|無い)"])
        self.assertEqual(dict_rewriter.left_rewrite[0].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "無い"])
        self.assertEqual(dict_rewriter.left_rewrite[1].spat, ["(助詞|助動詞)", "終助詞", "*", "*", "*", "*", "(よ|ヨ)"])
        self.assertEqual(dict_rewriter.left_rewrite[1].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "よ"])
        self.assertEqual(dict_rewriter.left_rewrite[2].spat, ["(助詞|助動詞)", "終助詞", "*", "*", "*", "*", "(な|なぁ|なあ|ナ)"])
        self.assertEqual(dict_rewriter.left_rewrite[2].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "な"])
        self.assertEqual(dict_rewriter.left_rewrite[3].spat, ["(助詞|助動詞)", "終助詞", "*", "*", "*", "*", "(ね|ねぇ|ねえ|ねェ|ねエ|ねっ|ねッ|ネ)"])
        self.assertEqual(dict_rewriter.left_rewrite[3].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "ね"])
        self.assertEqual(dict_rewriter.left_rewrite[4].spat, ["(助詞|助動詞)", "接続助詞", "*", "*", "*", "*", "(て|ちゃ|ちゃあ)"])
        self.assertEqual(dict_rewriter.left_rewrite[4].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "て"])
        self.assertEqual(dict_rewriter.left_rewrite[5].spat, ["(助詞|助動詞)", "接続助詞", "*", "*", "*", "*", "(ちゃあ|ちゃ)"])
        self.assertEqual(dict_rewriter.left_rewrite[5].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "ちゃ"])
        self.assertEqual(dict_rewriter.left_rewrite[6].spat, ["(助詞|助動詞)", "接続助詞", "*", "*", "*", "*", "(で|じゃ)"])
        self.assertEqual(dict_rewriter.left_rewrite[6].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "で"])
        self.assertEqual(dict_rewriter.left_rewrite[7].spat, ["(助詞|助動詞)", "接続助詞", "*", "*", "*", "*", "(けど|けれど)"])
        self.assertEqual(dict_rewriter.left_rewrite[7].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "けれど"])
        self.assertEqual(dict_rewriter.left_rewrite[8].spat, ["(助詞|助動詞)", "*", "*", "*", "*", "*", "*"])
        self.assertEqual(dict_rewriter.left_rewrite[8].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "$7"])
        self.assertEqual(dict_rewriter.left_rewrite[9].spat, ["記号", "(句点|括弧閉|括弧開)", "*", "*", "*", "*", "*"])
        self.assertEqual(dict_rewriter.left_rewrite[9].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "BOS/EOS"])
        self.assertEqual(dict_rewriter.left_rewrite[10].spat, ["BOS/EOS", "*", "*", "*", "*", "*", "*"])
        self.assertEqual(dict_rewriter.left_rewrite[10].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "BOS/EOS"])
        self.assertEqual(dict_rewriter.left_rewrite[11].spat, ["動詞", "自立", "*", "*", "*", "*", "(行う|行なう)"])
        self.assertEqual(dict_rewriter.left_rewrite[11].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "行う"])
        self.assertEqual(dict_rewriter.left_rewrite[12].spat, ["動詞", "自立", "*", "*", "*", "*", "(いう|言う|云う)"])
        self.assertEqual(dict_rewriter.left_rewrite[12].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "言う"])
        self.assertEqual(dict_rewriter.left_rewrite[13].spat, ["動詞", "自立", "*", "*", "*", "*", "(いく|行く)"])
        self.assertEqual(dict_rewriter.left_rewrite[13].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "行く"])
        self.assertEqual(dict_rewriter.left_rewrite[14].spat, ["動詞", "自立", "*", "*", "*", "*", "する"])
        self.assertEqual(dict_rewriter.left_rewrite[14].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "する"])
        self.assertEqual(dict_rewriter.left_rewrite[15].spat, ["動詞", "自立", "*", "*", "*", "*", "*"])
        self.assertEqual(dict_rewriter.left_rewrite[15].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "*"])
        self.assertEqual(dict_rewriter.left_rewrite[16].spat, ["動詞", "非自立", "*", "*", "*", "*", "(ある|おる|かかる|きる|なる|まいる|まわる|やる|回る|終わる|切る|参る|いらっしゃる|らっしゃる|なさる|る|もらう|しまう|続く|いく|ゆく|行く|く|くれる|おく|する)"])
        self.assertEqual(dict_rewriter.left_rewrite[16].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "$7"])
        self.assertEqual(dict_rewriter.left_rewrite[17].spat, ["動詞", "非自立", "*", "*", "*", "*", "(来る|くる)"])
        self.assertEqual(dict_rewriter.left_rewrite[17].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "来る"])
        self.assertEqual(dict_rewriter.left_rewrite[18].spat, ["動詞", "非自立", "*", "*", "*", "*", "(ぬく|抜く)"])
        self.assertEqual(dict_rewriter.left_rewrite[18].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "抜く"])
        self.assertEqual(dict_rewriter.left_rewrite[19].spat, ["動詞", "非自立", "*", "*", "*", "*", "(頂く|いただく)"])
        self.assertEqual(dict_rewriter.left_rewrite[19].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "頂く"])
        self.assertEqual(dict_rewriter.left_rewrite[20].spat, ["動詞", "非自立", "*", "*", "*", "*", "(いたす|致す)"])
        self.assertEqual(dict_rewriter.left_rewrite[20].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "致す"])
        self.assertEqual(dict_rewriter.left_rewrite[21].spat, ["動詞", "非自立", "*", "*", "*", "*", "(だす|出す)"])
        self.assertEqual(dict_rewriter.left_rewrite[21].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "出す"])
        self.assertEqual(dict_rewriter.left_rewrite[22].spat, ["動詞", "非自立", "*", "*", "*", "*", "(つくす|尽くす|尽す)"])
        self.assertEqual(dict_rewriter.left_rewrite[22].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "尽くす"])
        self.assertEqual(dict_rewriter.left_rewrite[23].spat, ["動詞", "非自立", "*", "*", "*", "*", "(直す|なおす)"])
        self.assertEqual(dict_rewriter.left_rewrite[23].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "直す"])
        self.assertEqual(dict_rewriter.left_rewrite[24].spat, ["動詞", "非自立", "*", "*", "*", "*", "(込む|こむ)"])
        self.assertEqual(dict_rewriter.left_rewrite[24].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "込む"])
        self.assertEqual(dict_rewriter.left_rewrite[25].spat, ["動詞", "非自立", "*", "*", "*", "*", "(くださる|下さる)"])
        self.assertEqual(dict_rewriter.left_rewrite[25].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "下さる"])
        self.assertEqual(dict_rewriter.left_rewrite[26].spat, ["動詞", "非自立", "*", "*", "*", "*", "(合う|あう)"])
        self.assertEqual(dict_rewriter.left_rewrite[26].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "合う"])
        self.assertEqual(dict_rewriter.left_rewrite[27].spat, ["動詞", "非自立", "*", "*", "*", "*", "*"])
        self.assertEqual(dict_rewriter.left_rewrite[27].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "*"])
        self.assertEqual(dict_rewriter.left_rewrite[28].spat, ["形容詞", "*", "*", "*", "*", "*", "(ない|無い|いい|らしい)"])
        self.assertEqual(dict_rewriter.left_rewrite[28].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "無い"])
        self.assertEqual(dict_rewriter.left_rewrite[29].spat, ["形容詞", "接尾", "*", "*", "*", "*", "(臭い|くさい)"])
        self.assertEqual(dict_rewriter.left_rewrite[29].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "臭い"])
        self.assertEqual(dict_rewriter.left_rewrite[30].spat, ["形容詞", "接尾", "*", "*", "*", "*", "(欲しい|ほしい)"])
        self.assertEqual(dict_rewriter.left_rewrite[30].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "欲しい"])
        self.assertEqual(dict_rewriter.left_rewrite[31].spat, ["形容詞", "接尾", "*", "*", "*", "*", "(ったらしい|たらしい|っぽい|ぽい)"])
        self.assertEqual(dict_rewriter.left_rewrite[31].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "たらしい"])
        self.assertEqual(dict_rewriter.left_rewrite[32].spat, ["形容詞", "接尾", "*", "*", "*", "*", "*"])
        self.assertEqual(dict_rewriter.left_rewrite[32].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "*"])
        self.assertEqual(dict_rewriter.left_rewrite[33].spat, ["形容詞", "非自立", "*", "*", "*", "*", "(難い|がたい|づらい|にくい|やすい)"])
        self.assertEqual(dict_rewriter.left_rewrite[33].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "難い"])
        self.assertEqual(dict_rewriter.left_rewrite[34].spat, ["形容詞", "非自立", "*", "*", "*", "*", "(よい|良い)"])
        self.assertEqual(dict_rewriter.left_rewrite[34].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "良い"])
        self.assertEqual(dict_rewriter.left_rewrite[35].spat, ["形容詞", "非自立", "*", "*", "*", "*", "(欲しい|ほしい)"])
        self.assertEqual(dict_rewriter.left_rewrite[35].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "欲しい"])
        self.assertEqual(dict_rewriter.left_rewrite[36].spat, ["形容詞", "非自立", "*", "*", "*", "*", "(じまう|じゃう|でく|どく|でる|どる)"])
        self.assertEqual(dict_rewriter.left_rewrite[36].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "でる"])
        self.assertEqual(dict_rewriter.left_rewrite[37].spat, ["形容詞", "非自立", "*", "*", "*", "*", "(ちまう|ちゃう|てく|とく|てる|とる)"])
        self.assertEqual(dict_rewriter.left_rewrite[37].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "てる"])
        self.assertEqual(dict_rewriter.left_rewrite[38].spat, ["形容詞", "非自立", "*", "*", "*", "*", "*"])
        self.assertEqual(dict_rewriter.left_rewrite[38].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "*"])
        self.assertEqual(dict_rewriter.left_rewrite[39].spat, ["接続詞", "*", "*", "*", "*", "*", "(及び|および|あるいは|或いは|或は|または|又は|ないし|ならびに|並びに|もしくは|若しくは)"])
        self.assertEqual(dict_rewriter.left_rewrite[39].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "および"])
        self.assertEqual(dict_rewriter.left_rewrite[40].spat, ["*", "*", "*", "*", "*", "*", "*"])
        self.assertEqual(dict_rewriter.left_rewrite[40].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "*"])

        self.assertEqual(len(dict_rewriter.right_rewrite), 41)
        self.assertEqual(dict_rewriter.right_rewrite[0].spat, ["(助詞|助動詞)", "*", "*", "*", "*", "*", "(ない|無い)"])
        self.assertEqual(dict_rewriter.right_rewrite[0].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "無い"])
        self.assertEqual(dict_rewriter.right_rewrite[1].spat, ["(助詞|助動詞)", "終助詞", "*", "*", "*", "*", "(よ|ヨ)"])
        self.assertEqual(dict_rewriter.right_rewrite[1].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "よ"])
        self.assertEqual(dict_rewriter.right_rewrite[2].spat, ["(助詞|助動詞)", "終助詞", "*", "*", "*", "*", "(な|なぁ|なあ|ナ)"])
        self.assertEqual(dict_rewriter.right_rewrite[2].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "な"])
        self.assertEqual(dict_rewriter.right_rewrite[3].spat, ["(助詞|助動詞)", "終助詞", "*", "*", "*", "*", "(ね|ねぇ|ねえ|ねェ|ねエ|ねっ|ねッ|ネ)"])
        self.assertEqual(dict_rewriter.right_rewrite[3].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "ね"])
        self.assertEqual(dict_rewriter.right_rewrite[4].spat, ["(助詞|助動詞)", "接続助詞", "*", "*", "*", "*", "(て|ちゃ|ちゃあ)"])
        self.assertEqual(dict_rewriter.right_rewrite[4].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "て"])
        self.assertEqual(dict_rewriter.right_rewrite[5].spat, ["(助詞|助動詞)", "接続助詞", "*", "*", "*", "*", "(ちゃあ|ちゃ)"])
        self.assertEqual(dict_rewriter.right_rewrite[5].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "ちゃ"])
        self.assertEqual(dict_rewriter.right_rewrite[6].spat, ["(助詞|助動詞)", "接続助詞", "*", "*", "*", "*", "(で|じゃ)"])
        self.assertEqual(dict_rewriter.right_rewrite[6].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "で"])
        self.assertEqual(dict_rewriter.right_rewrite[7].spat, ["(助詞|助動詞)", "接続助詞", "*", "*", "*", "*", "(けど|けれど)"])
        self.assertEqual(dict_rewriter.right_rewrite[7].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "けれど"])
        self.assertEqual(dict_rewriter.right_rewrite[8].spat, ["(助詞|助動詞)", "*", "*", "*", "*", "*", "*"])
        self.assertEqual(dict_rewriter.right_rewrite[8].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "$7"])
        self.assertEqual(dict_rewriter.right_rewrite[9].spat, ["記号", "(句点|括弧閉|括弧開)", "*", "*", "*", "*", "*"])
        self.assertEqual(dict_rewriter.right_rewrite[9].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "BOS/EOS"])
        self.assertEqual(dict_rewriter.right_rewrite[10].spat, ["BOS/EOS", "*", "*", "*", "*", "*", "*"])
        self.assertEqual(dict_rewriter.right_rewrite[10].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "BOS/EOS"])
        self.assertEqual(dict_rewriter.right_rewrite[11].spat, ["動詞", "自立", "*", "*", "*", "*", "(行う|行なう)"])
        self.assertEqual(dict_rewriter.right_rewrite[11].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "行う"])
        self.assertEqual(dict_rewriter.right_rewrite[12].spat, ["動詞", "自立", "*", "*", "*", "*", "(いう|言う|云う)"])
        self.assertEqual(dict_rewriter.right_rewrite[12].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "言う"])
        self.assertEqual(dict_rewriter.right_rewrite[13].spat, ["動詞", "自立", "*", "*", "*", "*", "(いく|行く)"])
        self.assertEqual(dict_rewriter.right_rewrite[13].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "行く"])
        self.assertEqual(dict_rewriter.right_rewrite[14].spat, ["動詞", "自立", "*", "*", "*", "*", "する"])
        self.assertEqual(dict_rewriter.right_rewrite[14].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "する"])
        self.assertEqual(dict_rewriter.right_rewrite[15].spat, ["動詞", "自立", "*", "*", "*", "*", "*"])
        self.assertEqual(dict_rewriter.right_rewrite[15].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "*"])
        self.assertEqual(dict_rewriter.right_rewrite[16].spat, ["動詞", "非自立", "*", "*", "*", "*", "(ある|おる|かかる|きる|なる|まいる|まわる|やる|回る|終わる|切る|参る|いらっしゃる|らっしゃる|なさる|る|もらう|しまう|続く|いく|ゆく|行く|く|くれる|おく|する)"])
        self.assertEqual(dict_rewriter.right_rewrite[16].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "$7"])
        self.assertEqual(dict_rewriter.right_rewrite[17].spat, ["動詞", "非自立", "*", "*", "*", "*", "(来る|くる)"])
        self.assertEqual(dict_rewriter.right_rewrite[17].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "来る"])
        self.assertEqual(dict_rewriter.right_rewrite[18].spat, ["動詞", "非自立", "*", "*", "*", "*", "(ぬく|抜く)"])
        self.assertEqual(dict_rewriter.right_rewrite[18].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "抜く"])
        self.assertEqual(dict_rewriter.right_rewrite[19].spat, ["動詞", "非自立", "*", "*", "*", "*", "(頂く|いただく)"])
        self.assertEqual(dict_rewriter.right_rewrite[19].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "頂く"])
        self.assertEqual(dict_rewriter.right_rewrite[20].spat, ["動詞", "非自立", "*", "*", "*", "*", "(いたす|致す)"])
        self.assertEqual(dict_rewriter.right_rewrite[20].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "致す"])
        self.assertEqual(dict_rewriter.right_rewrite[21].spat, ["動詞", "非自立", "*", "*", "*", "*", "(だす|出す)"])
        self.assertEqual(dict_rewriter.right_rewrite[21].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "出す"])
        self.assertEqual(dict_rewriter.right_rewrite[22].spat, ["動詞", "非自立", "*", "*", "*", "*", "(つくす|尽くす|尽す)"])
        self.assertEqual(dict_rewriter.right_rewrite[22].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "尽くす"])
        self.assertEqual(dict_rewriter.right_rewrite[23].spat, ["動詞", "非自立", "*", "*", "*", "*", "(直す|なおす)"])
        self.assertEqual(dict_rewriter.right_rewrite[23].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "直す"])
        self.assertEqual(dict_rewriter.right_rewrite[24].spat, ["動詞", "非自立", "*", "*", "*", "*", "(込む|こむ)"])
        self.assertEqual(dict_rewriter.right_rewrite[24].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "込む"])
        self.assertEqual(dict_rewriter.right_rewrite[25].spat, ["動詞", "非自立", "*", "*", "*", "*", "(くださる|下さる)"])
        self.assertEqual(dict_rewriter.right_rewrite[25].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "下さる"])
        self.assertEqual(dict_rewriter.right_rewrite[26].spat, ["動詞", "非自立", "*", "*", "*", "*", "(合う|あう)"])
        self.assertEqual(dict_rewriter.right_rewrite[26].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "合う"])
        self.assertEqual(dict_rewriter.right_rewrite[27].spat, ["動詞", "非自立", "*", "*", "*", "*", "*"])
        self.assertEqual(dict_rewriter.right_rewrite[27].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "*"])
        self.assertEqual(dict_rewriter.right_rewrite[28].spat, ["形容詞", "*", "*", "*", "*", "*", "(ない|無い|いい|らしい)"])
        self.assertEqual(dict_rewriter.right_rewrite[28].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "無い"])
        self.assertEqual(dict_rewriter.right_rewrite[29].spat, ["形容詞", "接尾", "*", "*", "*", "*", "(臭い|くさい)"])
        self.assertEqual(dict_rewriter.right_rewrite[29].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "臭い"])
        self.assertEqual(dict_rewriter.right_rewrite[30].spat, ["形容詞", "接尾", "*", "*", "*", "*", "(欲しい|ほしい)"])
        self.assertEqual(dict_rewriter.right_rewrite[30].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "欲しい"])
        self.assertEqual(dict_rewriter.right_rewrite[31].spat, ["形容詞", "接尾", "*", "*", "*", "*", "(ったらしい|たらしい|っぽい|ぽい)"])
        self.assertEqual(dict_rewriter.right_rewrite[31].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "たらしい"])
        self.assertEqual(dict_rewriter.right_rewrite[32].spat, ["形容詞", "接尾", "*", "*", "*", "*", "*"])
        self.assertEqual(dict_rewriter.right_rewrite[32].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "*"])
        self.assertEqual(dict_rewriter.right_rewrite[33].spat, ["形容詞", "非自立", "*", "*", "*", "*", "(難い|がたい|づらい|にくい|やすい)"])
        self.assertEqual(dict_rewriter.right_rewrite[33].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "難い"])
        self.assertEqual(dict_rewriter.right_rewrite[34].spat, ["形容詞", "非自立", "*", "*", "*", "*", "(よい|良い)"])
        self.assertEqual(dict_rewriter.right_rewrite[34].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "良い"])
        self.assertEqual(dict_rewriter.right_rewrite[35].spat, ["形容詞", "非自立", "*", "*", "*", "*", "(欲しい|ほしい)"])
        self.assertEqual(dict_rewriter.right_rewrite[35].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "欲しい"])
        self.assertEqual(dict_rewriter.right_rewrite[36].spat, ["形容詞", "非自立", "*", "*", "*", "*", "(じまう|じゃう|でく|どく|でる|どる)"])
        self.assertEqual(dict_rewriter.right_rewrite[36].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "でる"])
        self.assertEqual(dict_rewriter.right_rewrite[37].spat, ["形容詞", "非自立", "*", "*", "*", "*", "(ちまう|ちゃう|てく|とく|てる|とる)"])
        self.assertEqual(dict_rewriter.right_rewrite[37].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "てる"])
        self.assertEqual(dict_rewriter.right_rewrite[38].spat, ["形容詞", "非自立", "*", "*", "*", "*", "*"])
        self.assertEqual(dict_rewriter.right_rewrite[38].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "*"])
        self.assertEqual(dict_rewriter.right_rewrite[39].spat, ["接続詞", "*", "*", "*", "*", "*", "(及び|および|あるいは|或いは|或は|または|又は|ないし|ならびに|並びに|もしくは|若しくは)"])
        self.assertEqual(dict_rewriter.right_rewrite[39].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "および"])
        self.assertEqual(dict_rewriter.right_rewrite[40].spat, ["*", "*", "*", "*", "*", "*", "*"])
        self.assertEqual(dict_rewriter.right_rewrite[40].dpat, ["$1", "$2", "$3", "$4", "$5", "$6", "*"])

        feature = "BOS/EOS,*,*,*,*,*,*,*,*"
        feature_set = FeatureSet("", "", "")

        is_success = dict_rewriter.rewrite2(feature, feature_set)
        self.assertEqual(is_success, True)
        
    

if __name__ == '__main__':
    unittest.main()
