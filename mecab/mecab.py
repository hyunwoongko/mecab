"""
Pecab: Pure python mecab analyzer for CJK languages
Copyright(C) 2021 Hyunwoong Ko. All right reserved.
"""

import os

lang_synonym = {"kr": "ko", "cn": "zh", "jp": "ja"}


class MeCab(object):

    def __init__(
        self,
        lang: str,
        dic: str = "default",
    ) -> None:
        """
        Pecab: Pure python mecab analyzer for CJK languages

        Args:
            lang (str): language code
            dic (str): dictionary name or path (default="default")

        Notes:
            pecab provides pretrained dictionary for all languages.

            - you can use pretrained dictionaries using `dic="default"` or `dic="dict_name"`.
            - you can check pretrained dictionaries names using `MeCab.pretrained_dicts()`
            - also you can use your own dictionaries using `dic="/path/to/dict_path`.

        Examples:
              >>> # import mecab package
              >>> from mecab import MeCab

              >>> # check pretrained model names
              >>> MeCab.pretrained_dicts()
              {'ja': ['IPA', 'Juman', 'Unidic'], 'ko': ['mecab-ko-dic'], 'zh': ['mecab-chinese']}

              >>> # load Japanese default tagger
              >>> tagger = MeCab(lang="ja")

              >>> # load Japanese tagger by specifying dictionary.
              >>> tagger = MeCab(lang="ja", dic="Juman")

              >>> # load Japanese tagger using user own dictionary.
              >>> tagger = MeCab(lang="ja", dic="/path/to/dic")

              >>> # load Korean or Chinese tagger by modifying argument `lang`
              >>> ko_tagger = MeCab(lang="ko")
              >>> zh_tagger = MeCab(lang="zh")

              >>> # argument `dic` works the same for all languages.
              >>> ko_tagger = MeCab(lang="ko", dic="path/to/dic")
              >>> zh_tagger = MeCab(lang="zh", dic="path/to/dic")

        References:
            - MeCab: Yet Another Part-of-Speech and Morphological Analyzer
                - The CRF tagging mechanism follows the idea of the original mecab.
                - code: https://github.com/taku910/mecab
                - paper: https://www.aclweb.org/anthology/W04-3230.pdf

            - KoNLPy: Python package for Korean natural language processing.
                - The names of the method and factors follow KoNLPy's setting.
                - code: https://github.com/konlpy/konlpy
                - docs: https://konlpy.org/en/latest/

        """

        if lang in lang_synonym.keys():
            lang = lang_synonym[lang]

        assert lang in [
            "ja",
            "ko",
            "zh",
        ], "lang is must be in ['ja', 'jp', 'ko', 'kr', 'zh', 'cn']"

        self.lang = lang
        self.dic = self._load_dict(lang, dic)

    @staticmethod
    def pretrained_dicts():
        return {
            "ja": ["IPA", "Juman", "Unidic"],
            "ko": ["mecab-ko-dic"],
            "zh": ["mecab-chinese"]
        }

    def _load_dict(self, lang: str, dic: str):
        """
        load or download mecab dictionary

        Args:
            lang (str): language code (e.g. 'ja', 'ko', 'zh')
            dic (stR):

        Returns:

        """
        use_pretrain = False

        if dic == "default":
            dic = self.pretrained_dicts()[lang][0]
            dic = f"/root/.pecab/{dic}"
            use_pretrain = True
            # load default pretrained dictionary

        else:
            if dic in self.pretrained_dicts()[lang]:
                dic = f"/root/.pecab/{dic}"
                use_pretrain = True
                # load another specified pretrained dictionary

            else:
                use_pretrain = False

        if use_pretrain:

            if not os.path.exists(dic):
                try:
                    import wget
                except:
                    raise Exception("can not import `wget`. please install wget using `pip install wget`")

                wget.download(f"https://github.com/hyunwoongko/pecab/tree/main/dic/{lang}/{dic}.zip")

        else:
            pass

        return dic

    def parse(self, text):
        pass

    def morphs(self, text):
        pass


if __name__ == '__main__':
    print(MeCab.pretrained_dicts())
    tagger = MeCab(lang="ko")