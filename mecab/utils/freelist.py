from typing import TypeVar, Generic, List

T = TypeVar('T')


class FreeList(Generic[T]):

    def __init__(self):
        self.free_list: List[T] = []
        self.pi_: int = 0
        self.li_: int = 0
        self.size: int = 0

    def free(self):
        """
        make list free.
        """
        self.pi_ = self.li_ = 0

    def alloc(self):
        """
        allocate new element to list
        """
        if self.pi_ == self.size:
            self.li_ += 1
            self.pi_ = 0

        if self.li_ == len(self.free_list):
            self.free_list.append(T())

        self.pi_ += 1
        return self.free_list[self.li_] + self.pi_

