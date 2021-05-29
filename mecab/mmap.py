from typing import IO, Union

import numpy as np

from mecab.common import CHECK_FALSE
import os


class Mmap:
    filename: str
    flag: str
    fd: IO
    text: Union[str, bytes]
    length: int

    def __init__(self):
        self.text = ''
        self.length = 0
        self.fd = None

    def begin(self):
        return 0

    def end(self):
        return self.size()

    def size(self):
        return self.length

    def file_name(self):
        return self.filename

    def file_size(self):
        return self.length

    def empty(self) -> bool:
        return self.length == 0

    def open(self, filename: str, mode: str = 'r'):
        """Open file

        Args:
            filename (str): filename with path
            mode (str): flag for file open

        Returns:
            bool: Whether the file is open or not
        """
        self.close()

        self.filename = filename
        self.flag = mode

        # CHECK_FALSE(self.flag in allow_flags, f"unknown open mode: {self.filename} mode: {self.flag}")
        allow_flags = ("r", "r+")
        if self.flag in allow_flags:
            self.flag += 'b'
        else:
            print(f"unknown open mode: {self.filename} mode: {self.flag}")
            return False

        if os.path.isfile(self.filename):
            """
            CHECK_FALSE((fd = ::fopen(filename, flag.c_str())) != NULL) << "open failed: " << filename;
            CHECK_FALSE((fileDescriptor = ::fileno(fd)) >= 0) << "cannot get file descriptor: " << filename;
            CHECK_FALSE(::fstat(fileDescriptor, &st) >= 0) << "failed to get file size: " << filename;
            """

            # Open file and get file size
            self.fd = open(self.filename, self.flag)
            file_descriptor = self.fd.fileno()
            st = os.fstat(file_descriptor)
            self.length = st.st_size

            # Read text
            self.text = self.fd.read(self.length)
            CHECK_FALSE(len(self.text) > 0, f"read() failed: {self.filename}")
            self.fd.close()
            self.fd = IO()

        return True

    def close(self):
        if self.fd is not None:
            self.fd.close()
            self.fd = None

        if self.text:
            if self.flag > "r+b":
                with open(self.filename, 'wb') as file:
                    file.write(self.text)

        self.text = ''
        self.length = 0

    def __del__(self):
        self.close()

    def __getitem__(self, index):
        return self.text[index]
