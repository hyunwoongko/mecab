from mecab.allocator import Allocator
from mecab.common import DEFAULT_THETA, MIN_INPUT_BUFFER_SIZE
from mecab.utils.scoped_ptr import ScopedPtr
from mecab.data_structure import Node, Path, RequestType
# import mecab.utils.string_buffer

class Lattice:
    what_ = ""
    feature_constraint_ = []
    boundary_constraint_ = []

    def init(self):
        self.sentence_ = 0
        self.size_ = 0
        self.theta_ = DEFAULT_THETA
        self.Z_ = 0.0
        self.request_type_ = RequestType.MECAB_ONE_BEST

        self.begin_nodes_ = [None for _ in range(MIN_INPUT_BUFFER_SIZE)]
        self.end_nodes_ = [None for _ in range(MIN_INPUT_BUFFER_SIZE)]


        self.allocator_ = ScopedPtr(Allocator(Node, Path))
    
    # 내부 객체 데이터 초기화 메소드
    def clear(self):
        self.allocator_.data.free()
        self.begin_nodes_.clear()
        self.end_nodes_.clear()
        self.feature_constraint_.clear()
        self.boundary_constraint_.clear()
        self.size_ = 0
        self.theta_ = DEFAULT_THETA
        self.Z_ = 0.0
        self.sentence_ = 0

    # 결과 객체가 유효하면 true를 반환
    def is_available(self):
        return self.sentence_ != 0 and len(self.begin_nodes_) != 0 and len(self.end_nodes_) != 0

    # bos(begin of sentence) 노드를 반환
    def bos_nodes(self):
        return self.end_nodes_[0]

    # eos(end of sentence) 노드를 반환
    def eos_node(self):
        return self.begin_nodes_[self.size()]

    def begin_nodes(self):
        pass

    def end_nodes(self):
        pass

    def end_nodes(self, pos: int):
        return self.end_nodes_[pos]

    def begin_nodes(self, pos: int):
        return self.begin_nodes_[pos]
    
    def sentence(self):
        return self.sentence_
    
    def set_sentence(self, sentence: str):
        self.sentence_ = sentence
    
    def set_sentence(self, sentence: str, size: int):
        self.end_nodes_ = [None for _ in range(size)]
        self.begin_nodes_ = [None for _ in range(size)]

        if self.has_request_type(RequestType.MECAB_NBEST) or self.has_request_type(RequestType.MECAB_PARTIAL):
            new_sentence = self.allocator().data.strdup(sentence, size)
            self.sentence_ = new_sentence
        else:
            self.sentence_ = sentence
        
        self.size_ = size
        # std::memset(&end_nodes_[0], 0, sizeof(end_nodes_[0]) * (size + 4))
        # std::memset(&begin_nodes_[0], 0, sizeof(begin_nodes_[0]) * (size + 4))
    
    # Return sentence size
    def size(self) -> int:
        return self.size_

    def Z(self) -> float:
        return self.Z_
    
    def set_Z(self, Z: float):
        self.Z_ = Z
    
    def theta(self) -> float:
        return self.theta_
    
    def set_theta(self, theta: float):
        self.theta_ = theta
    
    def next(self) -> bool:
        if self.has_request_type(RequestType.MECAB_NBEST) != True:
            self.set_what("MECAB_NBEST request type is not set")
            return False
        if self.allocator().nbest_generator().data.next() != True:
            return False
        
        self.buildAllLattice()
        return True
    
    def request_type(self) -> int:
        return self.request_type_
    
    def has_request_type(self, request_type: int) -> bool:
        return request_type and self.request_type_
    
    def set_request_type(self, request_type: int):
        self.request_type_ = request_type

    def add_request_type(self, request_type: int):
        # request_type_ |= request_type
        # self.request_type_ |= request_type
        pass
    
    def remove_request_type(self, request_type: int):
        # request_type_ &= ~request_type
        # self.request_type_ &= ~request_type
        pass
    
    def allocator(self):
        return self.allocator_.data.get()

    def newNode(self) -> Node:
        return self.allocator_.data.newNode()
    
    def has_constraint(self) -> bool:
        pass

    def boundary_constraint(self, pos: int) -> int:
        pass
    
    def set_boundary_constraint(self, pos: int, boundary_constraint_type: type):
        pass

    def feature_constraint(self, pos: int) -> str:
        pass
    
    def setfeature_constraint(self, pos: int, feature_constraint_type: type):
        pass
    
    def set_result(self, result):
        _str = self.allocator_.data.strdup(result, len(result))
        lines = []
        lsize = tokenize(_str, "\n", back_inserter(lines), len(result))
        # ...

    def what(self) -> str:
        return self.what_

    def set_what(self, what: str):
        self.what_ = what

    def create(self):
        return Lattice()
    
    def buildAllLattice(self, lattice) -> bool:
        if lattice.has_request_type(RequestType.MECAB_ALL_MORPHS) != True:
            return True
        
        prev = lattice.bos_nodes()
        _len = lattice.size()
        begin_node_list = lattice.begin_nodes()

        pos = 0
        while(pos <= size):
            for node in begin_node_list[pos]:
                prev.next = node
                node.prev = prev
                prev = node
            pos += 1
        
        return True
