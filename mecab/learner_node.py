from typing import Optional, List
from dataclasses import dataclass
import numpy as np

from data_structure import NodeType
from utils import logsumexp

class LearnerPath:
    pass

class LearnerNode:
    pass


@dataclass
class LearnerPath:
    rnode: LearnerNode
    rnext: LearnerPath
    lnode: LearnerNode
    lnext: LearnerPath
    cost: float
    fvector: List[int]


@dataclass
class LearnerNode:
    prev: LearnerNode
    next: LearnerNode
    enext: LearnerNode
    bnext: LearnerNode
    rpath: LearnerPath
    lpath: LearnerPath
    anext: LearnerNode
    
    surface: str
    features: str

    id: int
    length: int
    rlength: int
    rcAttr: int
    posid: int
    char_type: str
    stat: str
    isbest: str
    alpha: float
    beta: float
    wcost: float
    wcost2: int
    cost: float
    fvector: List[int]



def repeat_find_if(target: str, delimiter: str, n: int) -> str:
    splited = target.split(delimiter, n)
    if len(splited) <= n:
        return ""
    else:
        if len(splited) == 1:
            return target
        else:
            return delimiter + splited[-1]
    


def node_cmp_eq(node1: LearnerNode, node2: LearnerNode, size: int, unk_size: int) -> bool:
    if node1.length == node2.length and node1.surface[:node1.length] == node2.surface[:node1.length]:
        p1 = node1.features
        p2 = node2.features

        if node2.stat == NodeType.MECAB_UNK_NODE:
            size = unk_size
        
        r1 = repeat_find_if(p1, ',', size)
        r2 = repeat_find_if(p2, ',', size)

        if len(p1) - len(r1) == len(p2) - len(r2) and p1[:len(p1) - len(r1)] == p2[:len(p1) - len(r1)]:
            return True
    
    return False


def is_empty(path: LearnerPath) -> bool:
    return (
        (not path.rnode.rpath and path.rnode.stat != NodeType.MECAB_EOS_NODE)
        or (not path.lnode.lpath and path.lnode.stat != NodeType.MECAB_BOS_NODE)
    )

def calc_expectation(path: LearnerPath, expected: List[float], Z: float):
    if is_empty(path):
        return None
    
    c = np.exp(path.lnode.alpha + path.cost + path.rnode.beta - Z)

    for i in range(0, len(path.fvector)):
        if path.fvector[i] == -1:
            break

        expected[path.fvector[i]] += c
    
    if path.rnode.stat != NodeType.MECAB_EOS_NODE:
        for i in range(0, len(path.rnode.fvector)):
            if path.rnode.fvector[i] == -1:
                break

            expected[path.rnode.fvector[i]] += c

def calc_alpha(n: LearnerNode):
    n.alpha = 0.0

    path = n.lpath
    while path:
        n.alpha = logsumexp(n.alpha, path.cost + path.lnode.alpha, path == n.lpath)

        path = path.lnext


def calc_beta(n: LearnerNode):
    n.beta = 0.0

    path = n.rpath
    while path:
        n.beta = logsumexp(n.beta, path.cost + path.rnode.beta, path == n.rpath)
        
        path = path.rnext
