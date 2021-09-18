import sys


def main(k):
    d = {"a": 1, "b": 2, "c": 3}
    v = d[k]
    return v


print(main(sys.argv[1]))
