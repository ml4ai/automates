def main(a, x1, x2):
    a = mutate(a, x1) + x2
    return a


def mutate(n, x1):
    mut_n = x1 * n
    return mut_n
