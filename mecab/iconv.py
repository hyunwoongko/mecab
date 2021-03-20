import mecab.common
import mecab.utils.string_utils


def decodeCharsetForIconv(str):
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
    __from = ''
    __to = ''

    def open(self, _from, to):
        self.__from = decodeCharsetForIconv(_from)
        self.__to = decodeCharsetForIconv(to)

        return True

    def convert(self, string):
        if not string:
            return {True, ''}

        if self.__from == '' or self.__to == '':
            return {True, ''}

        return {True, string.decode(self.__from).encode(self.__to)}
