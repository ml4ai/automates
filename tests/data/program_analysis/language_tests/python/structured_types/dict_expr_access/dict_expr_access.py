import sys


def main(x):
    d = {100: -1, 200: -2, 300: -3}
    a = d[x * 100]
    return a


print(main(int(sys.argv[1])))
