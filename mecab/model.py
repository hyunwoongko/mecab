import logging
from typing import List
from threading import Lock, Thread

from multipledispatch import dispatch

from mecab.common import CHECK_FALSE
from mecab.data_structure import Node, RequestType, DictionaryInfo
from mecab.lattice import Lattice
from mecab.model import Model
from mecab.utils.io import load_dictionary_resource
from mecab.utils.param import Param, Option
from mecab.utils.scoped_ptr import ScopedPtr
from mecab.viterbi import Viterbi
from mecab.writer import Writer

logger = logging.getLogger(__file__)

def get_request_type(allocate_sentence: bool, partial: bool, all_morphs: bool, marginal: bool, nbest: int) -> int:
    request_type = RequestType.MECAB_ONE_BEST
    if allocate_sentence:
        request_type |= RequestType.MECAB_ALLOCATE_SENTENCE

    if partial:
        request_type |= RequestType.MECAB_PARTIAL

    if all_morphs:
        request_type |= RequestType.MECAB_ALL_MORPHS

    if marginal:
        request_type |= RequestType.MECAB_MARGINAL_PROB

    if nbest >= 2:
        request_type |= RequestType.MECAB_NBEST

    return request_type

mecab_options = [
    Option("rcfile", 'r', "", "FILE", "use FILE as resource file"),
    Option("dicdir", 'd', "", "DIR", "set DIR  as a system dicdir"),
    Option("userdic", 'u', "", "FILE", "use FILE as a user dictionary"),
    Option("lattice-level", 'l', "0", "INT", "lattice information level (DEPRECATED)"),
    Option("dictionary-info", 'D', "", "", "show dictionary information and exit"),
    Option("output-format-type", 'O', "", "TYPE", "set output format type (wakati,none,...)"),
    Option("all-morphs", 'a', "", "", "output all morphs(default false)"),
    Option("nbest", 'N', "1", "INT", "output N best results (default 1)"),
    Option("partial", 'p', "", "", "partial parsing mode (default false)"),
    Option("marginal", 'm', "", "", "output marginal probability (default false)"),
    Option("max-grouping-size", 'M', "24", "INT", "maximum grouping size for unknown words (default 24)"),
    Option("node-format", 'F', "%m\\t%H\\n", "STR", "use STR as the user-defined node format"),
    Option("unk-format", 'U', "%m\\t%H\\n", "STR", "use STR as the user-defined unknown node format"),
    Option("bos-format", 'B', "", "STR", "use STR as the user-defined beginning-of-sentence format"),
    Option("eos-format", 'E', "EOS\\n", "STR", "use STR as the user-defined end-of-sentence format"),
    Option("eon-format", 'S', "", "STR", "use STR as the user-defined end-of-NBest format"),
    Option("unk-feature", 'x', "", "STR", "use STR as the feature for unknown word"),
    Option("input-buffer-size", 'b', "", "INT", "set input buffer size (default 8192)"),
    Option("dump-config", 'P', "", "", "dump MeCab parameters"),
    Option("allocate-sentence", 'C', "", "", "allocate new memory for input sentence"),
    Option("theta", 't', "0.75", "FLOAT", "set temparature parameter theta (default 0.75)"),
    Option("cost-factor", 'c', "700", "INT", "set cost factor (default 700)"),
    Option("output", 'o', "", "FILE", "set the output file name")
    ]

class Model:
    _viterbi_: Viterbi
    _mutex_: Lock
    _writer_: ScopedPtr
    _request_type_: int
    _theta_: float

    def __init__(self):
        self._viterbi_ = Viterbi()
        self._writer_ = ScopedPtr(Writer())
        self._request_type_ = RequestType.MECAB_ONE_BEST
        self._theta_ = 0.0
        self.mutex = Lock()

    def __del__(self):
        self._viterbi_.free()
        self._viterbi_ = 0

    @dispatch(int, List[str])
    def open(self, argc: int, argv: List[str]) -> bool:
        param = Param()
        if ((not param.parse(argc, argv, mecab_options)) or (not load_dictionary_resource(param))):
            return False

        return open(param)

    @dispatch(str)
    def open(self, arg: str) -> bool:
        param = Param()
        if ((not param.parse(arg, mecab_options)) or (not load_dictionary_resource(param))):
            return False

        return open(param)

    @dispatch(Param)
    def open(self, param: Param) -> bool:
        CHECK_FALSE(self._writer_.open(param) and self._viterbi_.open(param))

        self._request_type_ = get_request_type(param.get("allocate-sentence"), param.get("partial"),
                                             param.get("all-morphs"), param.get("marginal"), param.get("nbest"))
        self._theta_ = param.get("theta")

        return self.is_available()

    def version(self) -> str:
        """
        Return a version string
        @return version string
        """
        return DictionaryInfo.VERSION  ## version of this dictionary

    @dispatch(int, List[str])
    def create(self, argc: int, argv: List[str]) -> Model:
        """
        Factory method to create a new Model with a specified main's argc/argv-style parameters.
        Return NULL if new model cannot be initialized.
        @return new Model object
        @param argc number of parameters
        @param argv parameter list
        """
        model = Model()
        if not model.open(argc, argv):
            model.clear()
            return 0
        return model

    @dispatch(str)
    def create(self, arg: str) -> Param:
        """
        Factory method to create a new Model with a string parameter representation, i.e.,
        "-d /user/local/mecab/dic/ipadic -Ochasen".
        Return NULL if new model cannot be initialized.
        @return new Model object
        @param arg single string representation of the argment.
        """
        model = Model()
        if not model.open(arg):
            model.clear()
            return 0
        return model

    @dispatch(Param)
    def create(self, param: Param) -> Model:
        model = Model()
        if not model.open(param):
            model.clear()
            return 0
        return model

    def dictionary_info(self) -> DictionaryInfo:
        """
        Return DictionaryInfo linked list.
        @return DictionaryInfo linked list
        """
        return self._viterbi_.tokenizer_ if self._viterbi_.tokenizer_.dictionary_info() else 0

    def transition_cost(self, rcAttr: int, lcAttr: int) -> int:
        """
        Return transtion cost from rcAttr to lcAttr.
        @return transtion cost
        """
        return self._viterbi_.connector_().transition_cost(rcAttr, lcAttr)

    def lookup(self, begin: str, end: str, lattice: Lattice) -> Node:
        """
        perform common prefix search from the range [begin, end).
        |lattice| takes the ownership of return value.
        @return node linked list.
        """
        return self._viterbi_.tokenizer_.lookup(begin, end, lattice.allocator(), lattice)

    def create_lattice(self) -> Lattice:
        """
        Create a new Lattice object.
        @return new Lattice object
        """
        if not self.is_available():
            logger.error("Model is not available")
            return 0
        return Lattice()

    def swap(self, model: Model) -> bool:
        """
        Swap the instance with |model|.
        The ownership of |model| always moves to this instance,
        meaning that passed |model| will no longer be accessible after calling this method.
        return true if new model is swapped successfully.
        This method is thread safe. All taggers created by
        Model::createTagger() method will also be updated asynchronously.
        No need to stop the parsing thread excplicitly before swapping model object.
        @return boolean
        @param model new model which is going to be swapped with the current model.
        """
        model_data = ScopedPtr(Model(model))  ##ScopedPtr 사용법 맞는지?

        if not self.is_available():
            logger.error("current model is not available")
            return False

        m = model_data.get()
        if not m:
            logger.error("Invalid model is passed")
            return False

        if not m.is_available():
            logger.error("Passed model is not available")
            return False

        current_viterbi = self._viterbi_

        self._mutex_.acquire()  # 락을 얻음
        self._viterbi_ = m.take_viterbi()
        self._request_type_ = m.request_type()
        self._theta_ = m.theta()
        self._mutex_.release()  # 락을 해제함

        current_viterbi.clear()

        return True

    def take_viterbi(self) -> Viterbi:
        result = self._viterbi_
        self._viterbi_ = 0
        return result

    def is_available(self) -> bool:
        return (self._viterbi_ and self._writer_.get())

    def request_type(self) -> int:
        return self._request_type_

    def theta(self) -> float:
        return self._theta_

    def viterbi(self) -> Viterbi:
        return self._viterbi_

    def writer(self) -> Writer:
        return self._writer_.get()