from mecab.utils.scoped_ptr import ScopedPtr
from mecab.utils.scoped_ptr import ScopedString
from mecab.utils.scoped_ptr import ScopedArray
from mecab.utils.scoped_ptr import ScopedFixedArray


class foo:
    def print(self) -> None:
        print('foo.print()')

    def call_by_reference(self, ptr) -> None:
        ptr.data = 44444


if __name__ == '__main__':
    # scored_ptr-----------
    a = ScopedPtr(11111)
    ptr = ScopedPtr()

    ptr.reset(a)
    ptr.get().data = 22222

    print(ptr.get().data)
    print(a.data)

    temp = ptr.get()
    temp.data = 33333

    print(ptr.get().data)
    print(a.data)

    foo_test = foo()
    foo_test.call_by_reference(ptr.get())

    print(ptr.get().data)
    print(a.data)

    b = ScopedPtr(foo())
    ptr.reset(b)

    ptr.get().data.print()

    # scored_string-----------
    str1 = ScopedString("origin")
    str2 = ScopedString()
    str2.reset_string(str1)

    print(str1.data)
    print(str1.get().data)
    print(str2.get().data)

    str2.get().data = "modify"
    print(str1.get().data)
    print(str2.get().data)

    str2.reset_string()
    # print(str2.get().data)
    if (str2.get() is not None):
        print(str2.get().data)
    else:
        print("str2 is None")

    # scored_array-----------
    array = ScopedArray()
    q = ScopedPtr(1)
    w = ScopedPtr(2)
    e = ScopedPtr(3)
    array.append(q)
    array.append(w)
    array.append(e)
    # array.append(3)
    for ptr in array.get():
        print(ptr.data)

    for ptr in array.get():
        ptr.data += 1

    print('-------------')
    print(q.data, w.data, e.data)

    # scored_fixed_array-----------
    fixed_array = ScopedFixedArray(5)
    print(fixed_array.get())
    # fixed_array.append(scoped_ptr(1))