import sys


def main(x):
    d = {100: 1, 200: 2, 300: 3}
    d[x] = -1
    return d


print(main(int(sys.argv[1])))
