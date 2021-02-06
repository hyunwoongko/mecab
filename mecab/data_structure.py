class Node:
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


class Dict:
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


