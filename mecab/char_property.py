# MeCab -- Yet Another Part-of-Speech and Morphological Analyzer
# Copyright(C) 2001-2006 Taku Kudo <taku@chasen.org>
# Copyright(C) 2004-2006 Nippon Telegraph and Telephone Corporation
# Copyright(C) 2021 Hyunwoong Ko <kevin.woong@kakaobrain.com>

from typing import List, Dict

from mecab.utils import CHECK_DIE


class CharInfo:
    """
    struct `CharInfo`

    References:
        https://github.com/taku910/mecab/blob/master/mecab/src/char_property.h#L16
    """

    type: int = 0
    default_type: int = 0
    length: int = 0
    group: int = 0
    invoke: int = 0

    def is_kind_of(self, c) -> int:
        """
        checks whether the input CharInfo and the current CharInfo are the same type.

        Args:
            c (CharInfo): input CharInfo

        Returns:
            (int): result of bitwise AND operation
        """

        return self.type & c.type


class Range:
    """
    struct `Range`

    References:
        https://github.com/taku910/mecab/blob/master/mecab/src/char_property.cpp#L20
    """

    low: int
    high: int
    c: list


class CharProperty:

    def open_param(self, param) -> bool:
        pass

    def open_char(self, char) -> bool:
        pass

    def close(self):
        pass

    def size(self):
        pass

    def set_charset(self, charset):
        pass

    def id(self, char):
        pass

    def name(self, i):
        pass

    def what(self):
        pass

    def seek_to_other_type(self, begin, end, c, fail, mblen, clen):
        pass

    def get_char_info(self, begin, end, mblen):
        pass

    def compile(self):
        pass


def atohex(s: str) -> int:
    """
    convert hex string to decimal integer

    Args:
        s (str): hex string value

    Returns:
        (int) integer value

    Examples:
        >>> atohex('0x10')
        16
        >>> atohex('hello')
        'no hex value: hello'

    References:
        https://github.com/taku910/mecab/blob/master/mecab/src/char_property.cpp#L26
    """

    CHECK_DIE(
        condition=len(s) >= 3 and s[0] == '0' and (s[1] == 'x' or s[1] == 'X'),
        message=f"no hex value: {s}",
    )

    return int(s, 0)


def encode(c: List[str], category: Dict[str, CharInfo]) -> CharInfo:
    """
    encode from list of strings

    Args:
        c (List[str]): list of strings
        category (Dict[str, CharInfo]): categories

    Returns:
        (CharInfo): encoded output charinfo
    """

    CHECK_DIE(
        condition=len(c) != 0,
        message="category size is empty"
    )

    CHECK_DIE(
        condition=c[0] in category,
        message=f'category [{c[0]}] is undefined',
    )

    base: CharInfo = category[c[0]]

    for i in range(0, len(c)):
        CHECK_DIE(
            condition=c[i] in category,
            message=f'category [{c[i]}] is undefined',
        )

        base.type += (1 << category[c[i]].default_type)

    return base
