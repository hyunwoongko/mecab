from dataclasses import dataclass


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



