import sys


def main(x1, x2, x3, x4):
    a = x1 + x2 + x3 + x4
    b = x1 * x2 * x3 * x4
    c = x1 + x2 + x3 - x4
    d = x1 / x2 * x3 * x4

    return a + b + c + d


print(
    main(
        int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    )
)
