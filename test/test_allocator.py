import unittest

from mecab.allocator import Allocator

class TestAllocator(unittest.TestCase):

    def test_generator(self):
        allocator = Allocator(int, int)
        print("nbest_generator_: ", allocator.nbest_generator())
        print("results_: ", allocator.mutable_results())

        allocator.newPath()
        print("path_freelist_: "), allocator.print_path_freelist()
        allocator.newNode()
        print("id_: "), allocator.print_id()
        print("node_freelist_: "), allocator.print_node_freelist()
        

        print("mutable_results(): "), allocator.mutable_results()

        print("alloc(): ", allocator.alloc(size=0))
        print("char_freelist_: "), allocator.print_char_freelist()
        print("alloc(): ", allocator.alloc(size=1))
        print("char_freelist_: "), allocator.print_char_freelist()

        print("strdup(): ", allocator.strdup("Test Allocator", size=10))

        print("nbest_generator(): ", allocator.nbest_generator())

        print("partial_buffer(): ", allocator.partial_buffer(size=1))

        print("results_size(): ", allocator.results_size())

        allocator.free()
        print("id_: "), allocator.print_id()
        print("node_freelist_: "), allocator.print_node_freelist()
        # self.path_freelist_.get() 부분이 제대로 동작 안하는 듯 합니다.
        print("node_freelist_: "), allocator.print_path_freelist()
        # self.char_freelist_.get() 부분이 제대로 동작 안하는 듯 합니다.
        print("char_freelist_: "), allocator.print_char_freelist()


if __name__ == '__main__':
    test = unittest.defaultTestLoader.loadTestsFromTestCase(TestAllocator)
    unittest.TextTestRunner().run(test)
