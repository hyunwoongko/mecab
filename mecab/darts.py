from dataclasses import dataclass
from typing import List

import numpy as np

ARRAY_DTYPE = np.int
ARRAY_U_DTYPE = np.uintc

ARRAY_DTYPE = np.dtype([('base', ARRAY_DTYPE), ('check', ARRAY_U_DTYPE)])


@dataclass
class Node:
    code: int
    depth: int
    left: int
    right: int


class DoubleArrayTrieSystem:
    def __init__(self):
        self.keys: List[str] = []
        self.sizes: List[int] = []
        self.key_token_sizes: List[int] = []
        self.error: int = 0
        self.next_check_pos: int = 0
        self.progress: int = 0
        self.array: np.ndarray = np.zeros([], dtype=ARRAY_DTYPE)
        self.used: np.ndarray = np.zeros([], dtype=np.bool)

    def resize(self, size):
        self.array = np.resize(self.array, size)
        self.used = np.resize(self.used, size)

    def build(self, keys, sizes, key_token_sizes):
        """
        Args:
            keys: Strings to register in trie
            sizes: An array that collects the lengths of the elements in the key array
            key_token_sizes: An array that collects the token counts of the elements in the key array

        Returns:
            error: Indicate build successfully finished. If this value is non-zero, build is failed.
        """
        self.keys = keys
        self.sizes = sizes
        self.key_token_sizes = key_token_sizes
        self.progress = 0
        self.resize(8192)

        self.array[0]['base'] = 1
        self.next_check_pos = 0
        root_node = Node(code=0, left=0, right=len(keys), depth=0)
        siblings = []
        self.fetch(root_node, siblings)
        self.insert(siblings)

        return self.error

    def fetch(self, parent: Node, siblings: List[Node]) -> int:
        if self.error < 0:
            return 0

        prev_character_code = 0

        for i in range(parent.left, parent.right):
            if (self.sizes[i] if self.sizes else len(self.keys[i])) < parent.depth:
                continue

            cur_key = self.keys[i]
            cur_character_code = 0

            if (self.sizes[i] if self.sizes else len(self.keys[i])) != parent.depth:
                cur_character_code = ord(cur_key[parent.depth]) + 1

            if prev_character_code > cur_character_code:
                self.error = -3
                return 0

            if prev_character_code != cur_character_code or len(siblings) == 0:
                sibling = Node(code=cur_character_code, depth=parent.depth + 1,left = i, right=-1)
                if len(siblings) != 0:
                    siblings[len(siblings) - 1].right = i
                siblings.append(sibling)

            prev_character_code = cur_character_code

        if len(siblings) != 0:
            siblings[len(siblings) - 1].right = parent.right

        return len(siblings)

    def insert(self, siblings: List[Node]) -> int:
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
                self.resize(self.array.size * int(max(1.05, 1.0 * len(self.keys) / (self.progress + 1))))

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

        for i in range(0, len(siblings)):
            self.array[begin + siblings[i].code]['check'] = begin

        for i in range(0, len(siblings)):
            new_siblings: List[Node] = []

            if self.fetch(siblings[i], new_siblings):
                h: int = self.insert(new_siblings)
                self.array[begin + siblings[i].code]['base'] = h
            else:
                self.array[begin + siblings[i].code]['base'] = (
                    -self.key_token_sizes[siblings[i].left] - 1
                    if self.key_token_sizes
                    else
                    -siblings[i].left - 1
                )

                if self.key_token_sizes and -self.key_token_sizes[siblings[i].left] - 1 >= 0:
                    self.error = -2
                    return 0

                self.progress += 1

        return begin

    def exact_match_search(self, key, size=0, node_pos=0):
        if not size:
            size = len(key)

        result = {
            'value': -1,
            'len': 0
        }

        base: int = self.array[node_pos]['base']
        pointer: int

        for i in range(0, size):
            pointer = base + ord(key[i]) + 1
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

    def common_prefix_search(self, key, result_len, size=0, node_pos=0):
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

            pointer = base + ord(key[i]) + 1
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
    words = sorted(
        ["c", "ca", "cat", "cats", "center", "cut", "cute", "do", "dog", "fox", "rat", "rust", "rus", "한글", '한글안녕'])
    da = DoubleArrayTrieSystem()
    sizes = [len(word) for word in words]
    tokens = [1 for word in words]
    tokens[-1] = 2
    da.build(words, sizes, tokens)
    print(da.exact_match_search('cat'))
    print(da.exact_match_search('한글'))
    print(da.exact_match_search('영어'))
    print(da.common_prefix_search('한글안녕', 10))