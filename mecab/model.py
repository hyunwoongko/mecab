"""
## issue (해결 못한 부분들)

(중요) 1. overloading 어떻게 할 건지?
- open 함수
- create 함수

(중요) 2. mecab_options 구현

3. 같은 변수에 대해 public, private 둘다 있는 부분??

4. 클래스 변수명 뒤에 _ 부분은 빼는 게 맞는지?

(중요) 5. mutex 부분 구현 맞는지?

"""


import logging
from typing import Type, List
from threading import Thread
from threading import Lock

from mecab.common import CHECK_FALSE
from mecab.writer import Writer
from mecab.data_structure import Node, RequestType, DictionaryInfo
from mecab.viterbi import Viterbi
from mecab.utils.scoped_ptr import ScopedPtr
from mecab.utils.param import Param
from mecab.utils.io import load_dictionary_resource
from mecab.model import Model
from mecab.lattice import Lattice

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

### mecab options ?? 구현 how??
mecab_options = []
"""
const std::vector<MeCab::Option> mecab_options{
    {"rcfile", 'r', "", "FILE", "use FILE as resource file"},
    {"dicdir", 'd', "", "DIR", "set DIR  as a system dicdir"},
    {"userdic", 'u', "", "FILE", "use FILE as a user dictionary"},
    {"lattice-level", 'l', "0", "INT", "lattice information level (DEPRECATED)"},
    {"dictionary-info", 'D', "", "", "show dictionary information and exit"},
    {"output-format-type", 'O', "", "TYPE", "set output format type (wakati,none,...)"},
    {"all-morphs", 'a', "", "", "output all morphs(default false)"},
    {"nbest", 'N', "1", "INT", "output N best results (default 1)"},
    {"partial", 'p', "", "", "partial parsing mode (default false)"},
    {"marginal", 'm', "", "", "output marginal probability (default false)"},
    {"max-grouping-size", 'M', "24", "INT", "maximum grouping size for unknown words (default 24)"},
    {"node-format", 'F', "%m\\t%H\\n", "STR", "use STR as the user-defined node format"},
    {"unk-format", 'U', "%m\\t%H\\n", "STR", "use STR as the user-defined unknown node format"},
    {"bos-format", 'B', "", "STR", "use STR as the user-defined beginning-of-sentence format"},
    {"eos-format", 'E', "EOS\\n", "STR", "use STR as the user-defined end-of-sentence format"},
    {"eon-format", 'S', "", "STR", "use STR as the user-defined end-of-NBest format"},
    {"unk-feature", 'x', "", "STR", "use STR as the feature for unknown word"},
    {"input-buffer-size", 'b', "", "INT", "set input buffer size (default 8192)"},
    {"dump-config", 'P', "", "", "dump MeCab parameters"},
    {"allocate-sentence", 'C', "", "", "allocate new memory for input sentence"},
    {"theta", 't', "0.75", "FLOAT", "set temparature parameter theta (default 0.75)"},
    {"cost-factor", 'c', "700", "INT", "set cost factor (default 700)"},
    {"output", 'o', "", "FILE", "set the output file name"}};

"""

class Model:
    def __init__(self):
        self.viterbi = Viterbi()
        self.writer = Writer()
        self.request_type = RequestType.MECAB_ONE_BEST
        self.theta = 0.0

        self._writer = ScopedPtr(Writer())
        self.mutex = Lock()
        self._request_type = None
        self._theta = None

    def __del__(self):
        self.viterbi.free()
        self.viterbi = 0

    ## overloading
    def open(self, argc: int, argv: List[str]) -> bool:
        param = Param()
        if ((not param.parse(argc, argv, mecab_options)) or (not load_dictionary_resource(param))):
            return False

        return open(param)

    def open(self, arg: str) -> bool:
        param = Param()
        if ((not param.parse(arg, mecab_options)) or (not load_dictionary_resource(param))):
            return False

        return open(param)

    def open(self, param: Param) -> bool:
        CHECK_FALSE(self.writer.open(param) and self.viterbi.open(param))

        self.request_type = get_request_type(param.get("allocate-sentence"), param.get("partial"),
                                             param.get("all-morphs"), param.get("marginal"), param.get("nbest"))
        self.theta = param.get("theta")

        return self.is_available()

    def version(self) -> str:
        """
        Return a version string
        @return version string
        """
        return DictionaryInfo.VERSION  ## version of this dictionary

    ## overloading
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
        return self.viterbi.tokenizer_ if self.viterbi.tokenizer_.dictionary_info() else 0

    def transition_cost(self, rcAttr: int, lcAttr: int) -> int:
        """
        Return transtion cost from rcAttr to lcAttr.
        @return transtion cost
        """
        return self.viterbi.connector_().transition_cost(rcAttr, lcAttr)

    def lookup(self, begin: str, end: str, lattice: Lattice) -> Node:
        """
        perform common prefix search from the range [begin, end).
        |lattice| takes the ownership of return value.
        @return node linked list.
        """
        return self.viterbi.tokenizer_.lookup(begin, end, lattice.allocator(), lattice)

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
        model_data = ScopedPtr(model)

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

        current_viterbi = self.viterbi

        ## mutex 부분 구현 맞는지????
        self.mutex.acquire()  # 락을 얻음
        self.viterbi = m.take_viterbi()
        self.request_type = m.request_type()
        self.theta = m.theta()
        self.mutex.release()  # 락을 해제함

        current_viterbi.clear()

        return True

    def take_viterbi(self) -> Viterbi:
        result = self.viterbi
        self.viterbi = 0
        return result

    def is_available(self) -> bool:
        return (self.viterbi and self.writer_get())

    def request_type(self) -> int:
        return self.request_type

    def theta(self) -> float:
        return self.theta

    def viterbi(self) -> Viterbi:
        return self.viterbi

    def writer(self) -> Writer:
        return self._writer.get()