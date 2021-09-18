import sys


def main(x1, x2, x3, x4):
    a = 10
    b = 20
    c = 30
    d = 40
    e = 50

    a += x1 - x2 * x3
    b -= x4 * x3 / x2
    c *= x1 + x2 * x3
    c **= x4
    d /= x1 + x2
    e %= x4 - x3

    return a, b, c, d, e


print(
    main(
        int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    )
)
