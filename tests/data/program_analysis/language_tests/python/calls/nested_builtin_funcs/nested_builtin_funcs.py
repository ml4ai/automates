import math
import sys


def main(x1, x2, x3, x4):
    a = min(math.sqrt(x1), math.exp(x2), math.sin(x1 + x2)) + 100
    b = (abs(math.ceil(math.log(x4, 10)) - max(x3, x1, x2)) + 5) / 3
    return 1 + round(math.tanh(math.sin(a + b) - math.cos(a - b)))


print(
    main(
        float(sys.argv[1]),
        float(sys.argv[2]),
        float(sys.argv[3]),
        float(sys.argv[4]),
    )
)
