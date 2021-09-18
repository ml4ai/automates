import math
import sys


def main(x1, x2, x3, x4):
    a = math.sqrt(x1)
    b = math.exp(x2)
    c = math.log(x3, 10) * math.pow(x3, 10)
    d = math.floor(x4) + math.ceil(x4)
    e = math.sin(a + b) + math.cos(a + b) - math.tan(a - b)
    f = math.asin(c + d) + math.acos(c + d) - math.atan(c - d)
    g = math.sinh(e + f) - math.cosh(e + f) + math.tanh(e + f)
    return g


print(
    main(
        float(sys.argv[1]),
        float(sys.argv[2]),
        float(sys.argv[3]),
        float(sys.argv[4]),
    )
)
