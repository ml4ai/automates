import sys


def main(x, y):
    arr = [1, 2, 3, 4]
    a = arr[(x + y * 3) % 4]
    return a


print(main(int(sys.argv[1]), int(sys.argv[2])))
