import numpy as np
import pandas as pd
from typing import Dict, Tuple, Sequence, Optional
from datetime import datetime, timedelta


def sir(
    s: float, i: float, r: float, beta: float, gamma: float, n: float
) -> Tuple[float, float, float]:

    s_n = (-beta * s * i) + s
    i_n = (beta * s * i - gamma * i) + i
    r_n = gamma * i + r
    scale = n / (s_n + i_n + r_n)

    return s_n * scale, i_n * scale, r_n * scale


def sim_sir(
    s: float,
    i: float,
    r: float,
    gamma: float,
    i_day: int,
    policies: Sequence[Tuple[float, int]],
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
            s, i, r = sir(s, i, r, beta, gamma, n)
            d += 1

    d_a[index] = d
    s_a[index] = s
    i_a[index] = i
    r_a[index] = r

    return {
        "day": d_a,
        "susceptible": s_a,
        "infected": i_a,
        "recovered": r_a,
        "ever_infected": i_a + r_a,
    }


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


def get_growth_rate(doubling_time: Optional[float]) -> float:

    if doubling_time is None or doubling_time == 0.0:
        return 0.0

    return 2.0 ** (1.0 / doubling_time) - 1.0


def calculate_dispositions(
    raw: Dict, rates: Dict[str, float], market_share: float
):

    for key, rate in rates.items():
        raw["ever_" + key] = raw["ever_infected"] * rate * market_share
        raw[key] = raw["ever_infected"] * rate * market_share


def calculate_admits(raw: Dict, rates: Dict[str, float]):

    for key, rate in rates.items():
        ever = raw["ever_" + key]
        admit = np.empty_like(ever)
        admit[0] = np.nan
        admit[1:] = ever[1:] - ever[:-1]
        raw["admits_" + key] = admit
        raw[key] = admit


def calculate_census(raw: Dict, lengths_of_stay: Dict[str, int]):

    n_days = raw["day"].shape[0]
    for key, los in lengths_of_stay.items():
        cumsum = np.empty(n_days + los)
        cumsum[: los + 1] = 0.0
        cumsum[los + 1 :] = raw["admits_" + key][1:].cumsum()

        census = cumsum[los:] - cumsum[:-los]
        raw["census_" + key] = census


def run_projection(
    susceptible: float,
    infected: float,
    recovered: float,
    gamma: float,
    i_day: int,
    rates: float,
    days: float,
    market_share: float,
    policy: Sequence[Tuple[float, int]],
):

    raw = sim_sir(susceptible, infected, recovered, gamma, -i_day, policy)

    calculate_dispositions(raw, rates, market_share)
    calculate_admits(raw, rates)
    calculate_census(raw, days)

    return raw


def get_loss(current_hospitalized: float, predicted: float) -> float:
    return (current_hospitalized - predicted) ** 2.0


def get_argmin_ds(census, current_hospitalized: float) -> float:

    peak_day = census.argmax()
    losses = (census[:peak_day] - current_hospitalized) ** 2.0

    return losses.argmin()


def get_argmin_doubling_time(
    susceptible: float,
    infected: float,
    recovered: float,
    gamma: float,
    i_day: int,
    rates: float,
    days: float,
    market_share: float,
    n_days: int,
    current_hospitalized: float,
    intrinsic_growth_rate: float,
    relative_contact_rate: float,
    dts,
):

    losses = np.full(dts.shape[0], np.inf)

    for i, i_dt in enumerate(dts):
        intrinsic_growth_rate = get_growth_rate(i_dt)
        beta = get_beta(intrinsic_growth_rate, gamma, susceptible, 0.0)
        beta_t = get_beta(
            intrinsic_growth_rate, gamma, susceptible, relative_contact_rate
        )

        raw = run_projection(
            susceptible,
            infected,
            recovered,
            gamma,
            i_day,
            rates,
            days,
            market_share,
            [(beta, n_days)],
        )

        peak_admits_day = raw["admits_hospitalized"].argmax()

        if peak_admits_day < 0:
            continue

        predicted = raw["census_hospitalized"][i_day]

        loss = get_loss(current_hospitalized, predicted)
        losses[i] = loss

    min_loss = np.argmin(pd.Series(losses).values)

    return min_loss


def gen_policy(
    mitigation_date: str,
    current_date: str,
    i_day: int,
    n_days: int,
    beta: float,
    beta_t: float,
) -> Sequence[Tuple[float, int]]:

    if mitigation_date is not None:
        current_date_dt = datetime.strptime(current_date, "%m/%d/%Y")
        mitigation_date_dt = datetime.strptime(mitigation_date, "%m/%d/%Y")
        mitigation_day = (current_date_dt - mitigation_date_dt).days
        mitigation_day = -mitigation_day
    else:
        mitigation_day = 0

    total_days = i_day + n_days

    if mitigation_day < -i_day:
        mitigation_day = -i_day

    pre_mitigation_days = i_day + mitigation_day
    post_mitigation_days = total_days - pre_mitigation_days

    return [(beta, pre_mitigation_days), (beta_t, post_mitigation_days)]


def build_sim_sir_w_date_df(
    raw_df: pd.DataFrame, current_date_dt: datetime, keys: Sequence[str]
) -> pd.DataFrame:

    day = raw_df.day
    return pd.DataFrame(
        {
            "day": day,
            "date": day.astype("timedelta64[D]")
            + np.datetime64(current_date_dt),
            **{key: raw_df[key] for key in keys},
        }
    )


def build_floor_df(
    df: pd.DataFrame, keys: Sequence[str], prefix: str
) -> pd.DataFrame:

    return pd.DataFrame(
        {
            "day": df.day,
            "date": df.date,
            **{prefix + key: np.floor(df[prefix + key]) for key in keys},
        }
    )


def CHIME(
    dispositions,
    market_share,
    population,
    infectious_days,
    recovered,
    doubling_time,
    date_first_hospitalized,
    relative_contact_rate,
    n_days,
    current_hospitalized,
    mitigation_date,
    current_date,
):

    rates = {key: d["rate"] for key, d in dispositions.items()}

    days = {key: d["days"] for key, d in dispositions.items()}

    keys = ["susceptible", "infected", "recovered"]

    infected = 1.0 / market_share / hospitalized["rate"]

    susceptible = population - infected

    gamma = 1.0 / infectious_days

    intrinsic_growth_rate = get_growth_rate(doubling_time)

    i_day = 0  ###  Not sure if this is a parameter

    if date_first_hospitalized is None and doubling_time is not None:

        beta = get_beta(intrinsic_growth_rate, gamma, susceptible, 0.0)

        beta_t = get_beta(
            intrinsic_growth_rate, gamma, susceptible, relative_contact_rate
        )

        if mitigation_date is None:
            raw = run_projection(
                susceptible,
                infected,
                recovered,
                gamma,
                i_day,
                rates,
                days,
                market_share,
                [(beta, n_days)],
            )

            i_day = int(
                get_argmin_ds(raw["census_hospitalized"], current_hospitalized)
            )

            raw = run_projection(
                susceptible,
                infected,
                recovered,
                gamma,
                i_day,
                rates,
                days,
                market_share,
                [(beta, n_days)],
            )

        else:
            projections = {}
            best_i_day = -1
            beta_i_day_loss = float("inf")
            for day in range(n_days):
                i_day = day
                raw = run_projection(
                    susceptible,
                    infected,
                    recovered,
                    gamma,
                    i_day,
                    rates,
                    days,
                    market_share,
                    [(beta, n_days)],
                )

                if raw["census_hospitalized"].argmax() < i_day:
                    continue

                loss = get_loss(
                    raw["census_hospitalized"][i_day], current_hospitalized
                )
                if loss < best_i_day_loss:
                    best_i_day_loss = loss
                    best_i_day = i_day

            i_day = best_i_day

    elif date_first_hospitalized is not None and doubling_time is None:

        current_date_dt = datetime.strptime(current_date, "%m/%d/%Y")
        date_first_hospitalized_dt = datetime.strptime(
            date_first_hospitalized, "%m/%d/%Y"
        )

        i_day = (current_date_dt - date_first_hospitalized_dt).days

        dts = np.linspace(1, 15, 15)
        min_loss = get_argmin_doubling_time(
            susceptible,
            infected,
            recovered,
            gamma,
            i_day,
            rates,
            days,
            market_share,
            n_days,
            current_hospitalized,
            intrinsic_growth_rate,
            relative_contact_rate,
            dts,
        )

        doubling_time = dts[min_loss]

        intrinsic_growth_rate = get_growth_rate(doubling_time)
        beta = get_beta(intrinsic_growth_rate, gamma, susceptible, 0.0)
        beta_t = get_beta(
            intrinsic_growth_rate, gamma, susceptible, relative_contact_rate
        )

        raw = run_projection(
            susceptible,
            infected,
            recovered,
            gamma,
            i_day,
            rates,
            days,
            market_share,
            gen_policy(
                mitigation_date, current_date, i_day, n_days, beta, beta_t
            ),
        )

    current_date_dt = datetime.strptime(current_date, "%m/%d/%Y")
    new_date = [current_date_dt + timedelta(int(x)) for x in raw["day"]]
    raw["date"] = [x.strftime("%m/%d/%Y") for x in new_date]

    raw_df = pd.DataFrame(data=raw)
    dispositions_df = pd.DataFrame(
        data={
            "day": raw["day"],
            "date": raw["date"],
            "ever_hospitalized": raw["ever_hospitalized"],
            "ever_icu": raw["ever_icu"],
            "ever_ventilated": raw["ever_ventilated"],
        }
    )

    admits_df = pd.DataFrame(
        data={
            "day": raw["day"],
            "date": raw["date"],
            "admits_hospitalized": raw["admits_hospitalized"],
            "admits_icu": raw["admits_icu"],
            "admits_ventilated": raw["admits_ventilated"],
        }
    )

    census_df = pd.DataFrame(
        data={
            "day": raw["day"],
            "date": raw["date"],
            "census_hospitalized": raw["census_hospitalized"],
            "census_icu": raw["census_icu"],
            "census_ventilated": raw["census_ventilated"],
        }
    )

    infected = raw_df["infected"].values[i_day]
    susceptible = raw_df["susceptible"].values[i_day]
    recovered = raw_df["recovered"].values[i_day]

    intrinsic_growth_rate = get_growth_rate(doubling_time)

    r_t = beta_t / gamma * susceptible
    r_naught = beta / gamma * susceptible

    doubling_time_t = 1.0 / np.log2(beta_t * susceptible - gamma + 1)

    sim_sir_w_date_df = build_sim_sir_w_date_df(raw_df, current_date_dt, keys)

    sim_sir_w_date_floor_df = build_floor_df(sim_sir_w_date_df, keys, "")
    admits_floor_df = build_floor_df(admits_df, dispositions.keys(), "admits_")
    census_floor_df = build_floor_df(census_df, dispositions.keys(), "census_")

    daily_growth_rate = get_growth_rate(doubling_time)
    daily_growth_rate_t = get_growth_rate(doubling_time_t)


if __name__ == "__main__":

    ### Parameters ###

    hospitalized = {"rate": 0.025, "days": 7}
    icu = {"rate": 0.0075, "days": 9}
    ventilated = {"rate": 0.005, "days": 10}

    dispositions = {
        "hospitalized": hospitalized,
        "icu": icu,
        "ventilated": ventilated,
    }

    market_share = 10

    population = 1000

    infectious_days = 14

    recovered = 0

    date_first_hospitalized = "01/01/2020"

    doubling_time = None

    mitigation_date = "01/10/2020"

    n_days = 20

    current_date = "01/15/2020"

    current_hospitalized = 50.0

    relative_contact_rate = 0.05

    CHIME(
        dispositions,
        market_share,
        population,
        infectious_days,
        recovered,
        doubling_time,
        date_first_hospitalized,
        relative_contact_rate,
        n_days,
        current_hospitalized,
        mitigation_date,
        current_date,
    )
