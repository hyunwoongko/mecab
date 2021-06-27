from multipledispatch import dispatch

from mecab.common import BUF_SIZE, CHECK_FALSE, MATRIX_FILE
from mecab.data_structure import Node
from mecab.mmap import Mmap
from mecab.utils.param import Param
from mecab.utils.scoped_ptr import ScopedFixedArray, ScopedPtr
from mecab.utils.string_utils import create_filename, tokenize2

class Connector:
    _cmmap_: ScopedPtr
    _matrix_: int
    _lsize_: int
    _rsize_: int

    def __init__(self):
        self._cmmap_ = ScopedPtr(Mmap())
        self._matrix_ = 0
        self._lsize_ = 0
        self._rsize_ = 0

    @dispatch(Param)
    def open(self, param: Param) -> bool:
        return param.get("dicdir")

    @dispatch(str)
    def open(self, dicdir: str) -> bool:
        filename = create_filename(dicdir, MATRIX_FILE)
        return open(filename)

    @dispatch(str, str)
    def open(self, filename: str, mode='r') -> bool:
        CHECK_FALSE(self._cmmap_.open(filename, mode), "cannot open: " + filename)

        self._matrix_ = self._cmmap_.begin()

        CHECK_FALSE(self._matrix_, "matrix is NULL")
        CHECK_FALSE(self._cmmap_.size() >= 2, "file size is invalid: " + filename)

        # lsize_ = static_cast<unsigned short>((*cmmap_)[0]);
        self._lsize_ = len(self.__cmmap__[0]) # len??
        # rsize_ = static_cast<unsigned short>((*cmmap_)[1]);
        self._rsize_ = len(self.__cmmap__[1]) # len??

        CHECK_FALSE((self._lsize_ * self._rsize_ + 2) == self._cmmap_.size(), "file size is invalid: " + filename)

        self._matrix_ = self._cmmap_.begin() + 2
        return True

    def open_text(self, filename: str) -> bool:
        # std::ifstream ifs(filename);
        CHECK_FALSE(open(filename), "no such file or directory: " + filename)
        column = "00" # char* column[2];
        buf = ScopedFixedArray(BUF_SIZE)

        # ifs.getline(buf.get(), buf.size());
        # CHECK_DIE(tokenize2(buf.get(), "\t ", column, 2) == 2) << "format error: " << buf.get();
        
        self._lsize_ = int(column[0])
        self._rsize_ = int(column[1])

        return True

    def close(self):
        self._cmmap_.close()
    
    def clear():
        # void clear() {}
        pass

    def left_size(self) -> int: return self._lsize_
    def right_size(self) -> int: return self._rsize_

    def set_left_size(self, lsize: int):
        self._lsize_ = lsize
    
    def set_right_size(self, rsize: int):
        self._rsize_ = rsize
    
    def transition_cost(self, rc_attr: int, lc_attr: int) -> int:
        return self._matrix_[rc_attr + self._lsize_ * lc_attr]

    def cost(self, l_node: Node, r_node: Node):
        return self._matrix_[l_node.rcAttr + self._lsize_ * r_node.lcAttr] + r_node.wcost

    def mutable_matrix(self):
        return self._matrix_[0]

    def matrix(self):
        return self._matrix_[0]

    def is_valid(self, lid: int, rid: int) -> bool:
        return lid >= 0 and lid < self._rsize_ and rid >= 0 and rid < self._lsize_

    def compile(self):
        pass

    def __del__(self):
        self.close()
    