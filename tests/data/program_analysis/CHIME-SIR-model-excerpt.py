from typing import Dict, Tuple, Sequence, Optional


def get_growth_rate(doubling_time: Optional[float]) -> float:
    """Calculates average daily growth rate from doubling time."""
    if doubling_time is None or doubling_time == 0.0:
        return 0.0
    return 2.0 ** (1.0 / doubling_time) - 1.0


def get_beta(
    intrinsic_growth_rate: float,
    gamma: float,
    susceptible: float,
    relative_contact_rate: float,
) -> float:
    return (
        (intrinsic_growth_rate + gamma)
        / susceptible
        * (1.0 - relative_contact_rate)
    )


class Sir:
    def __init__(self, p: Parameters):

        ...

        gamma = 1.0 / p.infectious_days
        self.gamma = gamma

        ...

        if p.date_first_hospitalized is None and p.doubling_time is not None:
            ...

            intrinsic_growth_rate = get_growth_rate(p.doubling_time)
            self.beta = get_beta(
                intrinsic_growth_rate, gamma, self.susceptible, 0.0
            )
            self.beta_t = get_beta(
                intrinsic_growth_rate,
                self.gamma,
                self.susceptible,
                p.relative_contact_rate,
            )

        ...

    ...


def sir(
    s: float, i: float, r: float, beta: float, gamma: float, n: float
) -> Tuple[float, float, float]:
    """The SIR model, one time step."""
    s_n = (-beta * s * i) + s
    i_n = (beta * s * i - gamma * i) + i
    r_n = gamma * i + r
    scale = n / (s_n + i_n + r_n)
    return s_n * scale, i_n * scale, r_n * scale

