import sys
import os
from typing import List
import math
from delphi.translators.for2py.format import *
from delphi.translators.for2py.arrays import *
from delphi.translators.for2py.static_save import *
from delphi.translators.for2py.strings import *
from delphi.translators.for2py import intrinsics
from dataclasses import dataclass
from delphi.translators.for2py.types_ext import Float32
import delphi.translators.for2py.math_ext as math
from numbers import Real
from random import random
@dataclass

class mytype_123:
    def __init__(self):
        self.ctr: int = 123
        self.a: int
        self.b: int

class mytype_456:
    def __init__(self):
        self.ctr: int = 456
        self.c: int
        self.d: int

class mytype_123_456:
    def __init__(self):
        self.x = mytype_123()
        self.y = mytype_456()


def main():
    format_10: List[str] = [None]
    format_10 = ['3(i5,2x)']
    format_10_obj = Format(format_10)
    
    var =  mytype_123_456()
    var.x.a = 12
    var.y.c = 21
    var.x.b = 34
    var.y.d = 45
    
    write_list_stream = [var.x.ctr, var]
    write_line = format_10_obj.write_line(write_list_stream)
    sys.stdout.write(write_line)
    write_list_stream = [var.y.ctr, var]
    write_line = format_10_obj.write_line(write_list_stream)
    sys.stdout.write(write_line)
    return

main()
