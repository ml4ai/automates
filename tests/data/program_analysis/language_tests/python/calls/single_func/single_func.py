# import sys


def main(a, x1, x2):
    a = mutate(a, x1, x2)
    return a


def mutate(n, x1, x2):
    mut_n = x1 * n + x2
    return mut_n


# print(
#     main(
#         int(sys.argv[1]),
#         int(sys.argv[2]),
#         int(sys.argv[3]),
#     )
# )
