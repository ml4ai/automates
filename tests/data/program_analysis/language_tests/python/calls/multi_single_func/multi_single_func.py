def main():
    a = 1
    b = 2
    c = 3

    x1_a = 2
    x1_b = 4
    x1_c = 2

    x2_a = -4
    x2_b = -5
    x2_c = -6

    a = mutate(a, x1_a, x2_a)
    b = mutate(b, x1_b, x2_b)
    c = mutate(c, x1_c, x2_c)

    f_abc = (a + b) / c
    return f_abc


def mutate(n, x1, x2):
    mut_n = x1 * n + x2
    return mut_n


print(main())
