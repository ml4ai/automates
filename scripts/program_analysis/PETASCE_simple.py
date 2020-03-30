import sys
from typing import List
import math
from program_analysis.for2py.format import *
from program_analysis.for2py.arrays import *
from program_analysis.for2py.static_save import *
from program_analysis.for2py.strings import *
from dataclasses import dataclass
from program_analysis.for2py.types_ext import Float32
import program_analysis.for2py.math_ext as math
from numbers import Real
from random import random


@static_vars([{'name': 'tavg', 'call': [None], 'type': 'float'}, {'name': 'patm', 'call': [None], 'type': 'float'}, {'name': 'psycon', 'call': [None], 'type': 'float'}, {'name': 'udelta', 'call': [None], 'type': 'float'}, {'name': 'emax', 'call': [None], 'type': 'float'}, {'name': 'emin', 'call': [None], 'type': 'float'}, {'name': 'es', 'call': [None], 'type': 'float'}, {'name': 'ea', 'call': [None], 'type': 'float'}, {'name': 'fc', 'call': [None], 'type': 'float'}, {'name': 'few', 'call': [None], 'type': 'float'}, {'name': 'fw', 'call': [None], 'type': 'float'}, {'name': 'albedo', 'call': [None], 'type': 'float'}, {'name': 'rns', 'call': [None], 'type': 'float'}, {'name': 'pie', 'call': [None], 'type': 'float'}, {'name': 'dr', 'call': [None], 'type': 'float'}, {'name': 'ldelta', 'call': [None], 'type': 'float'}, {'name': 'ws', 'call': [None], 'type': 'float'}, {'name': 'ra1', 'call': [None], 'type': 'float'}, {'name': 'ra2', 'call': [None], 'type': 'float'}, {'name': 'ra', 'call': [None], 'type': 'float'}, {'name': 'rso', 'call': [None], 'type': 'float'}, {'name': 'ratio', 'call': [None], 'type': 'float'}, {'name': 'fcd', 'call': [None], 'type': 'float'}, {'name': 'tk4', 'call': [None], 'type': 'float'}, {'name': 'rnl', 'call': [None], 'type': 'float'}, {'name': 'rn', 'call': [None], 'type': 'float'}, {'name': 'g', 'call': [None], 'type': 'float'}, {'name': 'windsp', 'call': [None], 'type': 'float'}, {'name': 'wind2m', 'call': [None], 'type': 'float'}, {'name': 'cn', 'call': [None], 'type': 'float'}, {'name': 'cd', 'call': [None], 'type': 'float'}, {'name': 'kcmax', 'call': [None], 'type': 'float'}, {'name': 'rhmin', 'call': [None], 'type': 'float'}, {'name': 'wnd', 'call': [None], 'type': 'float'}, {'name': 'cht', 'call': [None], 'type': 'float'}, {'name': 'refet', 'call': [None], 'type': 'float'}, {'name': 'skc', 'call': [None], 'type': 'float'}, {'name': 'kcbmin', 'call': [None], 'type': 'float'}, {'name': 'kcbmax', 'call': [None], 'type': 'float'}, {'name': 'kcb', 'call': [None], 'type': 'float'}, {'name': 'ke', 'call': [None], 'type': 'float'}, {'name': 'kc', 'call': [None], 'type': 'float'}])
def petasce(canht: List[Real], doy: List[int], msalb: List[Real], meevp: String, srad: List[Real], tdew: List[Real], tmax: List[Real], tmin: List[Real], windht: List[Real], windrun: List[Real], xhlai: List[Real], xlat: List[Real], xelev: List[Real], eo: List[Real]):
    petasce.tavg[0] = ((tmax[0] + tmin[0]) / 2.0)
    petasce.patm[0] = (101.3 * (((293.0 - (0.0065 * xelev[0])) / 293.0) ** 5.26))
    petasce.psycon[0] = (0.000665 * petasce.patm[0])
    petasce.udelta[0] = ((2503.0 * math.exp(((17.27 * petasce.tavg[0]) / (petasce.tavg[0] + 237.3)))) / ((petasce.tavg[0] + 237.3) ** 2.0))
    petasce.emax[0] = (0.6108 * math.exp(((17.27 * tmax[0]) / (tmax[0] + 237.3))))
    petasce.emin[0] = (0.6108 * math.exp(((17.27 * tmin[0]) / (tmin[0] + 237.3))))
    petasce.es[0] = ((petasce.emax[0] + petasce.emin[0]) / 2.0)
    petasce.ea[0] = (0.6108 * math.exp(((17.27 * tdew[0]) / (tdew[0] + 237.3))))
    petasce.rhmin[0] = max(20.0, min(80.0, ((petasce.ea[0] / petasce.emax[0]) * 100.0)))
    if (xhlai[0] <= 0.0):
        petasce.albedo[0] = msalb[0]
    else:
        petasce.albedo[0] = 0.23
    petasce.rns[0] = ((1.0 - petasce.albedo[0]) * srad[0])
    petasce.pie[0] = 3.14159265359
    petasce.dr[0] = (1.0 + (0.033 * math.cos((((2.0 * petasce.pie[0]) / 365.0) * doy[0]))))
    petasce.ldelta[0] = (0.409 * math.sin(((((2.0 * petasce.pie[0]) / 365.0) * doy[0]) - 1.39)))
    petasce.ws[0] = math.acos(-(((1.0 * math.tan(((xlat[0] * petasce.pie[0]) / 180.0))) * math.tan(petasce.ldelta[0]))))
    petasce.ra1[0] = ((petasce.ws[0] * math.sin(((xlat[0] * petasce.pie[0]) / 180.0))) * math.sin(petasce.ldelta[0]))
    petasce.ra2[0] = ((math.cos(((xlat[0] * petasce.pie[0]) / 180.0)) * math.cos(petasce.ldelta[0])) * math.sin(petasce.ws[0]))
    petasce.ra[0] = ((((24.0 / petasce.pie[0]) * 4.92) * petasce.dr[0]) * (petasce.ra1[0] + petasce.ra2[0]))
    petasce.rso[0] = ((0.75 + (2E-5 * xelev[0])) * petasce.ra[0])
    petasce.ratio[0] = (srad[0] / petasce.rso[0])
    if (petasce.ratio[0] < 0.3):
        petasce.ratio[0] = 0.3
    else:
        if (petasce.ratio[0] > 1.0):
            petasce.ratio[0] = 1.0
    petasce.fcd[0] = ((1.35 * petasce.ratio[0]) - 0.35)
    petasce.tk4[0] = ((((tmax[0] + 273.16) ** 4.0) + ((tmin[0] + 273.16) ** 4.0)) / 2.0)
    petasce.rnl[0] = (((4.901E-9 * petasce.fcd[0]) * (0.34 - (0.14 * math.sqrt(petasce.ea[0])))) * petasce.tk4[0])
    petasce.rn[0] = (petasce.rns[0] - petasce.rnl[0])
    petasce.g[0] = 0.0
    petasce.windsp[0] = ((((windrun[0] * 1000.0) / 24.0) / 60.0) / 60.0)
    petasce.wind2m[0] = (petasce.windsp[0] * (4.87 / math.log(((67.8 * windht[0]) - 5.42))))
    petasce.cn[0] = 0.0
    petasce.cd[0] = 0.0
    if (meevp == "A"):
        petasce.cn[0] = 1600.0
        petasce.cd[0] = 0.38
    else:
        if (meevp == "G"):
            petasce.cn[0] = 900.0
            petasce.cd[0] = 0.34
    petasce.refet[0] = (((0.408 * petasce.udelta[0]) * (petasce.rn[0] - petasce.g[0])) + (((petasce.psycon[0] * (petasce.cn[0] / (petasce.tavg[0] + 273.0))) * petasce.wind2m[0]) * (petasce.es[0] - petasce.ea[0])))
    petasce.refet[0] = (petasce.refet[0] / (petasce.udelta[0] + (petasce.psycon[0] * (1.0 + (petasce.cd[0] * petasce.wind2m[0])))))
    petasce.refet[0] = max(0.0001, petasce.refet[0])
    petasce.skc[0] = 0.8
    petasce.kcbmin[0] = 0.3
    petasce.kcbmax[0] = 1.2
    if (xhlai[0] <= 0.0):
        petasce.kcb[0] = 0.0
    else:
        petasce.kcb[0] = max(0.0, (petasce.kcbmin[0] + ((petasce.kcbmax[0] - petasce.kcbmin[0]) * (1.0 - math.exp(-(((1.0 * petasce.skc[0]) * xhlai[0])))))))
    petasce.wnd[0] = max(1.0, min(petasce.wind2m[0], 6.0))
    petasce.cht[0] = max(0.001, canht[0])
    petasce.kcmax[0] = 0.5
    if (meevp == "A"):
        petasce.kcmax[0] = max(1.0, (petasce.kcb[0] + 0.05))
    else:
        if (meevp == "G"):
            petasce.kcmax[0] = max((1.2 + (((0.04 * (petasce.wnd[0] - 2.0)) - (0.004 * (petasce.rhmin[0] - 45.0))) * ((petasce.cht[0] / 3.0) ** 0.3))), (petasce.kcb[0] + 0.05))
    if (petasce.kcb[0] <= petasce.kcbmin[0]):
        petasce.fc[0] = 0.0
    else:
        petasce.fc[0] = (((petasce.kcb[0] - petasce.kcbmin[0]) / (petasce.kcmax[0] - petasce.kcbmin[0])) ** (1.0 + (0.5 * canht[0])))
    petasce.fw[0] = 1.0
    petasce.few[0] = min((1.0 - petasce.fc[0]), petasce.fw[0])
    petasce.ke[0] = max(0.0, min((1.0 * (petasce.kcmax[0] - petasce.kcb[0])), (petasce.few[0] * petasce.kcmax[0])))
    eo[0] = ((petasce.kcb[0] + petasce.ke[0]) * petasce.refet[0])
    eo[0] = max(eo[0], 0.0001)
    