import unittest

from mecab.allocator import Allocator

class TestAllocator(unittest.TestCase):

    def test_generator(self):
        allocator = Allocator(int, int)
        print("type_n: ", allocator.type_n)
        print("type_p: ", allocator.type_p)
        print("kResultsSize: ", allocator.kResultsSize)
        print("partial_buffer_: ", allocator.partial_buffer_)
        print("id_: ", allocator.id_)

        print("node_freelist_: ", allocator.node_freelist_.data)
        print("path_freelist_: ", allocator.path_freelist_.data)
        print("char_freelist_: ", allocator.char_freelist_.data)
        print("nbest_generator_: ", allocator.nbest_generator_.get())
        print("results_: ", allocator.results_.get())

        allocator.newPath()
        print("path_freelist_: ", allocator.path_freelist_.data)
        allocator.newNode()
        print("id_: ", allocator.id_)
        print("node_freelist_: ", allocator.node_freelist_.data)

        print("mutable_results(): ", allocator.mutable_results())

        print("alloc(): ", allocator.alloc(size=0))
        print("char_freelist_: ", allocator.char_freelist_.data)
        print("alloc(): ", allocator.alloc(size=1))
        print("char_freelist_: ", allocator.char_freelist_.data)

        print("strdup(): ", allocator.strdup("Test Allocator", size=10))

        print("nbest_generator(): ", allocator.nbest_generator())

        print("partial_buffer(): ", allocator.partial_buffer(size=1))

        print("results_size(): ", allocator.results_size())

        allocator.free()
        print("id_: ", allocator.id_)
        print("node_freelist_: ", allocator.node_freelist_.data)
        # self.path_freelist_.get() 부분이 제대로 동작 안하는 듯 합니다.
        print("path_freelist_: ", allocator.path_freelist_.data)
        # self.char_freelist_.get() 부분이 제대로 동작 안하는 듯 합니다.
        print("char_freelist_: ", allocator.char_freelist_.data)


if __name__ == '__main__':
    test = unittest.defaultTestLoader.loadTestsFromTestCase(TestAllocator)
    unittest.TextTestRunner().run(test)
