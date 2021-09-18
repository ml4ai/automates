import sys


def main(idx):
    arr = [1, 2, 3, 4]
    x = arr[idx]
    return x


print(main(int(sys.argv[1])))
