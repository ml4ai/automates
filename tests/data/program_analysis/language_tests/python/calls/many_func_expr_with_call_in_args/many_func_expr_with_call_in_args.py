import sys


def main(a, x1, x2, x3):
    return div(mutate(a, x1) + x2, x3)


def mutate(n, x):
    return x * n


def div(n, x):
    return n / x


print(
    main(
        int(sys.argv[1]),
        int(sys.argv[2]),
        int(sys.argv[3]),
        int(sys.argv[4]),
    )
)
