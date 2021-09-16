def main(a, x1, x2, x3):
    return div(mutate(a, x1) + x2, x3)


def mutate(n, x):
    return x * n


def div(n, x):
    return n / x
