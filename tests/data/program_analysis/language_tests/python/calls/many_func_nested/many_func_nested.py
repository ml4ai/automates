import sys


def main(a, x1, x2, x3):
    a = mutate(a, x1, x2, x3)
    return a


def mutate(n, x1, x2, x3):
    mut_n = x1 * n
    mut_n = increment(mut_n, x2, x3)
    return mut_n


def increment(n, x1, x2):
    inc_n = n + x1
    inc_n = div(inc_n, x2)
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
