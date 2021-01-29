# MeCab -- Yet Another Part-of-Speech and Morphological Analyzer
# Copyright(C) 2001-2006 Taku Kudo <taku@chasen.org>
# Copyright(C) 2004-2006 Nippon Telegraph and Telephone Corporation
# Copyright(C) 2021 Hyunwoong Ko <kevin.woong@kakaobrain.com>

from mecab.utils import CHECK_DIE


class CharInfo:
    """
    struct `CharInfo`

    References:
        https://github.com/taku910/mecab/blob/master/mecab/src/char_property.h#L16
    """

    _type: int = 0
    _default_type: int = 0
    _length: int = 0
    _group: int = 0
    _invoke: int = 0

    def is_kind_of(self, c) -> int:
        """
        checks whether the input CharInfo and the current CharInfo are the same type.

        Args:
            c (CharInfo): input CharInfo

        Returns:
            (int): result of bitwise AND operation
        """

        return self._type & c._type


class Range:
    """
    struct `Range`

    References:
        https://github.com/taku910/mecab/blob/master/mecab/src/char_property.cpp#L20
    """

    _low: int
    _high: int
    _c: list


def atohex(s: str) -> int:
    """
    convert hex string to decimal integer

    Args:
        s (str): hex string value

    Returns:
        (int) integer value

    Notes:
        I can't understand why the name of this function is 'atohex'
        because output of function is decimal, not hexadecimal.

    Examples:
        >>> atohex('0x10')
        16
        >>> atohex('hello')
        no hex value: hello

    References:
        https://github.com/taku910/mecab/blob/master/mecab/src/char_property.cpp#L26
    """

    CHECK_DIE(
        condition=len(s) >= 3 and s[0] == '0' and (s[1] == 'x' or s[1] == 'X'),
        message=f"no hex value: {s}",
    )

    return int(s, 0)




