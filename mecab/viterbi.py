import math
import sys
from typing import List, Tuple

from mecab.common import CHECK_FALSE
from mecab.data_structure import Node, RequestType, BoundaryConstraintType
from mecab.utils.scoped_ptr import ScopedArray
from mecab.lattice import Lattice
from mecab.utils import logsumexp
from mecab.tokenizer import Tokenizer
from mecab.connector import Connector
# 있다고 가정하고 구현


def calc_alpha(n: Node, beta: float):
    n.alpha = 0
    path = n.lpath  # 선언문
    while path:  # 반복문
        n.alpha = logsumexp(
            n.alpha,
            -beta * path.cost + path.lnode.alpha,
            path == n.lpath,
        )
        path = path.lnext  # 증감문

    return n


def calc_beta(n: Node, beta: float):
    n.beta = 0
    path = n.rpath  # 선언문
    while path:  # 반복문
        n.beta = logsumexp(
            n.beta,
            -beta * path.cost + path.rnode.beta,
            path == n.rpath,
        )
        path = path.rnext  # 증감문
    return n


def connect(
    pos,
    rnode,
    begin_node_list,
    end_node_list,
    connector,
    allocator,
    is_all_path,
):
    while rnode:  # 반복문
        best_cost = sys.maxsize
        best_node = 0

        lnode = end_node_list[pos]  # 선언문
        while lnode:  # 반복문
            lcost = connector.cost(lnode, rnode)
            cost = lnode.cost + lcost

            if cost < best_cost:
                best_node = lnode
                best_cost = cost

            if is_all_path:
                path = allocator.new_path()
                path.cost = lcost
                path.rnode = rnode
                path.lnode = lnode
                path.lnext = rnode.lpath
                rnode.lpath = path
                path.rnext = lnode.rpath
                lnode.rpath = path

            lnode = lnode.enext  # 증감문

        if not best_node:
            return False

        rnode.prev = best_node
        rnode.next = 0
        rnode.cost = best_cost
        x = rnode.rlength + pos
        rnode.enext = end_node_list[x]
        end_node_list[x] = rnode

        rnode = rnode.bnext  # 증감문
    return True


class Viterbi:

    def __init__(self):
        self.tokenizer_ = None
        self.connector_ = None
        self.cost_factor_ = None
        # 아직 구현 안된 부분이 많아서 일단 이렇게 해놓음.
        # 나중에 토크나이저와 커넥터 등이 구현되면 구현해놓을 예정.

    def open_(self, param):
        return self.open(
            param.get("dicdir"),
            param.get("userdic"),
            param.get("bos-feature"),
            param.get("unk-feature"),
            param.get("max-grouping-size"),
            param.get("cost-factor"),
        )

    def open(
        self,
        dicdir,
        userdic,
        bos_feature,
        unk_feature,
        max_grouping_size,
        cost_factor,
    ):
        self.tokenizer_.reset(Tokenizer())
        CHECK_FALSE(
            self.tokenizer_.open(dicdir, userdic, bos_feature, unk_feature,
                                 max_grouping_size), "")
        CHECK_FALSE(self.tokenizer_.dictionary_info(), "Dictionary is empty")

        self.connector_.reset(Connector())
        CHECK_FALSE(self.connector_.open(dicdir), "")
        CHECK_FALSE(
            self.tokenizer_.dictionary_info().lsize
            == self.connector_.left_size() and
            self.tokenizer_.dictionary_info().rsize
            == self.connector_.right_size(),
            "Transition table and dictionary are not compatible",
        )

        self.cost_factor_ = cost_factor
        if self.cost_factor_ == 0:
            self.cost_factor_ = 800

        return True

    def analyze(self, lattice):
        if not lattice or not lattice.sentence():
            return False

        if not self.init_partial(lattice):
            return False

        result = False
        if lattice.has_request_type(
                RequestType.MECAB_NBEST) or lattice.has_request_type(
                    RequestType.MECAB_MARGINAL_PROB):
            # is_all_path = True
            if lattice.has_constraint():
                result = self.viterbi(lattice, True, True)
            else:
                result = self.viterbi(lattice, True, False)
        else:
            if lattice.has_constraint():
                result = self.viterbi(lattice, False, True)
            else:
                result = self.viterbi(lattice, False, False)

        if not result:
            return False

        if not self.forwardbackward(lattice):
            return False

        if not self.build_best_larttice(lattice):
            return False

        if not self.build_all_lattice(lattice):
            return False

        if not self.init_nbest(lattice):
            return False

        return True

    def viterbi(self, lattice, is_all_path, is_partial):
        end_node_list = lattice.end_nodes()
        begin_node_list = lattice.begin_nodes()
        allocator = lattice.allocator()

        len_ = lattice.size()
        begin = lattice.sentence()
        end = begin + len_

        bos_node = self.tokenizer_.get_bos_node(lattice.allocator())
        bos_node.surface = lattice.sentence()
        end_node_list[0] = bos_node

        pos = 0
        while pos < len_:
            if end_node_list[pos]:
                right_node = self.tokenizer_.lookup(
                    begin + pos,
                    end,
                    allocator,
                    lattice,
                    is_partial,
                )

                begin_node_list[pos] = right_node

                if not connect(
                        pos,
                        right_node,
                        begin_node_list,
                        end_node_list,
                        self.connector_.get(),
                        allocator,
                        is_all_path,
                ):
                    lattice.set_what("too long sentence.")
                    return False
            pos += 1  # 증감문

        eos_node = self.tokenizer_.get_eos_node(lattice.allocator())
        eos_node.surface = lattice.sentence() + lattice.size()
        begin_node_list[lattice.size()] = eos_node

        pos = len_
        while pos >= 0:
            if end_node_list[pos]:
                if not connect(
                        pos,
                        eos_node,
                        begin_node_list,
                        end_node_list,
                        self.connector_.get(),
                        allocator,
                        is_all_path,
                ):
                    lattice.set_what("too long sentence.")
                    return False
                break
            pos -= 1  # 증감문

        end_node_list[0] = bos_node
        begin_node_list[lattice.size()] = eos_node

        return True

    def forwardbackward(self, lattice):
        if not lattice.has_request_type(RequestType.MECAB_MARGINAL_PROB):
            return True

        end_node_list = lattice.end_nodes()
        begin_node_list = lattice.begin_nodes()

        len_ = lattice.size()
        theta = lattice.theta()

        end_node_list[0].alpha = 0.0

        pos = 0
        while pos <= len_:
            node = begin_node_list[pos]
            while node:
                node = calc_alpha(node, theta)
                node = node.bnext  # 증감문
            pos += 1  # 증감문

        begin_node_list[len_].beta = 0.0

        pos = len_
        while pos >= 0:
            node = end_node_list[pos]
            while node:
                calc_beta(node, theta)
                node = node.enext  # 증감문
            pos -= 1  # 증감문

        Z = begin_node_list[len_].alpha
        lattice.set_z(Z)

        pos = 0
        while pos <= len_:
            node = begin_node_list[pos]
            while node:
                node.prob = math.exp(node.alpha + node.beta - Z)
                path = node.lpath
                while path:
                    path.prob = math.exp(path.lnode.alpha - theta * path.cost +
                                         path.rnode.beta - Z)
                    path = path.lnext  # 증감문
                node = node.bnext  # 증감문
            pos += 1  # 증감문

        return True

    def init_partial(self, lattice):
        if not lattice.has_request_type(RequestType.MECAB_PARTIAL):
            if lattice.has_constraint():
                lattice.set_boundary_constraint(
                    0,
                    BoundaryConstraintType.MECAB_TOKEN_BOUNDARY,
                )
                lattice.set_boundary_constraint(
                    lattice.size(),
                    BoundaryConstraintType.MECAB_TOKEN_BOUNDARY,
                )
            return True

        allocator = lattice.allocator()
        str_ = allocator.partial_buffer(lattice.size() + 1)
        str_ = lattice.sentence()[:lattice.size() + 1]

        lines: List[str] = []
        lsize = tokenize(str_, "\n", lines, lattice.size() + 1)
        # https://github.com/jeongukjae/python-mecab/blob/master/include/mecab/viterbi.h#L270
        # std::back_inserter(lines) 넘기는 방식이 파이썬에서 무슨 의미 있는지 모르겠음.
        # 그냥 레퍼런스만 넘겨주게끔 구현했음. 나중에 문제 생기면 말씀해주세용

        column: List[str] = []
        buf = ScopedArray(type_=str, size=lattice.size() + 1)

        tokens: List[Tuple[str, str]] = []
        # https://github.com/jeongukjae/python-mecab/blob/master/include/mecab/viterbi.h#L276
        # tokens.reverse(lsize) <-- 왜 하는건지 모르겠음.

        pos = 0
        os_ = ""
        for i in range(lsize):
            size = tokenize(lines[1], "t", column, 2)
            if size == 1 and column[0] == "EOS":
                break
            len_ = len(column[0])
            if size == 2:
                tokens.append((column[0], column[1]))
            else:
                tokens.append((column[0], "0"))

            os_ += column[0]
            pos += len_

        # os_ += "\0"
        # 필요 없을듯?

        lattice.set_sentence(os_)
        pos = 0

        for i in range(len(tokens)):
            surface = tokens[i][0]  # pair.first
            feature = tokens[i][1]  # pair.second
            len_ = len(surface)

            lattice.set_boundary_constraint(
                pos, BoundaryConstraintType.MECAB_TOKEN_BOUNDARY)
            lattice.set_boundary_constraint(
                pos + len_, BoundaryConstraintType.MECAB_TOKEN_BOUNDARY)

            if feature:
                lattice.set_feature_constraint(pos, pos + len_, feature)

                for n in range(len_):
                    lattice.set_boundary_constraint(
                        pos + n, BoundaryConstraintType.MECAB_INSIDE_TOKEN)

            pos += len_

        return True

    def init_n_best(self, lattice: Lattice):
        if not lattice.has_request_type(RequestType.MECAB_NBEST):
            return True

        lattice.allocator().nbest_generator().set(lattice.eos_node())
        return True

    def build_best_lattice(self, lattice: Lattice):
        node = lattice.eos_node()
        while node.prev:
            node.is_best = 1
            prev_node = node.prev
            prev_node.next = node
            node = prev_node

        return True

    def build_all_lattice(self, lattice: Lattice):
        return lattice.buildAllLattice(lattice)

    def build_alternative(self, lattice: Lattice):
        # cout으로 terminal에 출력하는 기능만 포함되어 있음.
        # 굳이 구현할 필요 없을듯?
        pass
