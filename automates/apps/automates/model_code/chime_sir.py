def get_beta(intrinsic_growth_rate, gamma, susceptible, relative_contact_rate, beta):
    inv_contact_rate = 1.0 - relative_contact_rate  # get_beta_icr_exp
    updated_growth_rate = intrinsic_growth_rate + gamma  # get_beta_ugr_exp
    beta = updated_growth_rate / susceptible * inv_contact_rate  # get_beta_beta_exp

    return beta


def get_growth_rate(doubling_time, growth_rate):
    # ggr_cond
    if doubling_time == 0:  # ggr_cond_b0_cond
        growth_rate = 0  # ggr_cond_b0_exp
    else:
        growth_rate = 2.0 ** (1.0 / doubling_time) - 1.0  # ggr_cond_b1_exp

    return growth_rate


def sir(s, i, r, beta, gamma, n):
    s_n = (-beta * s * i) + s  # sir_s_n_exp
    i_n = (beta * s * i - gamma * i) + i  # sir_i_n_exp
    r_n = gamma * i + r  # sir_r_n_exp

    scale = n / (s_n + i_n + r_n)  # sir_scale_exp

    s = s_n * scale  # sir_s_exp
    i = i_n * scale  # sir_i_exp
    r = r_n * scale  # sir_r_exp
    return (s, i, r)


def sim_sir(s_n, i_n, r_n, gamma, i_day, N_p, N_t, betas, days, T, S, E, I, R):

    n = s_n + i_n + r_n  # simsir_n_exp
    d = i_day  # simsir_d_exp

    idx = 1  # simsir_idx_exp
    for p_idx in range(N_p):  # simsir_loop_1
        beta = betas[p_idx]  # simsir_loop_1_beta_exp
        N_d = days[p_idx]  # simsir_loop_1_N_d_exp
        for d_idx in range(N_d):  # simsir_loop_1_1
            T[idx] = d  # simsir_loop_1_1_T_exp
            S[idx] = s_n  # simsir_loop_1_1_S_exp
            I[idx] = i_n  # simsir_loop_1_1_I_exp
            R[idx] = r_n  # simsir_loop_1_1_R_exp
            idx += 1  # simsir_loop_1_1_idx_exp
            (s_n, i_n, r_n) = sir(
                s_n, i_n, r_n, beta, gamma, n
            )  # simsir_loop_1_1_call_sir_exp
            d += 1  # simsir_loop_1_1_d_exp

    T[idx] = d  # simsir_T_exp
    S[idx] = s_n  # simsir_S_exp
    I[idx] = i_n  # simsir_I_exp
    R[idx] = r_n  # simsir_R_exp

    return (s_n, i_n, r_n, E)


def execute(
    growth_rate=0.0,  # main_gr_exp
    beta=0.0,  # main_beta_exp
    i_day=17.0,  # main_i_day_exp
    n_days=20,  # main_n_days_exp
    N_p=3,  # main_N_p_exp
    infections_days=14.0,  # main_inf_days_exp
    relative_contact_rate=0.05,  # main_rcr_exp
    s_n=1000,  # main_s_n_exp
    i_n=1,  # main_i_n_exp
    r_n=1,  # main_r_n_exp
):
    N_t = N_p * n_days + 2  # main_N_t_exp
    gamma = 1.0 / infections_days  # main_gamma_exp

    policys_betas = [0.0] * N_p  # TODO size      # main_pbetas_seq
    policy_days = [0] * N_p  # main_pdays_seq
    T = [0.0] * N_t  # main_T_seq
    S = [0.0] * N_t  # main_S_seq
    E = [0.0] * N_t  # main_E_seq
    I = [0.0] * N_t  # main_I_seq
    R = [0.0] * N_t  # main_R_seq

    for p_idx in range(N_p):  # main_loop_1
        doubling_time = (p_idx - 1.0) * 5.0  # main_loop_1_dtime_exp

        growth_rate = get_growth_rate(doubling_time, growth_rate)  # main_loop_1_gr_exp
        beta = get_beta(
            growth_rate, gamma, s_n, relative_contact_rate, beta  # main_loop_1_beta_exp
        )
        policys_betas[p_idx] = beta  # main_loop_1_pbetas_exp
        policy_days[p_idx] = n_days * p_idx  # main_loop_1_pdays_exp

    (s_n, i_n, r_n, E) = sim_sir(
        s_n,
        i_n,
        r_n,
        gamma,
        i_day,  # main_call_simsir_exp
        N_p,
        N_t,
        policys_betas,
        policy_days,
        T,
        S,
        E,
        I,
        R,
    )

    return (S, E, I, R)


def drive(start, end, step, parameters):
    """
    Allowed parameters:
    # i_day                 : UidJunction("J:main.i_day")
    UidVariable("V:i_day"),
    # n_days                : UidJunction("J:main.n_days")
    UidVariable("V:n_days"),
    # N_p                   : UidJunction("J:main.N_p")
    UidVariable("V:N_p"),
    # infections_days       : UidJunction("J:main.infections_days")
    UidVariable("V:infections_days"),
    # relative_contact_rate : UidJunction("J:main.relative_contact_rate")
    UidVariable("V:relative_contact_rate"),
    # s_n                   : UidJunction("J:main.s_n")
    UidVariable("V:s_n"),
    # i_n                   : UidJunction("J:main.i_n")
    UidVariable("V:i_n"),
    # r_n                   : UidJunction("J:main.r_n")
    UidVariable("V:r_n"),

    Technically, these are initial conditions, but do have a default val:
    # s_n                   : UidJunction("J:main.s_n")
    UidVariable("V:s_n"),
    # i_n                   : UidJunction("J:main.i_n")
    UidVariable("V:i_n"),
    # r_n                   : UidJunction("J:main.r_n")
    UidVariable("V:r_n"),

    Allowed measure selections:
    # out S                 : UidPort("P:main.out.S")
    UidVariable("V:S"),
    # out I                 : UidPort("P:main.out.I")
    UidVariable("V:I"),
    # out R                 : UidPort("P:main.out.R")
    UidVariable("V:R"),
    # out E                 : UidPort("P:main.out.E")
    UidVariable("V:E"),
    Returns:
        [type]: [description]
    """

    param_names_to_vals = {k.split(".")[-1]: v for k, v in parameters.items()}
    (S, E, I, R) = execute(**param_names_to_vals, n_days=end)

    def process_time_step_results(result_arr):
        stepped_results = []
        for i in range(start, end + 1, step):
            stepped_results.append(result_arr[i])
        return stepped_results

    return {
        "P:main.out.S": process_time_step_results(S),
        "P:main.out.E": process_time_step_results(E),
        "P:main.out.I": process_time_step_results(I),
        "P:main.out.R": process_time_step_results(R),
        "J:main.n_days": process_time_step_results(range(end + 1)),
    }
