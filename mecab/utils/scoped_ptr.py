from collections import deque, UserList
import ctypes


class ScopedPtr:
    """
    "scoped_ptr<param> ptr"은 scoped_ptr ptr로 사용한다.

    constructor : value로 쓸 것인지 pointer로 쓸 것인지 결정해야한다.
        a = scoped_ptr(11111) : value
        ptr = scoped_ptr() : pointer
        
    reset : 가르키는 대상 변경 및 기존 데이터 삭제한다.
        ptr.reset(a)
        
    get : 가르키는 대상을 반환 (메모리의 주소라고 생각), 실제로는 value로 사용된 scoped_ptr이다.
        temp = ptr.get()
        temp.data = 33333 ( = ptr.get().data, = a.data )

    원본 scoped_ptr의 operator*()는 "ptr.get().data"와 동일하다
                     operator->()는 "ptr.get()."와 동일하다.
    """
    __next = deque([], maxlen=1)

    def __init__(self, data=None):
        self.data = data

    def reset(self, data=None) -> None:
        if self.data is not None:
            raise Exception('Reset failed. This is not a pointer. Please delete the data.')

        self.__next.clear()
        if data is not None:
            self.__next.append(data)

    def get(self):
        if len(self.__next) == 0:
            return None

        return self.__next[0]


class ScopedArray:
    __array = []

    def __init__(self, type_: type, size: int):
        self.type = type_
        self.__array = [None for _ in range(size)]

    def append(self, data):
        if str(type(data)) != "<class 'mecab.utils.scoped_ptr.ScopedPtr'>":
            raise Exception('append failed. Please put only ScoredPtr type')

        self.__array.append(data)

    def get(self):
        return self.__array


class ScopedFixedArray(UserList):
    __size: int

    def __init__(self, size: int):
        self.__size = size
        self.__array = [None] * size

    def append(self, data):
        raise Exception(f"exceed the limit.[{self.n}]")

    def get(self):
        return self.__array

    def size(self):
        return self.__size


class ScopedString(ScopedPtr):
    # scoped_fixed_array<data_type, size>
    # -> array = scoped_fixed_array(size)

    def __init__(self, data=None):
        super().__init__(data)

    def reset_string(self, data=None):
        super().reset(data)
