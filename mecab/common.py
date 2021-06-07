COPYRIGHT = "MeCab: Yet Another Part-of-Speech and Morphological Analyzer\n\n" \
            "Copyright(C) 2001-2012 Taku Kudo\n" \
            "Copyright(C) 2004-2008 Nippon Telegraph and Telephone Corporation\n"

PACKAGE = "mecab"
VERSION = "0.996"
MECAB_DEFAULT_RC = "/usr/local/etc/mecabrc"
DIC_VERSION = 102

SYS_DIC_FILE = "sys.dic"
UNK_DEF_FILE = "unk.def"
UNK_DIC_FILE = "unk.dic"
MATRIX_DEF_FILE = "matrix.def"
MATRIX_FILE = "matrix.bin"
CHAR_PROPERTY_DEF_FILE = "char.def"
CHAR_PROPERTY_FILE = "char.bin"
FEATURE_FILE = "feature.def"
REWRITE_FILE = "rewrite.def"
LEFT_ID_FILE = "left-id.def"
RIGHT_ID_FILE = "right-id.def"
POS_ID_FILE = "pos-id.def"
MODEL_DEF_FILE = "model.def"
MODEL_FILE = "model.bin"
DICRC = "dicrc"
BOS_KEY = "BOS/EOS"

DEFAULT_MAX_GROUPING_SIZE = 24
CHAR_PROPERTY_DEF_DEFAULT = "DEFAULT 1 0 0\nSPACE   0 1 0\n0x0020 SPACE\n"
UNK_DEF_DEFAULT = "DEFAULT,0,0,0,*\nSPACE,0,0,0,*\n"
MATRIX_DEF_DEFAULT = "1 1\n0 0 0\n"
MECAB_DEFAULT_CHARSET = "UTF-8"

NBEST_MAX = 512
NODE_FREELIST_SIZE = 512
PATH_FREELIST_SIZE = 2048
MIN_INPUT_BUFFER_SIZE = 8192
MAX_INPUT_BUFFER_SIZE = (8192 * 640)
BUF_SIZE = 8192
DEFAULT_THETA = 0.75
EXIT_FAILURE = 1
EXIT_SUCCESS = 0


def CHECK_FALSE(
    condition: bool,
    message: str,
):
    """
    print message if condition is not satisfied.

    Args:
        condition (bool): condition
        message (str): message to print

    """

    if not condition:
        print(message)


def CHECK_DIE(
    condition: bool,
    message: str = "Check Die",
):
    """
    print message and exit program if condition is not satisfied.

    Args:
        condition (bool): condition
        message (str): message to print

    """

    import sys

    if not condition:
        print(message)
        exit(0)
        sys.exit(0)
