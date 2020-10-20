import sys
import os
from typing import List
import math
from automates.program_analysis.for2py.format import *
from automates.program_analysis.for2py.arrays import *
from automates.program_analysis.for2py.static_save import *
from automates.program_analysis.for2py.strings import *
from automates.program_analysis.for2py import intrinsics
from dataclasses import dataclass
from automates.program_analysis.for2py.types_ext import Float32
import automates.program_analysis.for2py.math_ext as math
from numbers import Real
from random import random

@dataclass
class mytype_123:
    ctr: int = 123
    a: int
    b: int

@dataclass
class mytype_456:
    ctr: int = 456
    c: int
    d: int

@dataclass
class mytype_123_456:
    x = mytype_123
    y = mytype_456


def main():
    format_10: List[str] = [None]
    format_10 = ['3(i5,2x)']
    format_10_obj = Format(format_10)
    
    var = mytype_123_456
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
