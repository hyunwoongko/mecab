import re
import csv
from enum import Enum
from io import StringIO


def dtoa(val):
    return str(val)


def itoa(val):
    return str(val)


def uitoa(val):
    return str(val)


def create_filename(path, file):
    s = path
    if len(s) > 0 and s[-1] != '/':
        s += '/'
    s += file

    return s


def remove_filename(path):
    path_word_list = path.split('/')

    if len(path_word_list) == 1:
        return '.'

    path_word_list.pop()

    return '/'.join(path_word_list)


def remove_pathname(path):
    path_word_list = path.split('/')

    if len(path_word_list) == 1:
        return '.'

    return path_word_list[-1]


def replace_string(string, source, destination):
    return string.replace(source, destination, 1)


def to_lower(text):
    return text.lower()


class EncodingType(Enum):
    UTF8 = 0
    UTF16 = 1
    UTF16LE = 2
    UTF16BE = 3
    ASCII = 4


def decode_charset(charset):
    tmp = to_lower(charset)

    if tmp == "utf8" or tmp == "utf_8" or tmp == "utf-8":
        return EncodingType.UTF8
    elif tmp == "utf16" or tmp == "utf_16" or tmp == "utf-16":
        return EncodingType.UTF16
    elif tmp == "utf16be" or tmp == "utf_16be" or tmp == "utf-16be":
        return EncodingType.UTF16BE
    elif tmp == "utf16le" or tmp == "utf_16le" or tmp == "utf-16le":
        return EncodingType.UTF16LE
    elif tmp == "ascii":
        return EncodingType.ASCII
    else:
        return EncodingType.UTF8


def getEscapedChar(p):
    mapper = {'0': '\0',
              'a': '\0',
              'b': '\a',
              't': '\t',
              'n': '\n',
              'v': '\v',
              'f': '\f',
              'r': '\r',
              's': ' ',
              '\\': '\\'}

    result = mapper.get(p)
    if result is None:
        return '\0'

    return result


def tokenize(string, delimiter):
    return re.split(f"[{delimiter}]", string)

def tokenize2(string, delimiter, size):
    return [
        elem
        for elem in re.split(f"[{delimiter}]", string)
        if len(elem) != 0
    ][:size]

def tokenizeCSV(string, size):
    size -= 1
    if(size < 0):
        size = 0
    return re.split(f"[,]", string, maxsplit=size)

def escape_csv_element(text):
    if text.find(',') != -1 or text.find('"') != -1:
        tmp = '\"'
        
        for character in text:
            if character == '"':
                tmp += '"'
            tmp += character
        
        tmp += '"'
        return tmp, True
    else:
        return text, True

    


bar = "###########################################"
scale = len(bar) - 1
prev = 0


def progress_bar(message, current, total):
    global bar
    global scale
    global prev

    cur_percentage = int(100.0 * current / total)
    bar_len = int(1.0 * current * scale / total)

    if prev != cur_percentage:
        print(f'{message}: {cur_percentage:>3}%% |%.{int(bar_len)}{bar}%{int(scale - bar_len)}{""}|')

    if cur_percentage == 100:
        print("\n")
    else:
        print("\r")

    prev = cur_percentage

    return 1
