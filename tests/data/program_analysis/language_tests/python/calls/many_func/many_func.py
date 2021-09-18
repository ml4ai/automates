import sys


def main(a, x1, x2, x3):
    a = mutate(a, x1)
    a = increment(a, x2)
    a = div(a, x3)
    return a


def mutate(n, x):
    mut_n = x * n
    return mut_n


def increment(n, x):
    inc_n = n + x
    return inc_n


def div(n, x):
    div_n = n / x
    return div_n


print(
    main(
        int(sys.argv[1]),
        int(sys.argv[2]),
        int(sys.argv[3]),
        int(sys.argv[4]),
    )
)
