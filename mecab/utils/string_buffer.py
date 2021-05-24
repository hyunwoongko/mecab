import numpy as np

from mecab.common import *
# from mecab.utils.string_utils import itoa, uitoa, dtoa

DEFAULT_ALLOC_SIZE = BUF_SIZE


# def _ITOA(n):
#     fbuf = itoa(n)
#     return StringBuffer().write(fbuf)
#
#
# def _UITOA(n):
#     fbuf = uitoa(n)
#     return StringBuffer().write(fbuf)
#
#
# def _DTOA(n):
#     fbuf = dtoa(n)
#     return StringBuffer().write(fbuf)


class StringBuffer:
    size_: int
    alloc_size_: int
    ptr_: str
    is_delete_: bool
    error_: bool

    def __init__(self, _s: str = '', _l: int = 0):
        self.size_ = 0
        self.alloc_size_ = _l
        self.ptr_ = _s
        self.is_delete_ = _s == '' and _l == 0
        self.error_ = False

    def __del__(self):
        if self.is_delete_:
            self.ptr_ = ''

    def reserve(self, length: int):
        if self.is_delete_ is False:
            self.error_ = self.size_ + length >= self.alloc_size_
            return not self.error_

        if self.size_ + length >= self.alloc_size_:
            if self.alloc_size_ == 0:
                self.alloc_size_ = DEFAULT_ALLOC_SIZE
                self.ptr_ = ''

            len = self.size_ + length
            while True:
                self.alloc_size_ *= 2
                if len < self.alloc_size_:
                    break

            self.ptr_ = self.ptr_[:self.size_]

        return True

    def write(self, string: str, length: int = None):
        if length is None:
            length = len(string)

        if self.reserve(length):
            self.ptr_ = f'{self.ptr_[:self.size_]}{string[:length]}{self.ptr_[self.size_ + length:]}'
            self.size_ += length

        return self

    def __lshift__(self, other):
        if not isinstance(other, str):
            other = str(other)

        return self.write(other, len(other))

    def clear(self):
        self.size_ = 0

    def str(self):
        return 0 if self.error_ else self.ptr_
