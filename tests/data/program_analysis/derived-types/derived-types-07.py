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
class mytype:
    simcontrol = String(120, "                                                                                                        ")


def main():
    test = String(20, "hello world")

main()
