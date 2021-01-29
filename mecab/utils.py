# MeCab -- Yet Another Part-of-Speech and Morphological Analyzer
# Copyright(C) 2001-2006 Taku Kudo <taku@chasen.org>
# Copyright(C) 2004-2006 Nippon Telegraph and Telephone Corporation
# Copyright(C) 2021 Hyunwoong Ko <kevin.woong@kakaobrain.com>

import sys


def CHECK_DIE(condition: bool, message: str):
    """
    If the condition is not satisfied,
    the program exits and a message is printed.

    Args:
        condition (bool): input condition
        message (str): output message

    Returns:
        (int) return 0 if condition is satisfied
        (exit) exits program if condition is not satisfied
    """

    if not condition:
        print(message)
        exit()
        sys.exit()

    else:
        return 0
