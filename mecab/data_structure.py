class NodeType:
    # Normal node defined in the dictionary.
    MECAB_NOR_NODE = 0

    # Unknown node not defined in the dictionary.
    MECAB_UNK_NODE = 1

    # Virtual node representing a beginning of the sentence.
    MECAB_BOS_NODE = 2

    # Virtual node representing a end of the sentence.
    MECAB_EOS_NODE = 3

    # Virtual node representing a end of the N-best enumeration.
    MECAB_EON_NODE = 4


class DictType:
    # This is a system dictionary.
    MECAB_SYS_DIC = 0

    # This is a user dictionary.
    MECAB_USR_DIC = 1

    # This is a unknown word dictionary.
    MECAB_UNK_DIC = 2


class RequestType:
    # One best result is obtained (default mode)
    MECAB_ONE_BEST = 1

    # Set this flag if you want to obtain N best results.
    MECAB_NBEST = 2

    # Set this flag if you want to enable a partial parsing mode.
    # When this flag is set, the input |sentence| needs to be written
    # in partial parsing format.
    MECAB_PARTIAL = 4

    # Set this flag if you want to obtain marginal probabilities.
    # Marginal probability is set in MeCab::Node::prob.
    # The parsing speed will get 3-5 times slower than the default mode.
    MECAB_MARGINAL_PROB = 8

    # Set this flag if you want to obtain alternative results.
    # Not implemented.
    MECAB_ALTERNATIVE = 16

    # When this flag is set, the result linked-list (Node::next/prev)
    # traverses all nodes in the lattice.
    MECAB_ALL_MORPHS = 32

    # When this flag is set, tagger internally copies the body of passed
    # sentence into internal buffer.
    MECAB_ALLOCATE_SENTENCE = 64


class BoundaryConstraintType:
    # The token boundary is not specified.
    MECAB_ANY_BOUNDARY = 0

    # The position is a strong token boundary.
    MECAB_TOKEN_BOUNDARY = 1

    # The position is not a token boundary.
    MECAB_INSIDE_TOKEN = 2


class DictionaryInfo:
    # filename of dictionary
    # On Windows, filename is stored in UTF-8 encoding
    filename: str

    # character set of the dictionary. e.g., "SHIFT-JIS", "UTF-8"
    charset: str

    # How many words are registered in this dictionary.
    size: int

    # dictionary type
    # this value should be MECAB_USR_DIC, MECAB_SYS_DIC, or MECAB_UNK_DIC.
    type: int

    # left attributes size
    lsize: int

    # right attributes soze
    rsize: int

    # version of this dictionary
    version: int

    # pointer to the next dictionary info.
    # python can't access itself. (type of next is DictionaryInfo*)
    next: object


class Path:
    # pointer to the right node
    # type of rnode is Node*
    rnode: object

    # pointer to the next right path
    # python can't access itself. (type of rnext is Path*)
    rnext: object

    # pointer to the left node
    # type of lnode is Node*
    lnode: object

    # pointer to the next left path
    # python can't access itself. (type of lnext is Path*)
    lnext: object

    # local cost
    cost: int

    # marginal probability
    prob: float


class Node:
    # pointer to the previous node.
    # python can't access itself. (type of prev is Node*)
    prev: object

    # pointer to the next node.
    # python can't access itself. (type of next is Node*)
    next: object

    # pointer to the node which ends at the same position.
    # python can't access itself. (type of enext is Node*)
    enext: object

    # pointer to the node which starts at the same position.
    # python can't access itself. (type of bnext is Node*)
    bnext: object

    # pointer to the right path.
    # this value is NULL if MECAB_ONE_BEST mode.
    rpath: Path

    # pointer to the left path.
    # this value is NULL if MECAB_ONE_BEST mode.
    lpath: Path

    # surface string.
    # this value is not 0 terminated.
    # You can get the length with length/rlength members.
    surface: str

    # feature string
    feature: str

    # unique node id
    id: int

    # length of the surface form.
    length: int

    # length of the surface form including white space before the morph.
    rlength: int

    # right attribute id
    rcAttr: int

    # left attribute id
    lcAttr: int

    # unique part of speech id. This value is defined in "pos.def" file.
    posid: int

    # character type
    char_type: int

    # status of this model.
    # This value is MECAB_NOR_NODE, MECAB_UNK_NODE, MECAB_BOS_NODE, MECAB_EOS_NODE, or MECAB_EON_NODE.
    stat: int

    # set 1 if this node is best node.
    isbest: int

    # forward accumulative log summation.
    # This value is only available when MECAB_MARGINAL_PROB is passed.
    alpha: float

    # backward accumulative log summation.
    # This value is only available when MECAB_MARGINAL_PROB is passed.
    beta: float

    # marginal probability.
    # This value is only available when MECAB_MARGINAL_PROB is passed.
    prob: float

    # word cost
    wcost: int

    # best accumulative cost from bos node to this node.
    cost: int
