import sys


def main(x1, x2, x3):
    d = {"a": x1, "b": x2, "c": x3}
    return d


print(main(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])))
