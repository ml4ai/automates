import math, sys

def simulate():
    I = 1.0
    beta = 0.1
    gamma = 0.05
    iota = 0.01
    N = 1000.0
    delta_t = 0.1

    L = beta * (I + iota) / N
    val1 = -L * delta_t
    ifrac = 1.0 - math.exp(val1)

    print(f"PY: beta = {beta}, gamma = {gamma}, iota = {iota}, N = {N}, delta_t = {delta_t}")
    print(f"PY: lambda = {L}, val1 = {val1}, ifrac = {ifrac}")

simulate()

