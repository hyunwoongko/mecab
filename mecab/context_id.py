from typing import List

import mecab.utils.param
from mecab.iconv import Iconv
from mecab.utils.string_utils import tokenize2
from mecab.common import CHECK_FALSE, CHECK_DIE

def open_map(filename: str, cmap: dict, iconv: Iconv):
    lines = open(filename, mode="r", encoding="utf-8").read().splitlines()
    cmap.clear()  ##
    col = ''
    for line in lines:
        assert tokenize2(line," \t", col, 2) == 2, \
            f"format error: {line}"
        pos = col[1]
        if iconv:
            iconv = Iconv.convert(pos)
        cmap[pos] = int(col[0])
    return True

def build_bos(cmap: dict, bos: str):
    id = 1   ## for BOS/EOS
    for k, v in cmap.items():
        cmap[k] = id
        id += 1
    if bos not in cmap:
        cmap[bos] = 0
    return True

def save_file(filename: str, cmap : dict):
    try:
        with open(filename, mode="w", encoding="utf-8") as f:
            for k, v in cmap.items():
                f.write(f"{v} {k}\n")
        return True
    except PermissionError:
        raise PermissionError

class ContextID:
    def __init__(self):
        self._left_ = {}
        self._right_ = {}
        self._left_bos_ = ""
        self._right_bos_ = ""

    def clear(self):
        self._left_.clear()
        self._right_.clear()
        self._left_bos_ = ""
        self._right_bos_ = ""

    def add(self, l: dict, r: dict):
        ## map key 중복 시 insert X
        if l not in self._left_:
            self._left_[l] = 1
        if r not in self._right_:
            self._right_[r] = 1

    def add_bos(self, l: str, r: str):
        self._left_bos_ = l
        self._right_bos_ = r

    def save(self, lfile: str, rfile: str) -> bool:
        return save_file(lfile, self._left_) and save_file(rfile, self._right_)

    def build(self) -> bool:
        return build_bos(self._left_, self._left_bos_) and build_bos(self._right_, self._right_bos_)

    def open(self, lfile: str, rfile: str, iconv: Iconv):
        return open_map(lfile, self._left_, iconv) and open_map(rfile, self._right_, iconv)

    def lid(self, l: str) -> int:
        if l not in self._left_:
            CHECK_DIE(False, f"cannot find LEFT-ID for {l}")
        return self._left_[l]

    def rid(self, r: str) -> int:
        if r not in self._right_:
            CHECK_DIE(False, f"cannot find RIGHT-ID for {r}")
        return self._right_[r]

    def left_size(self) -> int:
        return len(self._left_)

    def right_size(self) -> int:
        return len(self._right_)

    def left_ids(self):
        return self._left_

    def right_ids(self):
        return self._right_

    def is_valid(self, lid: int, rid: int) -> bool:
        return lid >= 0 and lid < self.left_size() and rid >= 0 and rid < self.right_size()
