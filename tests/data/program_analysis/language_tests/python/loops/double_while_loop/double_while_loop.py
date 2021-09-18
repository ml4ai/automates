import sys


def main(c1, c2):
    i = 0
    x = 0
    while i <= c1:
        j = 0
        while j < c2:
            x = x + (i * j)
            j = j + 1
        i = i + 1
    return x


print(
    main(
        int(sys.argv[1]),
        int(sys.argv[2]),
    )
)
