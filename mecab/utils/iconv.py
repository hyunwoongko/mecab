import mecab.common
import mecab.utils.string_utils


def decode_charset_for_iconv(str):
    charset = mecab.utils.string_utils.decode_charset(str)

    mapper = {mecab.utils.string_utils.EncodingType.UTF8: "UTF-8",
              mecab.utils.string_utils.EncodingType.UTF16: "UTF-16",
              mecab.utils.string_utils.EncodingType.UTF16LE: "UTF-16LE",
              mecab.utils.string_utils.EncodingType.UTF16BE: "UTF-16BE"}

    if charset in mapper:
        return mapper[charset]
    else:
        print("charset", str, "is not defined, use", mecab.common.MECAB_DEFAULT_CHARSET)
        return mecab.common.MECAB_DEFAULT_CHARSET


class Iconv:

    def __init__(self):
        self._from = ''
        self._to = ''

    def open(self, _from, _to):
        self._from = decode_charset_for_iconv(_from)
        self._to = decode_charset_for_iconv(_to)
        return True

    def convert(self, string):
        if not string:
            return ''

        if self._from == '' or self._to == '':
            return ''

        return string.decode(self._from).encode(self._to)
