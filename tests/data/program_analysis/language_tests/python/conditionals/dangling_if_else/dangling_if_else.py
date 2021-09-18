import sys


def main(x, y, c1, c2):
    a = 0
    b = 0
    if c1 < c2:
        a = a + x
        if a > y:
            a = a - y
    else:
        a = a + y

    if c1 > c2:
        b = b + x
        if b > y:
            b = b - y
        else:
            b = b + y

    return a, b


print(
    main(
        int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    )
)
