import sys


def main(k1, k2, k3, x1, x2, x3):
    d = {k1: x1, k2: x2, k3: x3}
    return d


print(
    main(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3],
        int(sys.argv[4]),
        int(sys.argv[5]),
        int(sys.argv[6]),
    )
)
