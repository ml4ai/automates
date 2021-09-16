def main(a, x1, x2):
    a = mutate(a, x1, x2)
    return a


def mutate(n, x1, x2):
    mut_n = x1 * n + x2
    return mut_n
