import sys


def main(x, c):
    a = 0
    while c > 0:
        a = a + (x * c)
        c = c - 1
    return a


print(
    main(
        int(sys.argv[1]),
        int(sys.argv[2]),
    )
)
