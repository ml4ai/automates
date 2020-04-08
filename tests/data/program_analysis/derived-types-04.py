import sys
from typing import List
import math
from automates.program_analysis.for2py.format import *
from automates.program_analysis.for2py.arrays import *
from automates.program_analysis.for2py.static_save import *
from automates.program_analysis.for2py.strings import *
from dataclasses import dataclass
from automates.program_analysis.for2py.types_ext import Float32
import automates.program_analysis.for2py.math_ext as math
from numbers import Real
from random import random
@dataclass

class mytype_123:
    def __init__(self):
        self.ctr : int = 123
        self.a : int
        self.b : int

class mytype_456:
    def __init__(self):
        self.ctr : int = 456
        self.c : int
        self.d : int

class mytype_123_456:
    def __init__(self):
        self.x = mytype_123()
        self.y = mytype_456()


def main():
    format_10: List[str] = [None]
    format_10 = ['3(I5,2X)']
    format_10_obj = Format(format_10)
    
    var =  mytype_123_456()
    var.x.a = 12
    var.y.c = 21
    var.x.b = 34
    var.y.d = 45
    
    write_list_stream = [var.x.ctr, var.x.a, var.x.b]
    write_line = format_10_obj.write_line(write_list_stream)
    sys.stdout.write(write_line)
    write_list_stream = [var.y.ctr, var.y.c, var.y.d]
    write_line = format_10_obj.write_line(write_list_stream)
    sys.stdout.write(write_line)
    return

main()
