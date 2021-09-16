def main(a, x1, x2, x3):
    return mutate(a, x1, x2, x3)


def mutate(n, x1, x2, x3):
    mut_n = x1 * n
    return increment(mut_n, x2, x3)


def increment(n, x1, x2):
    inc_n = n + x1
    return div(inc_n, x2)


def div(n, x):
    return n / x
