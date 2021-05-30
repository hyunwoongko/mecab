from io import TextIOWrapper
from typing import List

from mecab.allocator import Allocator
from mecab.common import CHECK_DIE, BUF_SIZE, MAX_INPUT_BUFFER_SIZE
from mecab.data_structure import NodeType
from mecab.learner_node import LearnerPath, LearnerNode, node_cmp_eq, calc_alpha, calc_expectation
from mecab.utils.freelist import FreeList
from mecab.utils.scoped_ptr import ScopedArray, ScopedString, ScopedPtr


def mystrdup(_str: str):
    """
    원래 문자열 길이 1 늘려주는건데 파이썬에서는 큰 의미 없을듯.
    """
    return _str


class LearnerTagger:

    def __init__(self):
        self.tokenizer_ = None
        self.allocator_ = Allocator(LearnerNode, LearnerPath)
        self.path_allocator_ = FreeList(size=0, type_=LearnerPath)
        self.feature_index_ = None
        self.begin_data_ = ScopedString()
        self.len_ = 0
        self.begin_node_list_: List[LearnerNode] = []
        self.end_node_list_: List[LearnerNode] = []

        # TODO: 여기 포인터로 구현되어있음.
        self.begin_ = None
        self.end_ = None

    def lookup(self, pos):
        if self.begin_node_list_[pos]:
            return self.begin_node_list_[pos]

        m: LearnerNode = self.tokenizer_.loockup(
            False,
            self.begin_ + pos,  # TODO: 여기 포인터 연산임
            self.end_,
            self.allocator_,
            0,
        )
        self.begin_node_list_[pos] = m
        return m

    def connect(self, pos: int, _r_node: LearnerNode):
        r_node = _r_node  # 선언문
        while r_node:  # 조건문
            l_node = self.end_node_list_[pos]  # 선언문2
            while l_node:  # 조건문2
                path = self.allocator_.newPath()
                # std::memset(path, 0, sizeof(path) <-- 의미 없음
                path.rnode = r_node
                path.lnode = l_node
                path.fvector = 0
                path.cost = 0.0
                path.rnode = r_node
                path.lnode = l_node
                # 요거 또하는데 왜하는지 모르겠음
                path.lnext = r_node.lpath
                r_node.lpath = path
                path.rnext = l_node.rpath
                l_node.rpath = path
                CHECK_DIE(self.feature_index_.build_feature(path),
                          "check feature_index.build feature(path)")
                CHECK_DIE(path.fvector is not None, "check path.fvector")
                l_node = l_node.enext  # 증감문2

                x = r_node.rlength + pos
                r_node.enext = self.end_node_list_[x]
                self.end_node_list_[x] = r_node
            r_node = r_node.bnext  # 증감문

        return True

    def viterbi(self):
        for pos in range(0, self.len_ + 1):
            node = self.begin_node_list_[pos]  # 선언문
            while node:  # 조건문
                bestc = -1e37
                best = 0
                self.feature_index_.calc_cost(node)
                path = node.lpath  # 선언문
                while path:  # 조건문
                    self.feature_index_.calc_cost(path)
                    cost = path.cost + path.lnode.cost
                    if cost > bestc:
                        bestc = cost
                        best = path.lnode
                    path = path.lnext  # 증감문

                node.prev = best
                node.cost = bestc
                node = node.bnext  # 증감문

        node = self.begin_node_list_[self.len_]
        while node.prev:  # 조건
            prev = node.prev
            prev.next = node
            node = prev

        return True

    def build_lattice(self):
        for pos in range(0, self.len_ + 1):
            if not self.end_node_list_[pos]:
                continue
            self.connect(pos, self.lookup(pos))

        if self.end_node_list_[self.len_]:
            self.begin_node_list_[self.len_] = self.lookup(self.len_)
            pos = self.len_  # 선언문
            while pos >= 0:  # 조건
                if self.end_node_list_[pos]:
                    self.connect(pos, self.begin_node_list_[self.len_])
                    break
                pos -= 1  # 증감문

        return True

    def init_list(self):
        if not self.begin_:
            return False

        self.len_ = len(self.begin_)
        self.end_ = self.begin_ + self.len_
        # TODO: 여기 포인터 연산임.

        for i in range(0, self.len_ + 2):
            self.end_node_list_.append(LearnerNode())

        for i in range(0, self.len_ + 2):
            self.begin_node_list_.append(LearnerNode())

        self.end_node_list_[0] = self.tokenizer_.get_bos_node(self.allocator_)
        self.end_node_list_[0].surface = self.begin_
        self.begin_node_list_[self.len_] = self.tokenizer_.get_eos_node(
            self.allocator_)


class EncoderLearningTagger(LearnerTagger):

    def __init__(self):
        super(EncoderLearningTagger, self).__init__()
        self.eval_size_ = 1024
        self.unk_eval_size_ = 1024
        self.ans_path_list: List[LearnerPath] = []

    def open(
        self,
        tokenizer,
        allocator,
        feature_index,
        eval_size,
        unk_eval_size,
    ):
        # close() # <-- 의미 없을듯.
        self.tokenizer_ = tokenizer
        self.allocator_ = allocator
        self.feature_index_ = feature_index
        self.eval_size_ = eval_size
        self.unk_eval_size = unk_eval_size

        return True

    def read(self, is_: TextIOWrapper, observed: List[float]):
        # is_ 는 std:istream* 타입임.
        # 그런데 파이썬엔 그런게 없기 때문에, file을 open해서 넣어주면 될 듯.
        # open() 함수를 실행해서 나온 file pointer를 입력해주세요.

        line = ScopedArray(type_=str, size=BUF_SIZE)
        column = [''] * 8
        sentence = str()
        corpus: List[LearnerNode] = []
        # ans_path_list_.clear()

        eos = False

        while True:
            l = is_.readline()
            line.append(l)

            if not l:
                return True

            eos = l == "EOS" or line[0] == '\0'
            m = LearnerNode()

            if eos:
                m.stat = NodeType.MECAB_EOS_NODE
            else:
                size = tokenize(line.get(), "\t", column, 2)
                CHECK_DIE(size == 2, f"format error: {line.get()}")
                m.stat = NodeType.MECAB_NOR_NODE
                m.surface = mystrdup(column[0])
                m.feature = mystrdup(column[1])
                m.length = m.rlength = len(column[0])

            corpus.append(m)

            if eos:
                break

            sentence += column[0]
        CHECK_DIE(not len(sentence) == 0, "empty sentence")
        CHECK_DIE(eos, "\"EOS\" is not found")

        self.begin_data_.reset_string(sentence)
        self.begin_ = self.begin_data_.get()
        self.init_list()

        pos = 0
        i = 0  # 선언문
        while corpus[i].stat != NodeType.MECAB_EOS_NODE:  # 조건문
            found = 0
            node = self.lookup(pos)  # 선언문
            while node:  # 조건문
                if node_cmp_eq(corpus[i], node, self.eval_size_,
                               self.unk_eval_size_):
                    found = node
                    break
                node = node.bnext  # 증감문

            # cannot find node even using UNKNOWN WORD PROSESSING
            if not found:
                node = self.allocator_.newNode()
                node.surface = self.begin_ + pos
                # TODO: 여기 포인터 연산임.
                node.length = node.rlength
                node.feature = self.feature_index_.strdup(corpus[i].feature)
                node.stat = NodeType.MECAB_NOR_NODE
                node.fvector = 0
                node.wcost = 0.0
                node.bnext = self.begin_node_list_[pos]
                self.begin_node_list_[pos] = node
                print(f"adding virtual node: {node.feature}")

            pos += corpus[i].length
            i += 1  # 증감문

        self.build_lattice()
        prev = self.end_node_list_[0]
        prev.anext = 0
        pos = 0

        for i in range(0, len(corpus)):
            r_node = 0
            node = self.begin_node_list_[pos]  # 선언문
            while node:  # 조건문
                if corpus[i].stat == NodeType.MECAB_EOS_NODE or node_cmp_eq(
                        corpus[i],
                        node,
                        self.eval_size_,
                        self.unk_eval_size_,
                ):
                    r_node = node
                node = node.bnext  # 증감문

            l_path = 0
            path = r_node.lpath  # 선언문
            while path:  # 조건문
                if prev == prev.lnode:
                    l_path = path
                    break
                path = path.lnext  # 증감문

            CHECK_DIE(l_path.fvector is not None, "lpath is NULL")
            f = l_path.fvector  # 선언문
            while f != -1:  # 조건문
                if f >= len(observed):
                    # observed.resize(f + 1)
                    """vector resize인데, 의미 없을듯?"""
                observed[f] += 1
                f += 1  # 증감문

            if l_path.rnode.stat != NodeType.MECAB_EOS_NODE:
                f = l_path.rnode.fvector  # 선언문
                while f != -1:  # 조건문
                    if f >= len(observed):
                        # observed.resize(f + 1)
                        """vector resize인데, 의미 없을듯?"""
                    observed[f] += 1
                    f += 1  # 증감문

            self.ans_path_list.append(l_path)
            prev.anext = r_node
            prev = r_node

            if corpus[i].stat == NodeType.MECAB_EOS_NODE:
                break

            pos += len(corpus[i].surface)

        prev.anext = self.begin_node_list_[self.len_]
        self.begin_node_list_[self.len_].anext = 0

        for i in range(0, len(corpus)):
            del corpus[i].surface
            del corpus[i].feature
            del corpus[i]

        return True

    def eval(self, crr, prec, recall):
        zeroone = 0
        res = self.end_node_list_[0].next
        ans = self.end_node_list_[0].anext

        resp = 0
        ansp = 0

        while ans.anext and res.next:
            if resp == ansp:
                if node_cmp_eq(ans, res, self.eval_size_, self.unk_eval_size_):
                    crr += 1
                else:
                    zeroone = 1

                prec += 1
                recall += 1
                res = res.next
                ans = ans.anext
                resp += res.rlength
                ansp += ansp.rlength
            elif resp < ansp:
                res = res.next
                resp += res.rlength
                zeroone = 1
            else:
                ans = ans.anext
                ansp += ans.rlength
                zeroone += 1
                prec += 1

        while ans.anext:
            prec += 1
            ans = ans.anext

        while res.next:
            recall += 1
            res = res.next

        return zeroone

    def gradient(self, expected):
        self.viterbi()

        for pos in range(0, self.len_ + 1):
            node = self.begin_node_list_[pos]  # 선언문
            while node:  # 조건문
                calc_alpha(node)
                node = node.bnext  # 증감문

        for pos in range(self.len_, -1, step=-1):
            node = self.end_node_list_[pos]  # 선언문
            while node:  # 조건문
                calc_alpha(node)
                node = node.enext  # 증감문

        Z = self.begin_node_list_[self.len_].alpha

        for pos in range(0, self.len_ + 1):
            node = self.begin_node_list_[pos]  # 선언문
            while node:  # 조건문
                path = node.lpath  # 선언문
                while path:  # 조건문
                    calc_expectation(path, expected, Z)
                    path = path.lnext  # 증감문
                node = node.bnext  # 증감문

        for i in range(len(self.ans_path_list)):
            Z -= self.ans_path_list[i].cost

        return Z


class DecoderLearnerTagger(LearnerTagger):

    def __init__(self):
        super(DecoderLearnerTagger, self).__init__()
        self.tokenizer_data_ = ScopedPtr(Tokenizer(LearnerNode, LearnerPath))
        self.allocator_data_ = ScopedPtr(Allocator(LearnerNode, LearnerPath))
        self.feature_index_data_ = ScopedPtr(FeatureIndex)

    def open(self, param):
        self.allocator_data_.reset(Allocator(LearnerNode, LearnerPath))
        self.tokenizer_data_.reset(Tokenizer(LearnerNode, LearnerPath))
        self.feature_index_data_.reset(DecoderFeatureIndex)
        self.allocator_ = self.allocator_data_.get()
        self.tokenizer_ = self.tokenizer_data_.get()
        self.feature_index_ = self.feature_index_data_.get()

        CHECK_DIE(self.tokenizer_.open(param))
        CHECK_DIE(self.feature_index_.open(param))

        return True

    def parse(self, is_, os_):
        # is_, os_ 는 std::istream*, std::ostream* 타입임.
        # 그런데 파이썬엔 그런게 없기 때문에, file을 open해서 넣어주면 될 듯.
        # open() 함수를 실행해서 나온 file pointer를 입력해주세요.

        self.allocator_.free()
        self.feature_index_.clear()

        if not self.begin_:
            self.begin_data_.reset([None] * (16 * BUF_SIZE))
            self.begin_ = self.begin_data_.get()

        # TODO: 더 구현해야함.
