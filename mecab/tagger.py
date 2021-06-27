from typing import List
from threading import Lock

from warnings import warn
from multipledispatch import dispatch

from mecab.common import DEFAULT_THETA
from mecab.data_structure import DictionaryInfo, Node, RequestType
from mecab.lattice import Lattice
from mecab.model import Model
from mecab.tagger import Tagger
from mecab.utils.param import Param
from mecab.utils.scoped_ptr import ScopedPtr

class Tagger:
    _current_model_: Model
    _mutex_: Lock
    
    _model_: ScopedPtr
    _lattice_: ScopedPtr
    _request_type_: int
    _theta_: float
    _what_: str

    def __init__(self):
        self._current_model_ = Model(0)
        self._mutex_ = Lock()

        self._model_ = ScopedPtr(Model())
        self._lattice_ = ScopedPtr(Lattice())
        self._request_type_ = RequestType.MECAB_ONE_BEST
        self._theta_ = DEFAULT_THETA
        self._what_ = ""

    @dispatch(int, List[str])
    def create(self, argc: int, argv: List[str]) -> Tagger:
        """
        Factory method to create a new Tagger with a specified main's argc/argv-style parameters.
        Return NULL if new model cannot be initialized.
        @return new Tagger object
        @param argc number of parameters
        @param argv parameter list
        """
        tagger = Tagger()
        if not tagger.open(argc, argv):
            warn(tagger.what())
            del tagger
            return 0
        return tagger
    
    @dispatch(str)
    def create(self, argv: str) -> Tagger:
        """
        Factory method to create a new Tagger with a string parameter representation, i.e.,
        "-d /user/local/mecab/dic/ipadic -Ochasen".
        Return NULL if new model cannot be initialized.
        @return new Model object
        @param arg single string representation of the argment.
        """ 
        tagger = Tagger()
        if not tagger.open(argv):
            warn(tagger.what())
            del tagger
            return 0
        return tagger # @return new Model object?
    
    @dispatch(Model)
    def create(self, model: Model) -> Tagger:
        if not model.is_available():
            warn("Model is not available")
            return 0
        
        tagger = Tagger()
        if not tagger.open(model):
            warn(tagger.what())
            del tagger
            return 0
        
        tagger.set_theta(model.theta())
        tagger.set_request_type(model.request_type())
        return tagger

    def version(self):
        """
        Return a version string
        @return version string
        """
        return self._model().dictionary_info().VERSION # version of this dictionary

    @dispatch(int, List[str])
    def open(self, argc: int, argv: List[str]) -> bool:
        self._model_.reset(Model())
        if not self._model_.open(argc, argv):
            self._model_.reset(0)
            return False

        self._current_model_ = self._model_.get()
        self._request_type_ = self._model().request_type()
        self._theta_ = self._model().theta()
        return True
    
    @dispatch(str)
    def open(self, arg: str) -> bool:
        self._model_.reset(Model())
        if not self._model_.open(arg):
            self._model_.reset(0)
            return False

        self._current_model_ = self._model_.get()
        self._request_type_ = self._model().request_type()
        self._theta_ = self._model().theta()
        return True
    
    @dispatch(Model)
    def open(self, model: Model) -> bool:
        if not model.is_available():
            return False
        
        self._model_.reset(0)
        self._current_model_ = Model()
        self._request_type_ = self._current_model_.request_type()
        self._theta_ = self._current_model_.theta()
        return True

    @dispatch(Model, Lattice)
    def parse(self, model: Model, lattice: Lattice) -> bool:
        """
        Handy static method.
        Return true if lattice is parsed successfully.
        This function is equivalent to
        {
            Tagger *tagger = model.createModel();
            cosnt bool result = tagger->parse(lattice);
            delete tagger;
            return result;
        }
        @return boolean
        """
        tagger = Tagger().create(model)
        return tagger.parse(lattice)

    @dispatch(Lattice)
    def parse(self, lattice: Lattice) -> bool:
        """
        Parse lattice object.
        Return true if lattice is parsed successfully.
        A sentence must be set to the lattice with Lattice:set_sentence object before calling this method.
        Parsed node object can be obtained with Lattice:bos_node.
        This method is thread safe.
        @return lattice lattice object
        @return boolean
        """
        self._mutex_.locked()
        return self._model().viterbi().analyze()

    @dispatch(str)
    def parse(self, str_: str) -> str:
        """
        Parse given sentence and return parsed result as string.
        You should not delete the returned string. The returned buffer
        is overwritten when parse method is called again.
        This method is NOT thread safe.
        @param str sentence
        @return parsed result
        """
        return self.parse(str_, len(str_))

    @dispatch(str)
    def parseToNode(self, str_: str) -> Node:
        """
        Parse given sentence and return Node object.
        You should not delete the returned node object. The returned buffer
        is overwritten when parse method is called again.
        You can traverse all nodes via Node::next member.
        This method is NOT thread safe.
        @param str sentence
        @return bos node object
        """
        return self.parseToNode(str_, len(str_))

    @dispatch(int, str)
    def parseNBest(self, N: int, str_: str) -> str:
        """
        Parse given sentence and obtain N-best results as a string format.
        Currently, N must be 1 <= N <= 512 due to the limitation of the buffer size.
        You should not delete the returned string. The returned buffer
        is overwritten when parse method is called again.
        This method is DEPRECATED. Use Lattice class.
        @param N how many results you want to obtain
        @param str sentence
        @return parsed result
        """
        return self.parseNBest(N, str_, len(str_))

    @dispatch(str)
    def parseNBestInit(self, str_: str) -> bool:
        """
        Initialize N-best enumeration with a sentence.
        Return true if initialization finishes successfully.
        N-best result is obtained by calling next() or nextNode() in sequence.
        This method is NOT thread safe.
        This method is DEPRECATED. Use Lattice class.
        @param str sentence
        @return boolean
        """
        return self.parseNBestInit(str_, len(str_))

    def nextNode(self) -> Node:
        """
        Return next-best parsed result. You must call parseNBestInit() in advance.
        Return NULL if no more reuslt is available.
        This method is NOT thread safe.
        This method is DEPRECATED. Use Lattice class.
        @return node object
        """
        lattice = self._mutable_lattice()
        if not lattice.next():
            lattice.set_what("no more results")
            return 0
        return lattice.bos_nodes() # bos_node() ?

    @dispatch
    def next(self) -> str:
        """
        Return next-best parsed result. You must call parseNBestInit() in advance.
        Return NULL if no more reuslt is available.
        This method is NOT thread safe.
        This method is DEPRECATED. Use Lattice class.
        @return parsed result
        """
        lattice = self._mutable_lattice()
        if not lattice.next():
            lattice.set_what("no more results")
            return 0

        result = self._model().writer().stringify_lattice(lattice)
        if not result:
            self._set_what(lattice.what())
            return 0
        return result

    @dispatch(Node)
    def formatNode(self, node: Node) -> str:
        """
        Return formatted node object. The format is specified with
        --unk-format, --bos-format, --eos-format, and --eon-format respectively.
        You should not delete the returned string. The returned buffer
        is overwritten when parse method is called again.
        This method is NOT thread safe.
        This method is DEPRECATED. Use Lattice class.
        @param node node object.
        @return parsed result
        """
        result = self._model().writer().stringify_lattice(self._mutable_lattice(), node)
        if not result:
            self._set_what(self._mutable_lattice().what())
            return 0
        return result

    @dispatch(str, int, str, int)
    def parse(self, str_: str, len_: int, ostr: str, olen: int) -> str:
        """
        The same as parse() method, but input length and output buffer are passed.
        Return parsed result as string. The result pointer is the same as |ostr|.
        Return NULL, if parsed result string cannot be stored within |olen| bytes.
        @param str sentence
        @param len sentence length
        @param ostr output buffer
        @param olen output buffer length
        @return parsed result
        """
        lattice = self._mutable_lattice()
        self._init_request_type()
        lattice.set_sentence(str_, len_)
        if not self.parse(lattice):
            self._set_what(lattice.what())
            return 0
        
        result = self._model().writer().stringify_lattice(lattice, ostr, olen)
        if not result:
            self._set_what(lattice.what())
            return 0

        return result

    @dispatch(str, int)
    def parse(self, str_: str, len_: int) -> str:
        """
        The same as parse() method, but input length can be passed.
        @param str sentence
        @param len sentence length
        @return parsed result
        """
        lattice = self._mutable_lattice()
        self._init_request_type()
        lattice.set_sentence(str_, len_)
        if not self.parse(lattice):
            self._set_what(lattice.what())
            return 0
        
        result = self._model().writer().stringify_lattice(lattice)
        if not result:
            self._set_what(lattice.what())
            return 0

        return result

    @dispatch(str, int)
    def parseToNode(self, str_: str, len_=0) -> Node:
        """
        The same as parseToNode(), but input lenth can be passed.
        @param str sentence
        @param len sentence length
        @return node object
        """
        lattice = self._mutable_lattice()
        self._init_request_type()
        lattice.set_sentence(str_, len_)
        if not self.parse(lattice):
            self._set_what(lattice.what())
            return 0
        return lattice.bos_nodes() # bos_node() ?

    @dispatch(int, str, int)
    def parseNBest(self, N: int, str_: str, len_: int) -> str:
        """
        The same as parseNBest(), but input length can be passed.
        @param N how many results you want to obtain
        @param str sentence
        @param len sentence length
        @return parsed result
        """
        lattice = self._mutable_lattice()
        self._init_request_type()
        lattice.add_request_type(RequestType.MECAB_NBEST)
        lattice.set_sentence(str_, len_)

        if not self.parse(lattice):
            self._set_what(lattice.what())
            return 0
        
        result = self._model().writer().stringify_lattice_nbest(lattice, N)
        if not result:
            self._set_what(lattice.what())
            return 0
        
        return result

    @dispatch(str, int)
    def parseNBestInit(self, str_: str, len_: int) -> bool:
        """
        The same as parseNBestInit(), but input length can be passed.
        @param str sentence
        @param len sentence length
        @return boolean
        @return parsed result
        """
        lattice = self._mutable_lattice()
        self._init_request_type()
        lattice.add_request_type(RequestType.MECAB_NBEST)
        lattice.set_sentence(str_, len_)

        if not self.parse(lattice):
            self._set_what(lattice.what())
            return False

        return True

    @dispatch(str, int)
    def next(self, ostr: str, olen: int) -> str:
        """
        The same as next(), but output buffer can be passed.
        Return NULL if more than |olen| buffer is required to store output string.
        @param ostr output buffer
        @param olen output buffer length
        @return parsed result
        """
        lattice = self._mutable_lattice()
        if not lattice.next():
            lattice.set_what("no more results")
            return 0

        result = self._model().writer().stringify_lattice(lattice, ostr, olen)
        if not result:
            self._set_what(lattice.what())
            return 0
        
        return result

    @dispatch(int, str, int, str, int)
    def parseNBest(self, N: int, str_: str, len_: int, ostr: str, olen: int) -> str:
        """
        The same as parseNBest(), but input length and output buffer can be passed.
        Return NULL if more than |olen| buffer is required to store output string.
        @param N how many results you want to obtain
        @param str input sentence
        @param len input sentence length
        @param ostr output buffer
        @param olen output buffer length
        @return parsed result
        """
        lattice = self._mutable_lattice()
        self._init_request_type()
        lattice.add_request_type(RequestType.MECAB_NBEST)
        lattice.set_sentence(str_, len_)

        if not self.parse(lattice):
            self._set_what(lattice.what())
            return 0
        
        result = self._model().writer().stringify_lattice_nbest(lattice, N, ostr, olen)
        if not result:
            self._set_what(lattice.what())
            return 0
        
        return result

    @dispatch(Node)
    def formatNode(self, node: Node, ostr: str, olen: int) -> str:
        """
        The same as formatNode(), but output buffer can be passed.
        Return NULL if more than |olen| buffer is required to store output string.
        @param node node object
        @param ostr output buffer
        @param olen output buffer length
        @return parsed result
        """
        result = self._model().writer().stringify_lattice(self._mutable_lattice(), node, ostr, olen)
        if not result:
            self._set_what(self._mutable_lattice().what())
            return 0
        return result

    def set_request_type(self, request_type: int):
        """
        Set request type.
        This method is DEPRECATED. Use Lattice::set_request_type(MECAB_PARTIAL).
        @param request_type new request type assigned
        """
        self._request_type_ = request_type

    def request_type(self) -> int:
        """
        Return the current request type.
        This method is DEPRECATED. Use Lattice class.
        @return request type
        """
        return self._request_type_

    def partial(self) -> bool:
        """
        Return true if partial parsing mode is on.
        This method is DEPRECATED. Use Lattice::has_request_type(MECAB_PARTIAL).
        @return boolean
        """
        return bool(self._request_type_ & RequestType.MECAB_PARTIAL)

    def set_partial(self, partial: bool):
        """
        set partial parsing mode.
        This method is DEPRECATED. Use Lattice::add_request_type(MECAB_PARTIAL) or
        Lattice::remove_request_type(MECAB_PARTIAL)
        @param partial partial mode
        """
        if partial:
            self._request_type_ = self._request_type_ | RequestType.MECAB_PARTIAL
        else:
            self._request_type_ = self._request_type_ & ~RequestType.MECAB_PARTIAL

    def lattice_level(self) -> int:
        """
        Return lattice level.
        This method is DEPRECATED. Use Lattice::*_request_type()
        @return int lattice level
        """
        if self._request_type_ & RequestType.MECAB_MARGINAL_PROB:
            return 2
        elif self._request_type_ & RequestType.MECAB_NBEST:
            return 1
        else:
            return 0

    def set_lattice_level(self, level: int):
        """
        Set lattice level.
        This method is DEPRECATED. Use Lattice::*_request_type()
        @param level lattice level
        """
        if level == 0:
            self._request_type_ = self._request_type_ | RequestType.MECAB_ONE_BEST
        elif level == 1:
            self._request_type_ = self._request_type_ | RequestType.MECAB_NBEST
        elif level == 2:
            self._request_type_ = self._request_type_ | RequestType.MECAB_MARGINAL_PROB

    def all_morphs(self) -> bool:
        """
        Return true if all morphs output mode is on.
        This method is DEPRECATED. Use Lattice::has_request_type(MECAB_ALL_MORPHS).
        @return boolean
        """
        return bool(self._request_type_ & RequestType.MECAB_ALL_MORPHS)

    def set_all_morphs(self, all_morphs):
        """
        set all-morphs output mode.
        This method is DEPRECATED. Use Lattice::add_request_type(MECAB_ALL_MORPHS) or
        Lattice::remove_request_type(MECAB_ALL_MORPHS)
        @param all_morphs
        """
        if all_morphs:
            self._request_type_ = self._request_type_ | RequestType.MECAB_ALL_MORPHS
        else:
            self._request_type_ = self._request_type_ & ~RequestType.MECAB_ALL_MORPHS

    def set_theta(self, theta: float):
        """
        Set temparature parameter theta.
        @param theta temparature parameter.
        """
        self._theta_ = theta

    def theta(self) -> float:
        """
        Return temparature parameter theta.
        @return temparature parameter.
        """
        return self._theta_

    def dictionary_info(self):
        """
        Return DictionaryInfo linked list.
        @return DictionaryInfo linked list
        """
        return self._model().dictionary_info()

    def what(self) -> str:
        """
        Return error string.
        @return error string
        """
        return self._what_

    # @private

    def _model(self) -> Model:
        return self._current_model_

    def _set_what(self, what: str):
        self._what_ = what

    def _init_request_type(self):
        self._mutable_lattice().set_request_type(self._request_type_)
        self._mutable_lattice().set_theta(self._theta_)

    def _mutable_lattice(self) -> Lattice:
        if not self._lattice_.get():
            self._lattice_.reset(self._model().create_lattice())
        return self._lattice_.get()
