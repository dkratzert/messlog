#!python
#  Copyright (c)  2019 by Daniel Kratzert
from pathlib import Path


class Sadabs():
    def __init__(self, filename):
        self.fileobj = Path(filename)

    def parse_file(self):
