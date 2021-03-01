import os
import subprocess
import unittest

from mecab.darts import DoubleArrayTrieSystem


class TestDarts(unittest.TestCase):
    da = None

    @classmethod
    def setUpClass(cls) -> None:
        da = DoubleArrayTrieSystem()
        dic = [
            ('cat', 'c'),
            ('cat', 'a'),
            ('cat', 't'),
            ('car', 'ca'),
            ('car', 'r'),
            ('한국어', '한국'),
            ('한국어', '어')
        ]
        dic.sort()

        bsize = 0
        idx = 0

        prev = None
        str_list = []
        len_list = []
        val_list = []

        for i in range(0, len(dic)):
            if i != 0 and prev != dic[i][0]:
                str_list.append(dic[idx][0])
                len_list.append(len(dic[idx][0]))
                val_list.append(bsize + (idx << 8))
                bsize = 1
                idx = i
            else:
                bsize += 1
            prev = dic[i][0]

        str_list.append(dic[idx][0])
        len_list.append(len(dic[idx][0]))
        val_list.append(bsize + (idx << 8))

        da.build(str_list, len_list, val_list)
        cls.da = da

    def test_binary_object(self):
        c_test_path = os.path.join(os.path.dirname(__file__), 'mecab', 'run_c_test.sh')
        subprocess.run(['sh', c_test_path])
        bin_path = os.path.join(os.path.dirname(__file__), 'mecab', 'build', 'output.bin')
        c_array = self.da.load_c_binary(bin_path)
        self.assertEqual(c_array.shape[0], self.da.size_)

        for i in range(0, c_array.shape[0]):
            self.assertEqual(c_array[i], self.da.array[i])

    def test_trie(self):
        self.assertEqual({'value': 515, 'len': 3}, self.da.exact_match_search('cat'))
        self.assertEqual({'value': 1282, 'len': 9}, self.da.exact_match_search('한국어'))
        self.assertEqual({'value': -1, 'len': 0}, self.da.exact_match_search('영어'))
        self.assertEqual([], self.da.common_prefix_search('한글안녕', 10))


if __name__ == '__main__':
    unittest.main()
