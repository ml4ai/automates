import sys


def main(x):
    a = 3
    b = 2
    c = 1
    quad_x = a * x ** 2 + b * x + c
    return quad_x


print(main(int(sys.argv[1])))
