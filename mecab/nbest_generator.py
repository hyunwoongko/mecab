from typing import List

from mecab.data_structure import Node, NodeType
from mecab.utils.freelist import FreeList
from queue import PriorityQueue


class QueueElement:

    def __init__(self):
        self.node = Node()
        self.next: QueueElement
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
