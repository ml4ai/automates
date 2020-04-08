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



def foo_int(x: List[int], result: List[int]):
    result[0] = int(((47 * x[0]) + 23))
    

def foo_real(x: List[Real], result: List[int]):
    result[0] = int(((int(x[0]) * 31) + 17))
    

def foo_bool(x: List[bool], result: List[int]):
    if x[0]:
        result[0] = 937
    else:
        result[0] = -(732)
    