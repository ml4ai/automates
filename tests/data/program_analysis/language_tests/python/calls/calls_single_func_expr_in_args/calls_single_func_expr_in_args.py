def main(a, x1, x2):
    a = mutate(a * x1, x2)
    return a


def mutate(n, x):
    mut_n = n + x
    return mut_n
