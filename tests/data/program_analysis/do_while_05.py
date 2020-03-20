import sys
from typing import List
import math
from program_analysis.for2py.format import *
from program_analysis.for2py.arrays import *
from dataclasses import dataclass
from program_analysis.for2py.types_ext import Float32
import program_analysis.for2py.math_ext as math
from numbers import Real


def do_while():
    month: List[int] = [None]
    month[0] = 1
    while (month[0] <= 13):
        if (month[0] == 13):
            return
        print("Month: ", month)
        month[0] = (month[0] + 1)

do_while()
