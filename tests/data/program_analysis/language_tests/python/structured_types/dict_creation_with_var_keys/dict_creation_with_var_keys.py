import sys


def main(x1, x2, x3):
    d = {x1: 1, x2: 2, x3: 3}
    return d


print(main(sys.argv[1], sys.argv[2], sys.argv[3]))
