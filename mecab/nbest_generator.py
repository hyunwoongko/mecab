from typing import List

from mecab.data_structure import Node, NodeType, Path
from mecab.utils.freelist import FreeList
from queue import PriorityQueue


class QueueElement:

    def __init__(self):
        self.node = Node()
        self.next = None
        self.fx = 0
        self.gx = 0

    def __gt__(self, other):
        """equivalent with `QueueElementComp`"""
        return self.fx > other.fx


class NBestGenerator:
    def __init__(self):
        self.agenda_: PriorityQueue = PriorityQueue()
        self.freelist_: FreeList = FreeList(QueueElement, 512)

    def set(self, eos_node: Node) -> bool:
        self.freelist_.free()
        while not self.agenda_.empty():
            self.agenda_.get()
            # make empty

        eos: QueueElement = self.freelist_.alloc()
        eos.node = eos_node
        eos.next = 0
        eos_node.fx = eos.gx = 0
        self.agenda_.put(eos)
        return True

    def next(self) -> bool:
        while not self.agenda_.empty():
            top: QueueElement = self.agenda_.get()
            rnode: Node = top.node

            if rnode.stat == NodeType.MECAB_BOS_NODE:
                n: QueueElement = top  # 선언문
                while n.next:  # 조건문
                    n.node.next = n.next.node
                    n.next.node.prev = n.node
                    n = n.next  # 증감문

                return True

            path: Path = rnode.lpath  # 선언문
            while path:  # 조건문
                n: QueueElement = self.freelist_.alloc()
                n.node = path.lnode
                n.gx = path.cost + top.gx
                n.fx = path.lnode.cost + path.cost + top.gx
                n.next = top
                self.agenda_.put(n)
                path = path.lnext  # 증감문

        return False
