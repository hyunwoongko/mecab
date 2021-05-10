from typing import IO

import numpy as np

from mecab.common import CHECK_FALSE
import os


class Mmap:
    filename: str
    flag: str
    fd: IO
    text: any
    length: int

    def __init__(self):
        self.text = None
        self.length = 0
        self.fd = IO()

    def begin(self):
        return self.text

    def end(self):
        return self.text + self.size()

    def size(self) -> np.uintc:
        return np.uintc(self.length // len(self.text))

    def file_name(self):
        return self.filename

    def file_size(self):
        return self.length

    def empty(self) -> bool:
        return self.length == 0

    def open(self, filename: str, mode: str = 'r'):
        self.close()

        self.filename = filename
        self.flag = mode

        CHECK_FALSE(self.flag in ("r", "r+"), f"unknown open mode: {self.filename} mode: {self.flag}")
        self.flag += 'b'
        """
        CHECK_FALSE((fd = ::fopen(filename, flag.c_str())) != NULL) << "open failed: " << filename;
        CHECK_FALSE((fileDescriptor = ::fileno(fd)) >= 0) << "cannot get file descriptor: " << filename;
        CHECK_FALSE(::fstat(fileDescriptor, &st) >= 0) << "failed to get file size: " << filename;
        """
        if os.path.isfile(self.filename):
            pass
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
            if "r+b".startswith(self.flag) and os.path.isfile(self.filename):
                with open(self.filename, 'wb') as file:
                    file.write(self.text)

        self.text = 0

    def __del__(self):
        self.close()
