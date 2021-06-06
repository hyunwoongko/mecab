from typing import Dict
from dataclasses import dataclass
import logging
from typing import List, Tuple
import os

from mecab.common import CHECK_DIE, BUF_SIZE
from mecab.utils.string_utils import tokenize, tokenize2, tokenizeCSV, escape_csv_element

logger = logging.getLogger(__file__)

def match_rewrite_pattern(pattern, target):
    if pattern == "*" or pattern == target:
        return True
    
    if len(pattern) >= 3 and pattern[0] == '(' and pattern[-1] == ')':
        CHECK_DIE(len(pattern) < BUF_SIZE - 3, "too long parameter")
        buf = pattern[1:len(pattern) - 3]
        
        tokens = tokenize(buf, '|')
        CHECK_DIE(len(tokens) < BUF_SIZE, "too long parameter")

        for token in tokens:
            if target == token:
                return True
    
    return False


class RewritePattern:

    def __init__(self):
        self.spat: List[str] = []
        self.dpat: List[str] = []

    def set_pattern(self, src: str, dst: str):
        self.spat = []
        self.dpat = []

        self.spat += tokenizeCSV(src, 512)
        self.dpat += tokenizeCSV(dst, 512)

        return len(self.spat) != 0 and len(self.dpat) != 0
    
    def rewrite(self, size: int, input_strings: List[str]) -> Tuple[str, bool]:
        output: List[str] = []
        if len(self.spat) > size:
            return "", False

        for i in range(0, len(self.spat)):
            
            if not match_rewrite_pattern(self.spat[i], input_strings[i]):
                return "", False
        
        for i in range(0, len(self.dpat)):
            char_index = 0
            elem = ""
            while char_index < len(self.dpat[i]):
                character = self.dpat[i][char_index]
                if character == '$':
                    char_index += 1
                    n = 0

                    while char_index < len(self.dpat[i]):
                        character = self.dpat[i][char_index]
                        if '0' <= character <= '9':
                            n = 10 * n + (character - '0')
                            char_index += 1
                        else:
                            break

                        char_index += 1
                    
                    CHECK_DIE(n >0 and (n - 1) < size, f"out of range [{self.dpat[i]}] {n}")
                    elem += input_strings[n-1]

                    if char_index < len(self.dpat[i]):
                        elem += character

                else:
                    elem += character
                
                char_index += 1
            elem, is_success = escape_csv_element(elem)
            CHECK_DIE(is_success)
            output.append(elem)

        return ','.join(output), True


class RewriteRules(List[RewritePattern]):
    
    def rewrite(self, size, input_strings: List[str]):
        for i in range(len(self)):
            output, is_success = self[i].rewrite(size, input_strings)
            if is_success:
                return output, True
        return None, False
    
    def append_rewrite_rule(self, s):
        col = tokenize2(s, " \t", 3)
        print("s", s)
        print("col", col, len(col), len(col) >= 2)
        CHECK_DIE(len(col) >= 2, f"format error: {col}")

        if len(col) >= 3:
            tmp = col[1]
            tmp += ' '
            tmp += col[2]
            col[1] = tmp
        new_item = RewritePattern()
        self.append(new_item)
        self[-1].set_pattern(col[0], col[1])


@dataclass
class FeatureSet:
    ufeature: str
    lfeature: str
    rfeature: str


class DictionaryRewriter:
    def __init__(self):
        self.unigram_rewrite = RewriteRules()
        self.left_rewrite = RewriteRules()
        self.right_rewrite = RewriteRules()
        self.cache: Dict[str, FeatureSet] = {}
    
    def open(self, filename, encoding='utf-8'):
        CHECK_DIE(os.path.exists(filename), f"no such file or directory: {filename}")

        append_to = 0

        with open(filename, 'r', encoding=encoding) as f:
            for line in f.read().splitlines():
                if len(line) == 0 or line[0] == '#':
                    continue
                
                if line == "[unigram rewrite]":
                    append_to = 1
                elif line == "[left rewrite]":
                    append_to = 2
                elif line == "[right rewrite]":
                    append_to = 3
                else:
                    print(f"here{line}")
                    CHECK_DIE(append_to != 0, "no sections found")

                    if append_to == 1:
                        self.unigram_rewrite.append_rewrite_rule(line)
                    elif append_to == 2:
                        self.left_rewrite.append_rewrite_rule(line)
                    elif append_to == 3:
                        self.right_rewrite.append_rewrite_rule(line)
        return True
    
    def clear(self):
        self.cache.clear()
    
    def rewrite(self, feature, feature_set: FeatureSet):
        CHECK_DIE(len(feature) < BUF_SIZE, "too long CSV entities")
        col = tokenizeCSV(feature, BUF_SIZE)
        CHECK_DIE(len(col) < BUF_SIZE, "too long CSV entities")

        ufeature, u_success = self.unigram_rewrite.rewrite(len(col), col)
        lfeature, l_success = self.left_rewrite.rewrite(len(col), col)
        rfeature, r_success = self.right_rewrite.rewrite(len(col), col)

        feature_set.ufeature = ufeature
        feature_set.lfeature = lfeature
        feature_set.rfeature = rfeature

        return u_success and l_success and r_success
    
    def rewrite2(self, feature, feature_set: FeatureSet):
        if feature in self.cache:
            feature_set.ufeature = self.cache[feature].ufeature
            feature_set.lfeature = self.cache[feature].lfeature
            feature_set.rfeature = self.cache[feature].rfeature
        else:
            if not self.rewrite(feature, feature_set):
                return False
            
            self.cache[feature] = feature_set
        return True


class PosIDGenerator:
    def __init__(self):
        self.rewrite = RewriteRules()
    
    def open(self, filename, encoding='utf-8'):
        if not os.path.exists(filename):
            logger.error(f"{filename} is not found. minimum setting is used")
            new_item = RewritePattern()
            new_item.set_pattern("*", "1")
            self.rewrite.append(new_item)
            return True

        with open(filename, 'r', encoding=encoding) as f:
            for line in f.readlines():
                col = tokenize2(line, " \t", 2)
                CHECK_DIE(len(col) == 2, f"format error: {line}")
                for character in col[1]:
                    CHECK_DIE("0" <= character <= "9", f"not a number: {col[1]}")
                
                new_item = RewritePattern()
                new_item.set_pattern(col[0], col[1])
                self.rewrite.append(new_item)

        return True

    def clear(self):
        self.rewrite.clear()
    
    def id(self, feature):
        CHECK_DIE(len(feature) < BUF_SIZE - 1, "too long feature")
        col = tokenizeCSV(feature, BUF_SIZE)
        CHECK_DIE(len(col) < BUF_SIZE, "too long CSV entities")

        output, is_success = self.rewrite.rewrite(len(col), col)

        if not is_success:
            return -1
        
        return int(output)
