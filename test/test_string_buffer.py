import unittest

from mecab.nbest_generator import QueueElement
from mecab.utils.string_buffer import StringBuffer, DEFAULT_ALLOC_SIZE


class TestStringBuffer(unittest.TestCase):

    def test_not_limit_size(self):
        string_buffer = StringBuffer()
        self.assertEqual(True, string_buffer._is_delete)

        self.assertEqual(True, string_buffer.reserve(10))
        self.assertEqual(DEFAULT_ALLOC_SIZE * 2, string_buffer._alloc_size)
        self.assertEqual('', string_buffer.str())

        string_buffer.write("hi")
        self.assertEqual("hi", string_buffer.str())
        self.assertEqual(2, string_buffer._size)

        string_buffer.write("test text", 4)
        self.assertEqual("hitest", string_buffer.str())
        self.assertEqual(6, string_buffer._size)

        string_buffer = string_buffer << " t2"
        self.assertEqual("hitest t2", string_buffer.str())
        self.assertEqual(9, string_buffer._size)

        string_buffer = string_buffer << " t3" << "t4"
        self.assertEqual("hitest t2 t3t4", string_buffer.str())
        self.assertEqual(14, string_buffer._size)

        string_buffer.clear()
        self.assertEqual('', string_buffer.str())

        string_buffer << "感動詞,*,*,*,*,*,*,*" << ' ' << 7 << '\0'
        self.assertEqual('感動詞,*,*,*,*,*,*,* 7\0', string_buffer.str())

        self.assertEqual(string_buffer._size, 20)

        string_buffer.clear()
        string_buffer = string_buffer << "U"
        self.assertEqual('U', string_buffer.str())
        self.assertEqual(string_buffer._size, 1)

        string_buffer << 1
        self.assertEqual('U1', string_buffer.str())
        self.assertEqual(2, string_buffer._size)

        string_buffer << ":"
        self.assertEqual('U1:', string_buffer.str())
        self.assertEqual(string_buffer._size, 3)

        string_buffer << "感動詞"
        self.assertEqual('U1:感動詞', string_buffer.str())
        self.assertEqual(string_buffer._size, 6)

        # \0은 어떻게 처리할 것인가
        string_buffer << "\0"
        self.assertEqual(string_buffer.str(), 'U1:感動詞\0')
        self.assertEqual(7, string_buffer._size)

    def test_limit_size(self):
        string_buffer = StringBuffer(_s='hi', _l=10)
        self.assertEqual(False, string_buffer._is_delete)
        self.assertEqual(10, string_buffer._alloc_size)
        self.assertEqual('hi', string_buffer.str())

        string_buffer << "10 times"
        self.assertEqual('10 times', string_buffer.str())
        self.assertEqual(10, string_buffer._alloc_size)
        self.assertEqual(8, string_buffer._size)

        string_buffer << "over"
        self.assertEqual(0, string_buffer.str())
        self.assertEqual(10, string_buffer._alloc_size)
        self.assertEqual(8, string_buffer._size)


if __name__ == '__main__':
    test = TestStringBuffer()
    test.run()

