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
    _next = deque([], maxlen=1)

    def __init__(self, data=None):
        self.data = data

    def reset(self, data=None) -> None:
        if self.data is not None:
            raise Exception(
                'Reset failed. This is not a pointer. Please delete the data.')

        self._next.clear()
        if data is not None:
            self._next.append(data)

    def get(self):
        if len(self._next) == 0:
            return None

        return self._next[0]


class ScopedArray:
    _array = []

    def __init__(self, type_: type, size: int):
        self.type = type_
        self._array = [None for _ in range(size)]

    def append(self, data):
        if str(type(data)) != "<class 'mecab.utils.scoped_ptr.ScopedPtr'>":
            raise Exception('append failed. Please put only ScoredPtr type')

        self._array.append(data)

    def get(self):
        return self._array

    def __getitem__(self, index):
        return self._array[index]


class ScopedFixedArray(UserList):
    _size: int

    def __init__(self, size: int):
        super(ScopedFixedArray, self).__init__()
        self._size = size
        self._array = [None] * size

    def append(self, data):
        raise Exception(f"exceed the limit.[{self.n}]")

    def get(self):
        return self._array

    def size(self):
        return self._size

    def __getitem__(self, index):
        return self._array[index]


class ScopedString(ScopedPtr):
    # scoped_fixed_array<data_type, size>
    # -> array = scoped_fixed_array(size)

    def __init__(self, data=None):
        super().__init__(data)

    def reset_string(self, data=None):
        super().reset(data)
