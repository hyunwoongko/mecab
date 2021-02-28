from ctypes import Structure, c_int, c_uint, sizeof
from dataclasses import dataclass
from typing import List

import numpy as np

ARRAY_DTYPE = np.int
ARRAY_U_DTYPE = np.uintc

ARRAY_DTYPE = np.dtype([('base', ARRAY_DTYPE), ('check', ARRAY_U_DTYPE)])


@dataclass
class Node:
    """
    Node contain trie's left, right node index and it's node depth in trie.
    code means character code (ord(Character))
    ex) A -> 65
    """

    code: int
    depth: int
    left: int
    right: int


class NodeInCPlusPlusBinary(Structure):
    _fields_ = [('base', c_int),
                ('check', c_uint)]


class DoubleArrayTrieSystem:
    def __init__(self):
        self.keys: List[List[int]] = []
        self.sizes: List[int] = []
        self.key_token_sizes: List[int] = []
        self.error: int = 0
        self.next_check_pos: int = 0
        self.progress: int = 0
        self.size_ = 0
        self.array: np.ndarray = np.zeros([], dtype=ARRAY_DTYPE)
        self.used: np.ndarray = np.zeros([], dtype=np.bool)

    def resize(self, size: int):
        self.array = np.resize(self.array, size)
        self.used = np.resize(self.used, size)

    def decompose_string_to_utf8(self, string):
        """Decompose String to hex values

        Examples:
            Input: 'a한국어'
            Output: [99, 237, 149, 156, 234, 181, 173, 236, 150, 180]

        Args:
            string: string to decompose

        Returns:
            string's integer codes
        """
        return [char for char in string.encode('utf-8')]

    def load_c_binary(self, binary_path: str) -> np.ndarray:
        """Load C++ style darts binary to python

        Args:
            binary_path: binary file path to load

        Returns:
            darts array in python
        """
        with open(binary_path, 'rb') as f:
            result = []
            x = NodeInCPlusPlusBinary()
            while f.readinto(x) == sizeof(x):
                result.append((x.base, x.check))
        result = np.asarray(result, dtype=ARRAY_DTYPE)
        return result

    def build(self, keys: List[str], sizes: List[int],
              key_token_sizes: List[int]):
        """ Build trie system.
        Args:
            keys: Strings to register in trie
            sizes: An array that collects the lengths of the elements in the key array
            key_token_sizes: An array that collects the token counts of the elements in the key array

        Returns:
            error: Indicate build successfully finished. If this value is non-zero, build is failed.
        """
        self.keys = [self.decompose_string_to_utf8(key) for key in keys]
        self.sizes = [len(k) for k in self.keys]
        self.key_token_sizes = key_token_sizes
        self.progress = 0
        self.resize(8192)

        self.array[0]['base'] = 1
        self.next_check_pos = 0
        root_node = Node(code=0, left=0, right=len(keys), depth=0)
        siblings = []
        self.fetch(root_node, siblings)
        self.insert(siblings)

        self.size_ += (1 << 8) + 1

        if self.size_ >= self.array.size:
            self.resize(self.size_)

        del self.used
        self.used = None

        return self.error

    def fetch(self, parent: Node, siblings: List[Node]) -> int:
        """ Extract sibling list in parent's left - right range and convert Character to code
        Args:
            parent: trie's parent node
            siblings: List to store sibling Nodes.
        Returns:
            Number of node in siblings
        """
        if self.error < 0:
            return 0

        prev_character_code = 0

        for i in range(parent.left, parent.right):
            if (self.sizes[i]
                    if self.sizes else len(self.keys[i])) < parent.depth:
                continue

            cur_key = self.keys[i]
            cur_character_code = 0

            if (self.sizes[i]
                    if self.sizes else len(self.keys[i])) != parent.depth:
                cur_character_code = cur_key[parent.depth] + 1

            if prev_character_code > cur_character_code:
                self.error = -3
                return 0

            if prev_character_code != cur_character_code or len(siblings) == 0:
                sibling = Node(code=cur_character_code,
                               depth=parent.depth + 1,
                               left=i,
                               right=-1)
                if len(siblings) != 0:
                    siblings[len(siblings) - 1].right = i
                siblings.append(sibling)

            prev_character_code = cur_character_code

        if len(siblings) != 0:
            siblings[len(siblings) - 1].right = parent.right

        return len(siblings)

    def insert(self, siblings: List[Node]) -> int:
        """ Insert prefetch siblings into parent node.
        Assign base and check values.

        Args:
            siblings: Node list to add into trie.

        Returns:
            node's begin index of double array (self.array)
        """
        if self.error < 0:
            return 0

        begin: int = 0
        pos: int = max(siblings[0].code + 1, self.next_check_pos) - 1
        nonzero_num: int = 0
        first: bool = True

        if self.array.size <= pos:
            self.resize(pos + 1)

        while True:
            is_pass = True
            pos += 1

            if self.array.size <= pos:
                self.resize(pos + 1)

            if self.array[pos]['check']:
                nonzero_num += 1
                continue
            elif first:
                self.next_check_pos = pos
                first = False

            begin = pos - siblings[0].code

            if self.array.size <= (begin + siblings[-1].code):
                self.resize(
                    self.array.size *
                    int(max(1.05, 1.0 * len(self.keys) / (self.progress + 1))))

            if self.used[begin]:
                continue

            for i in range(1, len(siblings)):
                if self.array[begin + siblings[i].code]['check'] != 0:
                    is_pass = False
                    break

            if is_pass:
                break

        # -- Simple heuristics --
        # if the percentage of non-empty contents in check between the index
        # 'next_check_pos' and 'check' is greater than some constant
        # value(e.g. 0.9),
        # new 'next_check_pos' index is written by 'check'.

        if 1.0 * nonzero_num / (pos - self.next_check_pos + 1) >= 0.95:
            self.next_check_pos = pos

        self.used[begin] = True
        self.size_ = max(self.size_, begin + siblings[-1].code + 1)

        for i in range(0, len(siblings)):
            self.array[begin + siblings[i].code]['check'] = begin

        for i in range(0, len(siblings)):
            new_siblings: List[Node] = []

            if self.fetch(siblings[i], new_siblings):
                h: int = self.insert(new_siblings)
                self.array[begin + siblings[i].code]['base'] = h
            else:
                self.array[begin + siblings[i].code]['base'] = (
                    -self.key_token_sizes[siblings[i].left] -
                    1 if self.key_token_sizes else -siblings[i].left - 1)

                if self.key_token_sizes and -self.key_token_sizes[
                        siblings[i].left] - 1 >= 0:
                    self.error = -2
                    return 0

                self.progress += 1

        return begin

    def exact_match_search(self, key: str, size: int = 0, node_pos: int = 0):
        """ Find exact match string in trie.
        Args:
            key: search key for exact match
            size: key length.
            node_pos: root index.

        Returns:
            dict of str: int
            {
                'value': int. input key's number of token
                'len': int. input key's length
            }

        """
        key = self.decompose_string_to_utf8(key)
        if not size:
            size = len(key)

        result = {'value': -1, 'len': 0}

        base: int = self.array[node_pos]['base']
        pointer: int

        for i in range(0, size):
            pointer = base + key[i] + 1
            if base == self.array[pointer]['check']:
                base = self.array[pointer]['base']
            else:
                return result
        pointer = base
        value = self.array[pointer]['base']

        if base == self.array[pointer]['check'] and value < 0:
            result['value'] = -value - 1
            result['len'] = size

        return result

    def common_prefix_search(self,
                             key: str,
                             result_len: int,
                             size: int = 0,
                             node_pos: int = 0):
        """ Find prefix match string in trie.
        Args:
            key: search key for exact match
            result_len: max number of result prefixes
            size: key length.
            node_pos: root index.

        Returns:
            list of dict of str: int
            [{
                'value': int. input key's number of token
                'len': int. input key's length
            }]

        """
        key = self.decompose_string_to_utf8(key)
        if not size:
            size = len(key)

        results = []
        base: int = self.array[node_pos]['base']
        pointer: int

        for i in range(0, size):
            pointer = base
            value = self.array[pointer]['base']

            if base == self.array[pointer]['check'] and value < 0:
                if len(results) < result_len:
                    results.append({'value': -value - 1, 'len': i})

            pointer = base + key[i] + 1
            if base == self.array[pointer]['check']:
                base = self.array[pointer]['base']
            else:
                return results

        pointer = base
        value = self.array[pointer]['base']

        if base == self.array[pointer]['check'] and value < 0:
            if len(results) < result_len:
                results.append({'value': -value - 1, 'len': size})

        return results


if __name__ == "__main__":
    da = DoubleArrayTrieSystem()
    c_array = da.load_c_binary('test/mecab/build/output.bin')
    dic = [
        ('cat', 'c'),
        ('cat', 'a'),
        ('cat', 't'),
        ('car', 'ca'),
        ('car', 'r'),
        ('한국어', '한국'),
        ('한국어', '어')
    ]
    dic.sort()

    bsize = 0
    idx = 0

    prev = None
    str_list = []
    len_list = []
    val_list = []

    for i in range(0, len(dic)):
        if i != 0 and prev != dic[i][0]:
            str_list.append(dic[idx][0])
            len_list.append(len(dic[idx][0]))
            val_list.append(bsize + (idx << 8))
            bsize = 1
            idx = i
        else:
            bsize += 1
        prev = dic[i][0]

    str_list.append(dic[idx][0])
    len_list.append(len(dic[idx][0]))
    val_list.append(bsize + (idx << 8))

    da.build(str_list, len_list, val_list)
