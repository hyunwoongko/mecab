from typing import Union

from mecab.common import CHECK_FALSE, BUF_SIZE
from mecab.data_structure import Node, NodeType
from mecab.lattice import Lattice
from mecab.utils.param import Param
from mecab.utils.scoped_ptr import *
from mecab.utils.string_buffer import StringBuffer


class Writer:
    def __init__(self):
        self.write_ = self.write_lattice
        self.temp_buffer = ScopedPtr()
        self.temp_buffer.reset(StringBuffer())

        self.node_format_ = ScopedString()
        self.bos_format_ = ScopedString()
        self.eos_format_ = ScopedString()
        self.unk_format_ = ScopedString()
        self.eon_format_ = ScopedString()

    def __del__(self):
        if self.temp_buffer.get():
            self.temp_buffer.get().clear()

    def open(self, param: Param):
        ostyle = param.get("output-format-type")
        self.write_ = self.write_lattice

        if ostyle == "wakati":
            self.write_ = self.write_wakati
        elif ostyle == "none":
            self.write_ = self.write_none
        elif ostyle == "dump":
            self.write_ = self.write_dump
        elif ostyle == "em":
            self.write_ = self.write_em
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

            if ostyle != '':
                node_format_key += "-" + ostyle
                bos_format_key += "-" + ostyle
                eos_format_key += "-" + ostyle
                unk_format_key += "-" + ostyle
                eon_format_key += "-" + ostyle
                tmp = param.get(node_format_key)
                CHECK_FALSE(tmp != '', f"unknown format type [{ostyle}]")

            node_format2 = param.get(node_format_key)
            bos_format2 = param.get(bos_format_key)
            eos_format2 = param.get(eos_format_key)
            unk_format2 = param.get(unk_format_key)
            eon_format2 = param.get(eon_format_key)

            if node_format != node_format2 or bos_format != bos_format2 \
                    or eos_format != eos_format2 or unk_format != unk_format2:
                self.write_ = self.write_user

                if node_format != node_format2:
                    node_format = node_format2

                if bos_format != bos_format2:
                    bos_format = bos_format2

                if eos_format != eos_format2:
                    eos_format = eos_format2

                # TODO:: elif 문의 조건이 참일 수 없는 구조임. 확인 필요할듯
                if unk_format != unk_format2:
                    unk_format = unk_format2
                elif node_format != node_format2:
                    unk_format = node_format2
                else:
                    unk_format = node_format

                if eon_format != eon_format2:
                    eon_format = eon_format2

                self.node_format_.reset_string(node_format)
                self.bos_format_.reset_string(bos_format)
                self.eos_format_.reset_string(eos_format)
                self.unk_format_.reset_string(unk_format)
                self.eon_format_.reset_string(eon_format)

        return True

    def close(self):
        self.write_ = self.write_lattice

    def stringify_lattice(self, lattice: Lattice, *args: Union[Node, str, int]):
        """
            Args:
                lattice (Lattice): language code
                args (tuple):
                    node (Node)
                    buf (str)
                    size (int)

            Returns:
                bool: Whether the file is open or not
            node: Node = None, buf: str = None, size: int = None
        """
        args_len = len(args)
        assert 0 <= args_len <= 3, ''

        if len(args) == 0:
            return self.stringify_lattice_internal(lattice, self.get_stream())
        elif len(args) == 1:
            node: Node = args[0]
            return self.stringify_lattice_internal_with_node(lattice, node, self.get_stream())
        elif len(args) == 2:
            buf: str = args[0]
            size: int = args[1]
            os: StringBuffer = StringBuffer(buf, size)
            return self.stringify_lattice_internal(lattice, os)
        elif len(args) == 3:
            node: Node = args[0]
            buf: str = args[1]
            size: int = args[2]
            os: StringBuffer = StringBuffer(buf, size)
            return self.stringify_lattice_internal_with_node(lattice, node, os)

    def stringify_lattice_nbest(self, lattice: Lattice, N: int, buf: str = None, size: int = None):
        os = StringBuffer(buf, size) if buf is not None and size is not None else self.get_stream()
        return self.stringify_lattice_nbest_internal(lattice, N, os)

    def write_node(self, lattice: Lattice, p: str, node: Node, os: StringBuffer):
        if p is None:
            node_type_dict = {
                NodeType.MECAB_BOS_NODE: self.bos_format_,
                NodeType.MECAB_EOS_NODE: self.eos_format_,
                NodeType.MECAB_UNK_NODE: self.unk_format_,
                NodeType.MECAB_NOR_NODE: self.node_format_,
                NodeType.MECAB_EON_NODE: self.eon_format_,
            }
            p = node_type_dict[node.stat].get()

        buf = ScopedFixedArray(BUF_SIZE)
        ptr = ScopedFixedArray(64)
        psize = 0

        index = 0
        p_length = len(p)
        while index < p_length:
            p_value = p[index]
            if p_value == '\\':
                index += 1
                os << get_escaped_char(p[index])
            elif p_value == '%':
                # macros
                index += 1
                p_second_value = p[index]
                if p_second_value == 'S':
                    # input sentence
                    os.write(lattice.sentence(), lattice.size())
                elif p_second_value == 'L':
                    # sentence length
                    os << lattice.size()
                elif p_second_value == 'm':
                    # morph
                    os.write(node.surface, node.length)
                elif p_second_value == 'M':
                    os.write(str(node.surface[node.length - node.rlength:]), node.length)
                elif p_second_value == 'h':
                    # Part-Of-Speech ID
                    os << node.posid
                elif p_second_value == '%':
                    os << '%'
                elif p_second_value == 'c':
                    # word cost
                    os << int(node.wcost)
                elif p_second_value == 'H':
                    os << node.feature
                elif p_second_value == 't':
                    os << int(node.char_type)
                elif p_second_value == 's':
                    os << int(node.stat)
                elif p_second_value == 'P':
                    os << node.prob
                elif p_second_value == 'p':
                    index += 1
                    p_third_value = p[index]
                    if p_third_value == 'i':
                        # node id
                        os << node.id
                    elif p_third_value == 'S':
                        # space
                        os.write(str(node.surface[node.length - node.rlength:]), node.rlength - node.length)
                    elif p_third_value == 's':
                        # start position
                        # TODO:: char* - char*
                        os << int(node.surface - lattice.sentence())
                    elif p_third_value == 'e':
                        # end position
                        # TODO:: char* - char*
                        os << int(node.surface - lattice.sentence() + node.length)
                    elif p_third_value == 'C':
                        # connection cost
                        os << node.cost - node.prev.cost - node.wcost
                    elif p_third_value == 'w':
                        # word cost
                        os << node.wcost
                    elif p_third_value == 'c':
                        # best cost
                        os << node.wcost
                    elif p_third_value == 'n':
                        # node cost
                        os << (node.cost - node.prev.cost)
                    elif p_third_value == 'b':
                        # * if best path, otherwise ' '
                        os << '*' if node.isbest else ' '
                    elif p_third_value == 'P':
                        os << node.prob
                    elif p_third_value == 'A':
                        os << node.alpha
                    elif p_third_value == 'B':
                        os << node.beta
                    elif p_third_value == 'l':
                        os << node.length
                    elif p_third_value == 'L':
                        os << node.rlength
                    elif p_third_value == 'h':
                        index += 1
                        p_fourth_value = p[index]
                        if p_fourth_value == 'l':
                            os << node.lcAttr
                        elif p_fourth_value == 'r':
                            os << node.rcAttr
                        else:
                            lattice.set_what('lr is required after %ph')
                            return False

                    elif p_third_value == 'p':
                        mode = p[index + 1]
                        sep = p[index + 2]
                        index += + 2

                        if sep == '\\':
                            index += 1
                            sep = get_escapedChar(p[index])
                        if not node.lpath:
                            lattice.set_what('no path information is available')
                            return False

                        path = node.lpath
                        while path:
                            if path != node.lpath:
                                os << sep

                            if mode == 'i':
                                os << path.lnode.id
                            elif mode == 'c':
                                os << path.cost
                            elif mode == 'P':
                                os << path.prob
                            else:
                                lattice.set_what('[icP] is required after %pp')
                                return False

                            path = path.lnext
                    else:
                        lattice.set_what('[iseSCwcnblLh] is required after %p')
                        return False

                elif p_second_value in ['F', 'f']:
                    if node.feature[0] == '\0':
                        lattice.set_what('no feature information available')
                        return False

                    if not psize:
                        buf.get()[:ptr.size()] = ptr.get()
                        psize = tokenize_csv(buf.get(), ptr.get(), ptr.size())

                    separator = '\t'
                    if p[index] == 'F':
                        index += 1
                        if p[index] == '\\':
                            index += 1
                            separator = getEscapedChar(p[index])
                        else:
                            separator = p[index]

                    index += 1
                    if p[index] != '[':
                        lattice.set_what("cannot find '['")
                        return False

                    n = 0
                    sep = False
                    is_fil = False
                    index += 1

                    while True:
                        if p_length >= index:
                            lattice.set_what("cannot find ']'")
                            return False

                        if p[index] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                            n = 10 * n + int(p[index])
                        elif p[index] in [',', ']']:
                            if n >= psize:
                                lattice.set_what('given index is out of range')
                                return False

                            is_fil = ptr[n][0] != '*'
                            if is_fil:
                                if sep:
                                    os << separator

                                os << ptr[n]

                            if p[index] == ']':
                                break

                            sep = is_fil
                            n = 0
                        else:
                            lattice.set_what("cannot find ']'")
                            return False

                        index += 1

                else:
                    error = 'unknown meta char:'
                    error += p_value
                    lattice.set_what(error)
                    return False

            else:
                os << p_value

        return True

    def write(self, lattice: Lattice, os: StringBuffer):
        if lattice is False or lattice.is_available() is False:
            return False

        return self.write_(lattice, os)

    def get_stream(self) -> StringBuffer:
        return self.temp_buffer.get()

    def stringify_lattice_internal(self, lattice: Lattice, os: StringBuffer):
        os.clear()
        if not self.write_(lattice, os):
            return 0

        os << '\0'
        if not os.str():
            lattice.set_what("output buffer overflow")
            return 0

        return os.str()

    def stringify_lattice_internal_with_node(self, lattice: Lattice, node: Node, os: StringBuffer):
        os.clear()
        if not node:
            lattice.set_what("node is None")
            return 0

        if not self.write_node(lattice, node, os):
            return 0

        os << '\0'
        if not os.str():
            lattice.set_what("output buffer overflow")
            return 0

        return os.str()

    def stringify_lattice_nbest_internal(self, lattice: Lattice, N: int, os: StringBuffer):
        pass

    def write_lattice(self, lattice: Lattice, os: StringBuffer):
        for node in lattice.bos_nodes():
            os.write(node.surface, node.length)
            os << '\t' << node.feature
            os << '\n'

        os << "EOS\n"
        return True

    def write_wakati(self, lattice: Lattice, os: StringBuffer):
        for node in lattice.bos_nodes():
            os.write(node.surface, node.length)
            os << ' '

        os << "\n"
        return True

    def write_none(self, lattice: Lattice, os: StringBuffer):
        return True

    def write_user(self, lattice: Lattice, os: StringBuffer):
        if not self.write_node(lattice, self.bos_format_.get(), lattice.bos_nodes(), os):
            return False

        node = None
        nodes = lattice.bos_nodes()
        for index in range(len(nodes)):
            node = nodes[index]
            fmt = self.unk_format_.get() if node.stat == NodeType.MECAB_UNK_NODE else self.node_format_.get()
            if not self.write_node(lattice, fmt, node, os):
                return False

        if not self.write_node(lattice, self.eos_format_.get(), node, os):
            return False

        return True

    def write_dump(self, lattice: Lattice, os: StringBuffer):
        string = lattice.sentence()
        for node in lattice.bos_nodes():
            os << node.id << ' '
            if node.stat == NodeType.MECAB_BOS_NODE:
                os << "BOS"
            elif node.stat == NodeType.MECAB_EOS_NODE:
                os << "EOS"
            else:
                os.write(node.surface, node.length)

            # TODO:: 테스트하는 과정에서 python에 맞게 수정 필요
            os << ' ' << node.feature << ' ' << int(node.surface - string) << ' ' \
            << int(node.surface - string + node.length) << ' ' << node.rcAttr << ' ' << node.lcAttr << ' ' \
            << node.posid << ' ' << int(node.char_type) << ' ' << int(node.stat) << ' ' \
            << int(node.isbest) << ' ' << node.alpha << ' ' << node.beta << ' ' << node.prob << ' ' << node.cost

            path = node.lpath
            while path:
                os << ' ' << path.lnode.id << ':' << path.cost << ':' << path.prob
                path = path.lnext

            os << '\n'

        return True

    def write_em(self, lattice: Lattice, os: StringBuffer):
        min_prob = 0.0001
        node: Node = lattice.bos_nodes()
        while node:
            if node.prob >= min_prob:
                os << 'U\t'
                if node.stat == NodeType.MECAB_BOS_NODE:
                    os << "BOS"
                elif node.stat == NodeType.MECAB_EOS_NODE:
                    os << "EOS"
                else:
                    os.write(node.surface, node.length)

                os << '\t' << node.feature << '\t' << node.prob << '\n'

            path = node.lpath
            while path:
                if path.prob >= min_prob :
                    os << 'B\t' << path.lnode.feature << '\t' << node.feature << '\t' << path.prob << '\n'

                path = path.lnext

            node = node.next

        os << "EOS\n"
        return True
