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

    def build_bigram_feature(self, path: LearnerPath, rfeature: str, lfeature: str):
        rbuf = rfeature if len(rfeature) <= BUFSIZE else rfeature[:BUFSIZE]
        lbuf = lfeature if len(lfeature) <= BUFSIZE else lfeature[:BUFSIZE]

        self.feature_.clear()
        
        L = tokenizeCSV(lbuf, ',', POSSIZE)
        R = tokenizeCSV(rbuf, ',', POSSIZE)
        lsize, rsize = len(L), len(R)

        goto = False
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
                            goto = True
                            break # goto
                        self.os_ += r
                    elif it[p] == 'R':
                        r, p = self.get_index(p, it, R, rsize)
                        if r == 0:
                            goto = True
                            break # goto
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
            
            if goto:
                goto = False
                continue

            self.os_ += '\0'
            # ADDB
            id_ = self.id(self.os_)
            if id_ != -1:
                self.feature_.append(id)
        
        copy_feature(path.rnode.fvector, self.feature_freelist_)
        return True

    def build_unigram_feature(self, path: LearnerPath, ufeature: str):
        ubuf = ufeature if len(ufeature) <= BUFSIZE else ufeature[:BUFSIZE]
        self.feature_.clear()

        F = tokenizeCSV(ubuf, ',', POSSIZE)
        usize = len(F)

        goto = False
        for it in self.unigram_templs_:
            self.os_.clear()
            p = 0
            while True:
                if it[p] == '\\':
                    p = p + 1 # ++p
                    self.os_ += getEscapedChar(it[p])
                elif it[p] == '%':
                    p = p + 1 # ++p

                    if it[p] == 'F':
                        r, p = self.get_index(p, it, F, usize)
                        if r == 0:
                            goto = True
                            break # goto
                        self.os_ += r
                    elif it[p] == 't':
                        self.os_ += path.rnode.char_type
                    elif it[p] == 'u':
                        self.os_ += ufeature
                    elif it[p] == 'w':
                        if path.rnodestat == MECAB_NOR_NODE:
                            self.os_.wrte(path.rnode.surface, path.rnode.length)
                    else:
                        CHECK_DIE(False, "unknown meta char: " + it[p])

                else:
                    self.os_ += it[p]
                p += 1
            
            if goto:
                goto = False
                continue

            self.os_ += '\0'
            # ADDB
            id_ = self.id(self.os_)
            if id_ != -1:
                self.feature_.append(id)
        
        copy_feature(path.rnode.fvector, self.feature_freelist_)
        return True

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

        # buf = ScopedFixedArray(BUFSIZE)
        column = ['' for _ in range(4)]
        dic = [] # List[tuple(int, float)]
        model_charset = ''
        for line in ifs.readlines():
            if len(line) == 0: break

            CHECK_DIE(len(tokenize2(line, ":", 2)) == 2, "format error: ", line)
            if column[0] == 'charset':
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

        output = []
        # output.clear()
        size = len(dic)
        output.append(size)
        
        charset_buf = str(to_) if len(to_) < 32 else str(to_)[:31]
        output.append(charset_buf)

        dic = sorted(dic)

        alphas, fps = zip(*dic)
        output = output + alphas + fps

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
    def __init__(self):
        super(self, FeatureIndex).__init__()
        self.dic_ = {}
        self.feature_cache_ = {}

    def id_(self, key: str):
        if key in self.dic_:
            return self.dic_[key]
        else:
            self.dic_[key] = self.maxid_
            self.maxid_ += 1
            # return maxid_++
            return self.maxid_ - 1

    def open(self, param: Param) -> bool:
        return self.open_template(param)

    def close(self):
        self.dic_.clear()
        self.feature_cache_.clear()
        self.maxid_ = 0

    def reopen(self, filename: str, dic_charset: str, alpha: List[float], param: Param):
        self.close()
        if not os.path.exists(filename):
            return False

        ifs = open(filename, 'r')

        for buf in ifs.readlines():
            if len(buf) == 0: break

            column = tokenize2(buf, ':', 2)
            CHECK_DIE(len(column) == 2, 'format error: ' + buf)
            if column[0] == 'charset':
                model_charset = column[1] + 1
            else:
                param.set(column[0], column[1])

        CHECK_DIE(dic_charset)
        CHECK_DIE(not len(model_charset) == 0, 'charset is empty')

        iconv = Iconv()
        CHECK_DIE(iconv.open(model_charset, dic_charset),
        "cannot create model from=" + model_charset + " to=" + dic_charset)

        alpha.clear()
        CHECK_DIE(self.maxid_ == 0)
        CHECK_DIE(self.dic_)
        for buf in ifs.readlines():
            column = tokenize2(buf, '\t', 2)
            CHECK_DIE(len(column) == 2, 'format error: ' + buf)
            feature = column[1]
            CHECK_DIE(iconv.convert(feature))
            self.dic_[feature] = self.maxid_
            self.maxid_ = self.maxid_ + 1
            alpha.append(float(column[0]))

        return True

    def save(self, filename: str, header: str) -> bool:
        CHECK_DIE(header)
        CHECK_DIE(self.alpha_)
        try:
            ofs = open(filename, 'wb')
        except OSError:
            return False
        
        ofs.write(header + '\n')

        for k, v in self.dic_.items():
            ofs.write(self.alpha_[v] + '\t' + k + '\n')

        return True

    def shrink(self, freq: int, observed: List[float]):
        freqv = [0 for _ in range(self.maxid_)]

        for k, v in self.feature_cache_.items():
            while v[0] != -1:
                freqv[v[0]] += v[1]

        if freq <= 1: return

        self.maxid_ = 0
        old2new = {}

        for i, v in enumerate(freqv):
            if v >= freq:
                old2new[i] = self.maxid_
                self.maxid_ += 1

        new_dic = {}
        for k, v in self.dic_.items():
            if k in old2new:
                new_dic[k] = old2new[k]

        # need pointer operation..
        # TODO
        # for k, v in self.feature_cache.items():
        #     to = v[0]
        #     while v[0] != -1:
        #         if v[0] in old2new:
        #             to = 

    def clearcache(self):
        self.feature_cache_.clear()
        self.rewrite_.clear()
            