import sys


def main(x, y, c1, c2, c3, c4):
    a = 0
    if c1 < c2:
        a = a + x
    elif c2 > c1:
        a = a + y
    elif c3 > c2:
        a = a - x
        if c1 == c2:
            a = 0
    elif c4 > c3:
        a = a - y
        if c1 == c2:
            a = 10
        else:
            a = 0
    elif c2 > c4:
        a = a + x + y
    else:
        a = a - x - y
    return a


print(
    main(
        int(sys.argv[1]),
        int(sys.argv[2]),
        int(sys.argv[3]),
        int(sys.argv[4]),
        int(sys.argv[5]),
        int(sys.argv[6]),
    )
)
