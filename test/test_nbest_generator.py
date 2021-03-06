import unittest

from mecab.data_structure import Node
from mecab.nbest_generator import NBestGenerator


class TestNBestGenerator(unittest.TestCase):

    def test_generator(self):
        gen = NBestGenerator()
        eos = Node()
        gen.set(eos)


if __name__ == '__main__':
    test = TestNBestGenerator()
    test.run()
