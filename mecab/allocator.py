from mecab.common import BUF_SIZE, NODE_FREELIST_SIZE, PATH_FREELIST_SIZE
from mecab.nbest_generator import NBestGenerator
from mecab.utils.scoped_ptr import ScopedPtr, ScopedArray
from mecab.utils.freelist import FreeList, ChunkFreeList

class Allocator:
    _kResultsSize = 512
    _partial_buffer_ = []

    def __init__(self, typeN: type, typeP: type):
        self._type_n = typeN
        self._type_p = typeP

        # member
        self._id_ = 0
        self._node_freelist_ = ScopedPtr(FreeList(type_=typeN, size=NODE_FREELIST_SIZE))
        self._path_freelist_ = ScopedPtr(FreeList(type_=typeP, size=0))
        self._char_freelist_ = ScopedPtr(ChunkFreeList(type_=str, size=0))
        self._nbest_generator_ = ScopedPtr(NBestGenerator())
        self._results_ = ScopedArray(type_=str, size=self._kResultsSize)
        # self._results_ = ScopedArray()

    def newNode(self):
        """[summary]
            add an element to node_freelist_
            then increase id_
        
        Returns:
            [typeN]: [description]
        """
        self._node_freelist_.data.alloc()
        self._id_ = self._id_ + 1
        return self._node_freelist_.data

    def newPath(self):
        """[summary]
            add an element to path_freelist_
        
        Returns:
            [typeP]: [description]
        """
        if self._path_freelist_.get() != None:
            self._path_freelist_.reset(FreeList(type_=self._type_p, size=PATH_FREELIST_SIZE))
        self._path_freelist_.data.alloc()
        return self._path_freelist_.data

    def mutable_results(self) -> list:
        """[summary]
            ...
        Returns:
            [list]: [description]
        """
        return self._results_.get()

    def alloc(self, size: int) -> list:
        if self._char_freelist_.get() != None:
            self._char_freelist_.reset(ChunkFreeList(type_=str, size=BUF_SIZE))
        self._char_freelist_.data.alloc(size + 1)
        return self._char_freelist_.data
    
    # python에서는 size의 의미가 필요한가 싶네요.
    def strdup(self, str_: str, size: int) -> str:
        n_str = str_
        return n_str
    
    def nbest_generator(self) -> NBestGenerator:
        if self._nbest_generator_.get() != None:
            self._nbest_generator_.reset(NBestGenerator())
        return self._nbest_generator_.get()
    
    def partial_buffer(self, size: int) -> str:
        if len(self._partial_buffer_) == 0:
            self._partial_buffer_ = ['' for _ in range(size)]
        else:
            self._partial_buffer_ = self._partial_buffer_[:(size + 1)]
        return self._partial_buffer_[0]
    
    def results_size(self) -> int:
        return self._kResultsSize

    def free(self):
        self._id_ = 0
        self._node_freelist_.data.free()
        if self._path_freelist_.get() != None:
            # self._path_freelist_.get() 부분에 데이터가 제대로 확인 안됨.
            self._path_freelist_.data.free()
        if self._char_freelist_.get() != None:
            # self._char_freelist_.get() 부분에 데이터가 제대로 확인 안됨.
            self._char_freelist_.data.free()
    
    # only debugging
    def print_node_freelist(self):
        print(self._node_freelist_.data)
    
    def print_path_freelist(self):
        print(self._path_freelist_.data)
    
    def print_char_freelist(self):
        print(self._char_freelist_.data)
    
    def print_id(self):
        print(self._id_)