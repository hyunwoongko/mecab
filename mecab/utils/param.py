import argparse
from dataclasses import dataclass
from typing import List, Union
from mecab.common import PACKAGE, VERSION


@dataclass
class Option:
    option_name: str  # e.g. help
    short_option: str  # e.g. h
    default_value: str
    arg_name: Union[str, type]  # argument type e.g. int, float, ...
    description: str


defaultOptions = [
    Option("version", "v", f"{PACKAGE} of {VERSION}\n", "", "print version and exit")
]


class Param(object):
    command_name: str
    help_message: str
    version_message: str = f"{PACKAGE} of {VERSION}\n"
    rest_parameters = []
    configurations = {}

    def parse(self, argv: List[str] = None, options: List[Option] = None):
        # argc is meaningless in python.
        # so please use only this method not `parse(argc, argv, options)`.
        # we don't need to override method because it is useless.

        arguments: List[str] = []

        for arg in argv:
            if arg[-3:] != ".py":
                arguments.append(arg)

        parser = argparse.ArgumentParser()
        options = defaultOptions + options

        for option in options:
            parser.add_argument(
                f"-{option.short_option}",
                f"--{option.option_name}",
                default=option.default_value,
                help=option.description,
                type=option.arg_name if isinstance(option.arg_name, type) else str,
            )

        parser.add_argument('rest', nargs='*')
        parsed = parser.parse_args(arguments)

        self.configurations = vars(parsed)
        self.rest_parameters = self.configurations["rest"]
        self.configurations.pop("rest")
        self.help_message = parser.format_help()
        self.command_name = arguments[0]

    def get(self, name):
        return self.configurations[name]

    def set(self, key: str, value, override: bool = True) -> None:
        if key in self.configurations:
            if override:
                self.configurations[key] = value
        else:
            self.configurations[key] = value

    def parse_file(self, filename: str) -> bool:
        lines = open(filename, mode="r", encoding="utf-8").read().splitlines()

        for line in lines:
            if len(line) == 0 or line[0] == ";" or line[0] == "#":
                continue

            if "=" not in line:
                raise Exception(f"format error: {line}")

            split_by_equal_mark = line.split("=")
            assert len(split_by_equal_mark) == 2, \
                f"format error: {line}, must be 'key=value'"

            key, val = split_by_equal_mark[0], split_by_equal_mark[1]
            key, val = key.replace("\t\v", ""), val.replace("\t\v", "")
            self.set(key, val)

        return True

    def get_rest_parameters(self) -> List[str]:
        return self.rest_parameters

    def get_version_message(self) -> str:
        return self.version_message

    def get_help_message(self) -> str:
        return self.help_message

    def get_command_name(self) -> str:
        return self.command_name

    def clear(self) -> None:
        self.configurations = {}
        self.rest_parameters = []


if __name__ == '__main__':
    """HOW TO USE?"""

    param = Param()
    options = [
        Option("chicken", "c", "", "", "치킨"),
        Option("beverage", "b", "", "", "음료"),
        Option("price", "p", "", int, "가격"),
        Option("number", "n", "1", int, "개수")
    ]

    param.parse(
        argv=[
            "--chicken=kfc",
            "--beverage=coke",
            "--price=10000",
            "dunkin",  # rest parameters
            "starbucks"  # rest parameters
        ],
        options=options
    )

    chicken = param.get("chicken")
    print(chicken, type(chicken))  # kfc, <class 'str'>

    number = param.get("number")
    print(number, type(number))  # 1 (default value), <class 'int'>

    rest = param.rest_parameters
    print(rest)  # [dunkin, starbucks]

    param.get_version_message()
    param.get_help_message()
    param.get_command_name()

    param.set("chicken", "bbq", override=True)
    chicken = param.get("chicken")
    print(chicken)  # bbq

    param.set("chicken", "bbq", override=False)
    chicken = param.get("chicken")
    print(chicken)  # bbq (because override is False)

    param.set("burger", "mcdonald")
    burger = param.get("burger")
    print(burger)  # mcdonald
