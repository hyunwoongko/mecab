from typing import List, Tuple
from mecab.common import CHECK_DIE, BUF_SIZE
from mecab.utils.string_utils import tokenize, escape_csv_element

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

    def __init__():
        spat: List[str] = []
        dpat: List[str] = []

    def set_pattern(self, src: str, dst: str):
        self.spat = []
        self.dpat = []

        self.spat += tokenizeCSV(src)
        self.dpat += tokenizeCSV(dst)

        return len(self.spat) and len(self.dpat)
    
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

            CHECK_DIE(escape_csv_element(elem))
            output.append(elem)
    
        return ','.join(output), True


# 작업중
# class RewriteRules(List[RewritePattern]):
    
#     def rewrite()