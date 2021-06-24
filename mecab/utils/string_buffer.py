import numpy as np

from mecab.common import *
# from mecab.utils.string_utils import itoa, uitoa, dtoa

DEFAULT_ALLOC_SIZE = BUF_SIZE


class StringBuffer:
    _size: int  # 현재 문자열 사이즈
    _alloc_size: int  # 메모리에 할당된 버퍼 사이즈
    _ptr: str  # 문자열
    _is_delete: bool
    _error: bool

    def __init__(self, _s: str = '', _l: int = 0):
        self._size = 0
        self._alloc_size = _l
        self._ptr = _s
        self._is_delete = _s == '' and _l == 0
        self._error = False

    def __del__(self):
        if self._is_delete:
            self._ptr = ''

    def reserve(self, length: int):
        """
        reserve the buffer for write text

        Args:
            length (int): reservation length

        Returns:
            (bool) success of reservation
        """

        if self._is_delete is False:
            self._error = self._size + length >= self._alloc_size
            return not self._error

        if self._size + length >= self._alloc_size:
            if self._alloc_size == 0:
                self._alloc_size = DEFAULT_ALLOC_SIZE
                self._ptr = ''

            len = self._size + length
            while True:
                self._alloc_size *= 2
                if len < self._alloc_size:
                    break

            self._ptr = self._ptr[:self._size]

        return True

    def write(self, string: str, length: int = None):
        if length is None:
            length = len(string)

        if self.reserve(length):
            self._ptr = f'{self._ptr[:self._size]}{string[:length]}{self._ptr[self._size + length:]}'
            self._size += length

        return self

    def __lshift__(self, other):
        if not isinstance(other, str):
            other = str(other)

        return self.write(other, len(other))

    def clear(self):
        self._size = 0
        self._ptr = ''

    def str(self):
        return 0 if self._error else self._ptr
