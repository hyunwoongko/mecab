import math
import sys
from typing import List

from mecab.data_structure import Node, RequestType, BoundaryConstraintType
from mecab.utils import logsumexp
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

    def open(self):
        pass

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
