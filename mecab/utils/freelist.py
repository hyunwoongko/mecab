from typing import List


class FreeList(object):

    def __init__(self, type_: type, size: int):
        self.free_list = []
        self.pi_: int = 0
        self.li_: int = 0
        self.size: int = size
        self.type = type_

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
            self.free_list.append([self.type()] * self.size)
            # freeList.push_back(new T[size]);

        obj = self.free_list[self.li_][self.pi_]
        self.pi_ += 1
        return obj
        # return freeList[li_] + (pi_++);

    def __repr__(self):
        return str(self.free_list)


class ChunkFreeList:

    def __init__(self, type_: type, size: int):
        self.free_list = []
        self.pi_: int = 0
        self.li_: int = 0
        self.default_size: int = size
        self.type = type_

    def free(self):
        """
        make list free.
        """
        self.pi_ = self.li_ = 0

    def alloc(self, req=1):
        """
        allocate new element to list
        """
        while self.li_ < len(self.free_list):
            if self.pi_ + req < self.free_list[self.li_][0]:
                r = self.free_list[self.li_][1][self.pi_]
                # T* r = freelist_[li_].second + pi_;
                # 포인터이기 때문에 pi_만큼 주소를 뒤로 이동
                self.pi_ += req
                return r

            self.li_ += 1
            self.pi_ = 0

        _size = max(req, self.default_size)
        self.free_list.append((_size, [self.type()] * _size))
        self.li_ = len(self.free_list) - 1
        self.pi_ += req

        return self.free_list[self.li_][1]

    def __repr__(self):
        return str(self.free_list)
