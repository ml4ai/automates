from multiprocessing import Pool, cpu_count
import time

import numpy as np


def isPrime(n):
    # Corner case
    if n <= 1:
        return 0

    # Check from 2 to n-1
    for i in range(2, n):
        if n % i == 0:
            return 0

    return 1


def square(n):
    time.sleep(1)
    return n ** 2


def main():
    num_examples = 100
    print(f"BEGIN isPrime multiprocessing test with {num_examples} examples")
    data = np.array(list(range(1, num_examples)), np.int32)
    with Pool(8) as p:
        res = p.map(square, data)
    print(f"END isPrime multiprocessing test with {num_examples} examples")
    # print(f"FOUND {sum(res)} primes")


if __name__ == "__main__":
    main()
