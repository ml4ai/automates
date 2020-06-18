import sys
from typing import List
import math
from program_analysis.translators.for2py.format import *
from program_analysis.translators.for2py.arrays import *
from program_analysis.translators.for2py.static_save import *
from program_analysis.translators.for2py.strings import *
from dataclasses import dataclass
from program_analysis.translators.for2py.types_ext import Float32
import program_analysis.translators.for2py.math_ext as math
from numbers import Real
from random import random
from program_analysis.translators.for2py.tmp.m_interface03_mod import *


def main():
    
    control_arg =  controltype()
    iswitch_arg =  switchtype()
    get_control(control_arg)
    get_iswitch(iswitch_arg)
    put_control(control_arg)
    put_iswitch(iswitch_arg)

main()
