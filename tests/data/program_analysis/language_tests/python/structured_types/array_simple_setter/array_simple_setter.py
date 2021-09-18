import sys


def main(idx, x):
    arr = [1, 2, 3, 4]
    arr[idx] = x
    return arr


print(main(int(sys.argv[1]), int(sys.argv[2])))
