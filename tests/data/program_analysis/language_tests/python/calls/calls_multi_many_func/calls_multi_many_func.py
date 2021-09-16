def main(a1, a2, a3, x1, x2, x3):
    a1 = mutate(a1, x1)
    a1 = increment(a1, x2)
    a1 = div(a1, x3)

    a2 = mutate(a2, x1)
    a2 = increment(a2, x2)
    a2 = div(a2, x3)

    a3 = mutate(a3, x1)
    a3 = increment(a3, x2)
    a3 = div(a3, x3)

    return a1, a2, a3


def mutate(n, x):
    mut_n = x * n
    return mut_n


def increment(n, x):
    inc_n = n + x
    return inc_n


def div(n, x):
    div_n = n / x
    return div_n
