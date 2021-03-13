from dataclasses import dataclass
from enum import Enum
from typing import List, Dict

from mecab.common import CHECK_FALSE, COPYRIGHT, PACKAGE, VERSION


@dataclass
class Option:
    option_name: str
    short_option: str
    default_value: str
    arg_name: str
    description: str


defaultOptions = [
    Option("help", "h", "", "", "print help message and exit"),
    Option("version", "v", "", "", "print version and exit")
]


def get_length_of_option(option: Option) -> int:
    if len(option.arg_name) == 0:
        # +1 : space between displayname and description
        return len(option.option_name) + 1

    # space between displayname and description
    # '=' character
    return len(option.option_name) + len(option.arg_name) + 2


def get_default_option():
    return None


def get_default_value() -> str:
    return ""


def cast_string(arg):
    return arg


class ParamError(Enum):
    UNRECOGNIZED: int = 1
    REQUIRE_ARG: int = 2
    NO_ARG: int = 3


def print_arg_error(error, option) -> bool:
    if error == ParamError.UNRECOGNIZED:
        CHECK_FALSE(False, f"unrecognized option `{option}`")
    elif error == ParamError.REQUIRE_ARG:
        CHECK_FALSE(False, f"`{option}` requires an argument")
    elif error == ParamError.NO_ARG:
        CHECK_FALSE(False, f"`{option}` doesn't allow an argument")
    return False


class Param(object):
    command_name: str
    help_message: str
    version_message: str
    rest_parameters: List[str]
    configurations: Dict[str, str]

    def _construct_help_and_version_message(
        self,
        options: List[Option],
    ) -> None:
        length_of_options: List[int] = []

        for option in options:
            option_len = get_length_of_option(option)
            length_of_options.append(option_len)

        max_display_length = max(length_of_options)
        self.help_message = COPYRIGHT + "\nUsage: " + self.command_name + " [options] files\n"
        self.version_message = PACKAGE + " of " + VERSION + '\n'

        for option in options:
            length = 0
            self.help_message += " -"
            self.help_message += option.short_option[0]
            self.help_message += f", -- {option.option_name}"

            if option.arg_name and len(option.arg_name) != 0:
                self.help_message += f"={option.arg_name}"
                length += len(option.arg_name) + 1

            self.help_message += ' ' * (max_display_length - length)
            self.help_message += option.description + "\n"

    def _set_default_value(self, options: List[Option]):
        for option in options:
            if option.default_value and len(option.default_value) != 0:
                self.configurations[option.option_name] = option.default_value

    def clear(self):
        self.configurations.clear()
        self.rest_parameters.clear()

    def parse(self):
        # argParser 사용 예정
        pass
