import sys
import math


def main(x1, x2, x3, x4):
    a = mutate(x1, abs(x2) + 2, x3, math.log(x4, 3))
    return a


def mutate(n, x1, x2, x3):
    mut_n = x1 * n
    mut_n = round(increment(mut_n, x2, x3))
    return mut_n


def increment(n, x1, x2):
    inc_n = n + x1
    inc_n = math.sqrt(div(inc_n, max(x1, x2)) + 10)
    return inc_n


def div(n, x):
    div_n = n / x
    return div_n


print(
    main(
        float(sys.argv[1]),
        float(sys.argv[2]),
        float(sys.argv[3]),
        float(sys.argv[4]),
    )
)
