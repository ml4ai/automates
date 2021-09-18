import sys


def main(x, c):
    a = 0
    for i in range(0, c):
        a = a + (x * i)
    return a


print(
    main(
        int(sys.argv[1]),
        int(sys.argv[2]),
    )
)
