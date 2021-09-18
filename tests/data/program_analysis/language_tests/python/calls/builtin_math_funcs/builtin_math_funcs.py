import sys


def main(x1, x2, x3):
    a = min(x1, x2, x3)
    b = max(x3, x1, x2)
    c = abs(a - b)
    d = pow(x2, c)
    e = round(d)
    return e


print(main(float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3])))
