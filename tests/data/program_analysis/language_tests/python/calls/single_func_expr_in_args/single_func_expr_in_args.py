import sys


def main(a, x1, x2):
    a = mutate(a * x1, x2)
    return a


def mutate(n, x):
    mut_n = n + x
    return mut_n


print(
    main(
        int(sys.argv[1]),
        int(sys.argv[2]),
        int(sys.argv[3]),
    )
)
