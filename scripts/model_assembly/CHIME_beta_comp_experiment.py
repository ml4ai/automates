"""
PURPOSE: Simple experiment to see the difference in results of the CHIME model
when beta is calculated during the simulation, as opposed to when beta is
pre-computed (as it is in the original Penn-CHIME).
"""


from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np

# Some assumptions for the sake of argument
infectious_days = 14
gamma = 1 / infectious_days
relative_contact_rate = 0.05


def main():
    # More assumptions for the sake of argument
    policy_days = [60, 120]
    doubling_times = [4, 21]
    S0 = 6800000
    I0 = 100
    R0 = 0
    start_day = 1
    policies = [
        [get_beta(get_growth_rate(dtimes), S0), pdays]
        for pdays, dtimes in zip(policy_days, doubling_times)
    ]

    (D1, S1, I1, R1, E1) = sim_sir(S0, I0, R0, start_day, policies)

    (D2, S2, I2, R2, E2) = sim_sir_fixed(
        S0, I0, R0, start_day, policy_days, doubling_times
    )

    plt.figure()
    plt.plot(D1, S1, color="blue", label="Susceptible (pre-comp)")
    plt.plot(
        D2, S2, color="blue", linestyle="--", label="Susceptible (co-comp)"
    )

    plt.plot(D1, I1, color="red", label="Infected (pre-comp)")
    plt.plot(D2, I2, color="red", linestyle="--", label="Infected (co-comp)")

    plt.plot(D1, R1, color="green", label="Recovered (pre-comp)")
    plt.plot(
        D2, R2, color="green", linestyle="--", label="Recovered (co-comp)"
    )

    plt.plot(D1, E1, color="purple", label="Ever Infected (pre-comp)")
    plt.plot(
        D2,
        E2,
        color="purple",
        linestyle="--",
        label="Ever Infected (co-comp)",
    )

    plt.axvline(61, color="grey", linestyle="--")

    plt.title("Comparison of SIR dynamics with pre-computed vs co-computed β")
    plt.xlabel("Time (in days)")
    plt.ylabel("Population (in millions)")

    plt.legend(
        loc="upper center",
        ncol=4,
        bbox_to_anchor=(0.5, -0.06),
    )

    plt.show()


def get_beta(
    intrinsic_growth_rate: float,
    susceptible: float,
) -> float:

    return (
        (intrinsic_growth_rate + gamma)
        / susceptible
        * (1.0 - relative_contact_rate)
    )


def get_growth_rate(doubling_time) -> float:
    return 2.0 ** (1.0 / doubling_time) - 1.0


def sir(
    s: float, i: float, r: float, beta: float, n: float
) -> Tuple[float, float, float]:

    s_n = (-beta * s * i) + s
    i_n = (beta * s * i - gamma * i) + i
    r_n = gamma * i + r
    scale = n / (s_n + i_n + r_n)

    return s_n * scale, i_n * scale, r_n * scale


def sim_sir_fixed(
    s: float,
    i: float,
    r: float,
    i_day: int,
    policy_days: List[int],
    doubling_times: List[int],
):

    s, i, r = (float(v) for v in (s, i, r))
    n = s + i + r
    d = i_day

    total_days = sum(policy_days) + 1
    d_a = np.empty(total_days, "int")
    s_a = np.empty(total_days, "float")
    i_a = np.empty(total_days, "float")
    r_a = np.empty(total_days, "float")

    index = 0
    for p_days, double_time in zip(policy_days, doubling_times):
        beta = get_beta(get_growth_rate(double_time), s)
        for j in range(p_days):
            d_a[index] = d
            s_a[index] = s
            i_a[index] = i
            r_a[index] = r
            index += 1
            s, i, r = sir(s, i, r, beta, n)
            d += 1

    d_a[index] = d
    s_a[index] = s
    i_a[index] = i
    r_a[index] = r

    return (d_a, s_a, i_a, r_a, i_a + r_a)


def sim_sir(
    s: float,
    i: float,
    r: float,
    i_day: int,
    policies: List[Tuple[float, int]],
):

    s, i, r = (float(v) for v in (s, i, r))
    n = s + i + r
    d = i_day

    total_days = 1
    for beta, days in policies:
        total_days += days

    d_a = np.empty(total_days, "int")
    s_a = np.empty(total_days, "float")
    i_a = np.empty(total_days, "float")
    r_a = np.empty(total_days, "float")

    index = 0
    for beta, n_days in policies:
        for _ in range(n_days):
            d_a[index] = d
            s_a[index] = s
            i_a[index] = i
            r_a[index] = r
            index += 1
            s, i, r = sir(s, i, r, beta, n)
            d += 1

    d_a[index] = d
    s_a[index] = s
    i_a[index] = i
    r_a[index] = r

    return (d_a, s_a, i_a, r_a, i_a + r_a)


if __name__ == "__main__":
    main()
