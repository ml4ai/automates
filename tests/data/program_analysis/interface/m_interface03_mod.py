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
class controltype:
    mesic = String(1)
    rnmode = String(1)
    crop = String(2)
    model = String(8)
    ename = String(8)
    filex = String(12)
    fileio = String(30)
    dssatp = String(102)
    das: int
    dynamic: int
    frop: int
    errcode: int
    lunio: int
    multi: int
    n_elems: int
    nyrs: int
    repno: int
    rotnum: int
    run: int
    trtnum: int
    yrdif: int
    yrdoy: int
    yrsim: int

@dataclass
class switchtype:
    fname = String(1)
    idetc = String(1)
    idetd = String(1)
    idetg = String(1)
    ideth = String(1)
    idetl = String(1)
    idetn = String(1)
    ideto = String(1)
    idetp = String(1)
    idetr = String(1)
    idets = String(1)
    idetw = String(1)
    ihari = String(1)
    iplti = String(1)
    iirri = String(1)
    isimi = String(1)
    iswche = String(1)
    iswdis = String(1)
    iswnit = String(1)
    iswpho = String(1)
    iswpot = String(1)
    iswsym = String(1)
    iswtil = String(1)
    iswwat = String(1)
    meevp = String(1)
    meghg = String(1)
    mehyd = String(1)
    meinf = String(1)
    meli = String(1)
    mepho = String(1)
    mesom = String(1)
    mesol = String(1)
    mesev = String(1)
    mewth = String(1)
    metmp = String(1)
    iferi = String(1)
    iresi = String(1)
    ico2 = String(1)
    fmopt = String(1)
    nswi: int

@dataclass
class transfertype:
    control = controltype
    iswitch = switchtype
    output: outputtype
    plant: planttype
    mgmt: mgmttype
    nitr: nitype
    orgc: orgctype
    soilprop: soiltype
    spam: spamtype
    water: wattype
    weather: weathtype
    pdlabeta: pdlabetatype


maxfiles: List[int] = [500]
save_data = transfertype

def get_control(control_arg: List[controltype]):
    control_arg[0] = save_data.control
    

def put_control(control_arg: List[controltype]):
    save_data.control = control_arg[0]
    

def get_iswitch(iswitch_arg: List[switchtype]):
    iswitch_arg[0] = save_data.iswitch
    

def put_iswitch(iswitch_arg: List[switchtype]):
    save_data.iswitch = iswitch_arg[0]
    