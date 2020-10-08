# from os.path import join
# import json
# import time
# import sys
# import os
from itertools import chain
import time

import numpy as np
from mpi4py import MPI


COMM = MPI.COMM_WORLD


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
    return n


def split(container, count):
    """
    Simple function splitting a container into equal length chunks.
    Order is not preserved but this is potentially an advantage depending on
    the use case.
    """
    return [container[_i::count] for _i in range(count)]


num_examples = 100
if COMM.rank == 0:
    print(f"BEGIN isPrime MPI test with {num_examples} examples")
    data = np.array(list(range(1, num_examples)), np.int32)
    jobs = split(data, COMM.size)
else:
    jobs = []


# Scatter jobs across cores.
jobs = COMM.scatter(jobs, root=0)

results = []
for num_to_check in jobs:
    results.append(square(num_to_check))

# Gather results on rank 0.
results = COMM.gather(results, root=0)

if COMM.rank == 0:
    # Flatten list of lists.
    # res = list(chain.from_iterable(results))
    print(f"END isPrime MPI test with {num_examples} examples")
    # print(f"FOUND {sum(res)} primes")
