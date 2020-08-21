import sys
import os
from typing import List
import math
from program_analysis.translators.for2py.format import *
from program_analysis.translators.for2py.arrays import *
from program_analysis.translators.for2py.static_save import *
from program_analysis.translators.for2py.strings import *
from program_analysis.translators.for2py import intrinsics
from dataclasses import dataclass
from program_analysis.translators.for2py.types_ext import Float32
import program_analysis.translators.for2py.math_ext as math
from numbers import Real
from random import random

@dataclass
class mytype:
    simcontrol = String(120, "                                                                                                        ")


def main():
    test = String(20, "hello world")

main()
