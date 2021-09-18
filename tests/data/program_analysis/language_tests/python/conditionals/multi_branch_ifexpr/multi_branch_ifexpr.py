import sys


def main(x, y, c1, c2):
    a = 0
    if c1 < c2:
        a = a + x
    elif c2 > c1:
        a = a + y
    else:
        a = a + x + y
    return a


print(
    main(
        int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    )
)
