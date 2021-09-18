import sys


def main(x, y, c1, c2, c3):
    a = 0
    if c1 < c2:
        if c3:
            a = a + x
        else:
            a = a * x
    else:
        if c3:
            a = a + y
        else:
            a = a * y
    return a


print(
    main(
        int(sys.argv[1]),
        int(sys.argv[2]),
        int(sys.argv[3]),
        int(sys.argv[4]),
        int(sys.argv[5]),
    )
)
