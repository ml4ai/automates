import sys


def main(c1):
    i = 0
    x = 0
    while i <= c1:
        j = i
        while j < 5:
            x = x + i
            j = j + 1
        i = j
    return x


print(
    main(
        int(sys.argv[1]),
    )
)
