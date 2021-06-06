from mecab.common import CHECK_FALSE
from mecab.utils.param import Param
from mecab.lattice import Lattice
# from mecab.utils.scoped_ptr import *
# from mecab.utils.string_buffer


class Writer:
    def __init__(self):
        self.write_ = None
        self.temp_buffer = None

    def open(self, param: Param):
        ostyle = param.get("output-format-type")
        write_ = self.write_lattice

        if ostyle == "wakati":
            write_ = self.write_wakati
        elif ostyle == "none":
            write_ = self.write_none
        elif ostyle == "dump":
            write_ = self.write_dump
        elif ostyle == "em":
            write_ = self.write_em
        else:
            node_format = "%m\\t%H\\n"
            unk_format = "%m\\t%H\\n"
            bos_format = ""
            eos_format = "EOS\\n"
            eon_format = ""

            node_format_key = "node-format"
            bos_format_key = "bos-format"
            eos_format_key = "eos-format"
            unk_format_key = "unk-format"
            eon_format_key = "eon-format"

            if ostyle == '':
                node_format_key += "-" + ostyle
                bos_format_key += "-" + ostyle
                eos_format_key += "-" + ostyle
                unk_format_key += "-" + ostyle
                eon_format_key += "-" + ostyle
                tmp = param.get(node_format_key)

                # TODO:: CHECK_FALSE return이 없음
                CHECK_FALSE(tmp != '', f"unknown format type [{ostyle}]")
                if tmp != '':
                    return False

            node_format2 = param.get(node_format_key)
            bos_format2 = param.get(bos_format_key)
            eos_format2 = param.get(eos_format_key)
            unk_format2 = param.get(unk_format_key)
            eon_format2 = param.get(eon_format_key)

            if node_format != node_format2 or bos_format != bos_format2 or \
                    eos_format != eos_format2 or unk_format != unk_format2:
                write_ = self.write_user

                if node_format != node_format2:
                    node_format = node_format2

                if bos_format != bos_format2:
                    bos_format = bos_format2

                if unk_format != unk_format2:
                    unk_format = unk_format2
                elif node_format != node_format2:
                    unk_format = node_format2
                else:
                    unk_format = node_format

                if eon_format != eon_format2:
                    eon_format = eon_format2

                """
                node_format_.reset_string(node_format.c_str());
                bos_format_.reset_string(bos_format.c_str());
                eos_format_.reset_string(eos_format.c_str());
                unk_format_.reset_string(unk_format.c_str());
                eon_format_.reset_string(eon_format.c_str());
                """
        return True

    def close(self):
        self.write_ = None

    def write_lattice(self, lattice: Lattice, os):
        while True:
            node = lattice.next()
            if node is False:
                break

            # os.write(node.surface, node.langth)

    def write_wakati(self, lattice: Lattice, os):
        pass

    def write_none(self, lattice: Lattice, os):
        return True

    def write_user(self, lattice: Lattice, os):
        pass

    def write_dump(self, lattice: Lattice, os):
        pass

    def write_em(self, lattice: Lattice, os):
        pass