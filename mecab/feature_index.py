from dataknows.pecab.mecab.utils.string_utils import decode_charset
from typing import List
from abc import ABC, abstractmethod
import os

from mecab.utils.iconv import Iconv
from mecab.utils.fingerprint import fingerprint
from mecab.utils.param import Param
from mecab.utils.freelist import ChunkFreeList
from mecab.utils.string_utils import create_filename, getEscapedChar, tokenizeCSV, tokenize2
from mecab.utils.scoped_ptr import ScopedFixedArray
from mecab.common import FEATURE_FILE, CHECK_DIE, REWRITE_FILE
from mecab.learner_node import LearnerNode, LearnerPath, is_empty
from mecab.data_structure import MECAB_NOR_NODE

BUFSIZE = 2048
POSSIZE = 64


def copy_feature(feature_, feautre_free_list):
    feature_.append(-1)
    ptr = feautre_free_list.alloc(len(feature_))
    # copy
    ptr.extend(feature_)
    feature_.clear()


class FeatureIndex(ABC):

    def __init__(self):
        # protected
        self.feature_: List[int] = []
        self.feature_freelist_ = ChunkFreeList(int, 8192 * 32)
        self.char_freelist_ = ChunkFreeList(str, 8192 * 32)
        self.unigram_templs_: List[str] = []
        self.bigram_templs_: List[str] = []
        # self.rewrite_ = DictionaryRewriter
        self.os_ = ''
        self.maxid_: int = 0
        self.alpha_: float = 0.

    @abstractmethod
    def open(param: Param):
        pass

    @abstractmethod
    def clear():
        pass

    @abstractmethod
    def close():
        pass

    @abstractmethod
    def build_featrue():
        pass

    @abstractmethod
    def id(key: str):
        pass

    def size(self):
        # __len__ ?
        return self.maxid_

    def set_alpha(self, alpha: float):
        self.alpha_ = alpha

    def build_unigram_feature(self, path: LearnerPath, rfeature: str, lfeature: str):
        rbuf = rfeature if len(rfeature) <= BUFSIZE else rfeature[:BUFSIZE]
        lbuf = lfeature if len(lfeature) <= BUFSIZE else lfeature[:BUFSIZE]

        R = [None for _ in range(POSSIZE)]
        L = [None for _ in range(POSSIZE)]
        self.feature_.clear()
        
        lsize = tokenizeCSV(lbuf, L, len(L))
        rsize = tokenizeCSV(rbuf, R, len(R))

        for it in self.bigram_templs_:
            self.os_.clear()
            p = 0
            while True:
                if it[p] == '\\':
                    p = p + 1 # ++p
                    self.os_ += getEscapedChar(it[p])
                elif it[p] == '%':
                    p = p + 1 # ++p

                    if it[p] == 'L':
                        r, p = self.get_index(p, it, L, lsize)
                        if r == 0:
                            pass # goto
                        self.os_ += r
                    elif it[p] == 'R':
                        r, p = self.get_index(p, it, R, rsize)
                        if r == 0:
                            pass # goto
                        self.os_ += r
                    elif it[p] == 'l':
                        self.os_ += lfeature
                    elif it[p] == 'r':
                        self.os_ += rfeature
                    else:
                        CHECK_DIE(False, "unknown meta char: " + it[p])

                else:
                    self.os_ += it[p]
                p += 1
            self.os_ += '\0'
            # ADDB
            id_ = self.id(self.os_)
            if id != -1:
                self.feature_.append(id)
        
        copy_feature(path.rnode.fvector, self.feature_freelist_)
        return True

    def build_bigram_feature(self, ):
        pass

    def calc_cost(self, path: LearnerPath = None, node: LearnerNode = None):
        if path != None:
            if is_empty(path): return
            path.cost = path.rnode.wcost
            
            for f in path.fvector:
                if f == -1: break
                path.cost += self.alpha_[f]
        else:
            node.wcost = 0.
            if node.stat == MECAB_NOR_NODE: return
            for f in node.fvector:
                if f == -1: break
                node.wcost += self.alpha_[f]

    def strdup(self, p: str):
        length = len(p)
        q = self.char_freelist_.alloc()# length + 1
        q.extend(p)
        return q
    
    @staticmethod
    def convert(param: Param, txtfile: str, output: str):
        if not os.path.exists(txtfile):
            CHECK_DIE(False, "no such file or directory: ", txtfile)
        ifs = open(txtfile, 'r')

        buf = ScopedFixedArray(BUFSIZE)
        column = ['' for _ in range(4)]
        dic = [] # List[tuple(int, float)]
        model_charset = ''
        for line in ifs.readlines():
            if len(line) == 0: break

            CHECK_DIE(tokenize2(line, ":", column, 2), "format error: ", line)
            if column[0]:
                model_charset = column[1] + 1

        from_ = param.get("dictionary-charset")
        to_ = param.get("charset")

        if not len(from_) == 0:#.empty():
            CHECK_DIE(decode_charset(model_charset) == decode_charset(from_),
            "dictionary charset and model charset are different. " +\
            "dictionary_charset=" + from_ + " model_charset=" + model_charset)
        else:
            from_ = model_charset

        if len(to_) == 0:#.empty():
            to_ = from_

        iconv = Iconv() # TODO
        CHECK_DIE(iconv.open(from_, to_), "cannot create model from="+from_ + " to=" + to_)

        for line in ifs.readlines():
            CHECK_DIE(tokenize2(line, "\t", column, 2) == 2, "format error: " + line)
            feature = column[1]
            CHECK_DIE(iconv.convert(feature), "")
            fp = fingerprint(feature)
            alpha = float(column[0])
            dic.append((fp, alpha))

        output_list = []
        # output.clear()
        size = len(dic)
        
        #   unsigned int size = static_cast<unsigned int>(dic.size());
        # output->append(reinterpret_cast<const char*>(&size), sizeof(size));
        
        charset_buf = str(to_) if len(to_) < 32 else str(to_)[:31]
        dic = sorted(dic)

        
        return True

    def compile(self, param: Param, txtfile: str, binfile: str):
        buf = ''
        FeatureIndex.convert(param, txtfile, buf)
        try:
            ofs = open(binfile, 'wb')
        except OSError:
            raise "permission denied: " + binfile
        # permission denied check
        ofs.write(buf)
        ofs.close()
        return True

    def get_index(self, p: int, char: str, column: str, max: int):
        p += 1
        flg = False
        
        if char[p] == '?':
            flg = True
            p += 1
        
        CHECK_DIE(char[p] == '[', "getIndex(): unmatched '['")

        n = 0
        p += 1

        while(True):
            if char[p] in [str(i) for i in range(9)]:
                continue
            elif char[p] == '9':
                n = 10 * n + (ord(char[p]) - ord('0'))
            elif char[p] == ']':
                if n >= max:
                    return 0, p

                if flg and (column[n] == '*' or column[n][0] == '\0'):
                    return 0, p
                
                return column[n], p
            else:
                CHECK_DIE(False, "unmatched '['")
        return 0, p

    def open_template(self, param: Param):
        filename = create_filename(param.get('dicdir'), FEATURE_FILE)
        CHECK_DIE(os.path.exists(filename), "no such file or directory: " + filename)

        self.unigram_templs_.clear()
        self.bigram_templs_.clear()
        column = ['' for _ in range(4)]
        with open(filename, 'r') as f:
            for l in f.readlines():
                if l[0] == '\0' or l[0] == '#' or l[0] == ' ':
                    continue
                CHECK_DIE(tokenize2(l, "\t ", column, 2) == 2, "format error: " + filename)

                if column[0] == "UNIGRAM":
                    self.unigram_templs_.append(self.strdup(column[1]))
                elif column[0] == "BIGRAM":
                    self.bigram_templs_.append(self.strdup(column[1]))
                else:
                    CHECK_DIE(False, "format error: ", filename)

        
        filename = create_filename(param.get('dicdir'), REWRITE_FILE)
        self.rewrite_.open(filename)

        return True


class EncoderFeatureIndex(FeatureIndex):
    def open(self, param: Param) -> bool:
        return self.open_template(param)

    def close(self):
        self.dic_.clear()
        self.feature_cache_.clear()
        self.maxid_ = 0
