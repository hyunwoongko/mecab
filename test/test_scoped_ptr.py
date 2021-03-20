from mecab.scoped_ptr import scoped_ptr
from mecab.scoped_ptr import scoped_string
from mecab.scoped_ptr import scoped_array
from mecab.scoped_ptr import scoped_fixed_array


class foo:
    def print(self) -> None:
        print('foo.print()')

    def call_by_reference(self, ptr) -> None:
        ptr.data = 44444


if __name__ == '__main__':
    # scored_ptr-----------
    a = scoped_ptr(11111)
    ptr = scoped_ptr()

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

    b = scoped_ptr(foo())
    ptr.reset(b)

    ptr.get().data.print()

    # scored_string-----------
    str1 = scoped_string("origin")
    str2 = scoped_string()
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
    array = scoped_array()
    q = scoped_ptr(1)
    w = scoped_ptr(2)
    e = scoped_ptr(3)
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
    fixed_array = scoped_fixed_array(5)
    print(fixed_array.get())
    # fixed_array.append(scoped_ptr(1))