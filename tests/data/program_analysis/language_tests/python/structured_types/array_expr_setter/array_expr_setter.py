import sys


def main(x, y, a):
    arr = [1, 2, 3, 4]
    arr[(x + y * 3) % 4] = a
    return arr


print(main(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])))
