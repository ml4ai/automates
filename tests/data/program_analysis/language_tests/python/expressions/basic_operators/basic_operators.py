import sys


def main(x, y, z, c1, c2):
    a = x + y - z
    b = (a / (y * -z)) ** 2
    c = b % 10
    d = c // 2

    c3 = c1 and c2
    c4 = c1 or (not c3)
    c5 = c2 ^ c4

    e1 = a == b and c != d
    e2 = c >= d or b > a
    e3 = d <= a and c < d
    e4 = e1 or e2 or e3

    return d, c5, e4


print(
    main(
        int(sys.argv[1]),
        int(sys.argv[2]),
        int(sys.argv[3]),
        bool(sys.argv[4]),
        bool(sys.argv[5]),
    )
)
