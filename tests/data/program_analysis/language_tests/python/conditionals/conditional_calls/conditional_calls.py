import sys


def main(x, y, c1, c2):
    a = 0
    b = 0
    if c1 < c2:
        a = fizz(x, y)
        b = buzz(x, y)
    else:
        a = buzz(x, y)
        b = fizz(x, y)
    return a, b


def fizz(x, y):
    return x + y


def buzz(x, y):
    return x * y


print(
    main(
        int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    )
)
