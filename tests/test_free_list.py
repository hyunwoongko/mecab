import unittest

from mecab.nbest_generator import QueueElement
from mecab.utils.freelist import FreeList


class TestFreeList(unittest.TestCase):

    def test_generator(self):
        free_list = FreeList(int, size=4)
        print(free_list)
        output_of_alloc = free_list.alloc()
        print(free_list)
        print(output_of_alloc)

if __name__ == '__main__':
    test = TestFreeList()
    test.run()
