import sys


def main(c1, c2, c3, c4):
    a = 0
    for i1 in range(c1):
        for i2 in range(c2):
            for i3 in range(c3):
                for i4 in range(c4):
                    a += 1
    return a


print(
    main(
        int(sys.argv[1]),
        int(sys.argv[2]),
        int(sys.argv[3]),
        int(sys.argv[4]),
    )
)
