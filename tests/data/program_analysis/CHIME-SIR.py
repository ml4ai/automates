def get_beta(intrinsic_growth_rate, gamma,
        susceptible, relative_contact_rate,
        beta):
    inv_contact_rate = 1.0 - relative_contact_rate               # get_beta_icr_exp
    updated_growth_rate = intrinsic_growth_rate + gamma          # get_beta_ugr_exp
    beta = updated_growth_rate / susceptible * inv_contact_rate  # get_beta_beta_exp

    return beta


def get_growth_rate(doubling_time, growth_rate):
                                                            # ggr_cond
    if doubling_time == 0:                                  # ggr_cond_b0_cond
        growth_rate = 0                                     # ggr_cond_b0_exp
    else:
        growth_rate = 2.0 ** (1.0 / doubling_time) - 1.0    # ggr_cond_b1_exp
    
    return growth_rate


def sir(s, i, r, beta, gamma, n):
    s_n = (-beta * s * i) + s               # sir_s_n_exp
    i_n = (beta * s * i - gamma * i) + i    # sir_i_n_exp
    r_n = gamma * i + r                     # sir_r_n_exp

    scale = n / (s_n + i_n + r_n)           # sir_scale_exp

    s = s_n * scale                         # sir_s_exp
    i = i_n * scale                         # sir_i_exp
    r = r_n * scale                         # sir_r_exp
    return (s, i, r)


def sim_sir(s_n, i_n, r_n, gamma, i_day,
            N_p, N_t, betas, days, T, S, E, I, R):

    n = s_n + i_n + r_n                     # simsir_n_exp
    d = i_day                               # simsir_d_exp

    idx = 1                                 # simsir_idx_exp
    for p_idx in range(N_p):                # simsir_loop_1
        beta = betas[p_idx]                 # simsir_loop_1_beta_exp
        N_d = days[p_idx]                   # simsir_loop_1_N_d_exp
        for d_idx in range(N_d):            # simsir_loop_1_1
            T[idx] = d                      # simsir_loop_1_1_T_exp
            S[idx] = s_n                    # simsir_loop_1_1_S_exp
            I[idx] = i_n                    # simsir_loop_1_1_I_exp
            R[idx] = r_n                    # simsir_loop_1_1_R_exp
            idx += 1                        # simsir_loop_1_1_idx_exp
            (s_n, i_n, r_n) = sir(s_n, i_n, r_n, beta, gamma, n)  # simsir_loop_1_1_call_sir_exp
            d += 1                          # simsir_loop_1_1_d_exp

    T[idx] = d                              # simsir_T_exp
    S[idx] = s_n                            # simsir_S_exp
    I[idx] = i_n                            # simsir_I_exp
    R[idx] = r_n                            # simsir_R_exp

    return (s_n, i_n, r_n, E)


def main():
    growth_rate = 0.0                             # main_gr_exp
    beta = 0.0                                    # main_beta_exp

    i_day = 17.0                                  # main_i_day_exp
    n_days = 20                                   # main_n_days_exp
    N_p = 3                                       # main_N_p_exp
    N_t = 121                                     # main_N_t_exp
    infections_days = 14.0                        # main_inf_days_exp
    relative_contact_rate = 0.05                  # main_rcr_exp
    gamma = 1.0 / infections_days                 # main_gamma_exp

    policys_betas = [0.0] * N_p  # TODO size      # main_pbetas_seq
    policy_days = [0] * N_p                       # main_pdays_seq
    T = [0.0] * N_t                               # main_T_seq
    S = [0.0] * N_t                               # main_S_seq
    E = [0.0] * N_t                               # main_E_seq
    I = [0.0] * N_t                               # main_I_seq
    R = [0.0] * N_t                               # main_R_seq
    
    s_n = 1000                                    # main_s_n_exp
    i_n = 1                                       # main_i_n_exp
    r_n = 1                                       # main_r_n_exp

    for p_idx in range(N_p):                      # main_loop_1
        doubling_time = (p_idx - 1.0) * 5.0       # main_loop_1_dtime_exp

        growth_rate = get_growth_rate(doubling_time, growth_rate)  # main_loop_1_gr_exp
        beta = get_beta(growth_rate, gamma, s_n,                   # main_loop_1_beta_exp
                        relative_contact_rate, beta)
        policys_betas[p_idx] = beta                                # main_loop_1_pbetas_exp
        policy_days[p_idx] = n_days * p_idx                        # main_loop_1_pdays_exp

    (s_n, i_n, r_n, E) = sim_sir(s_n, i_n, r_n, gamma, i_day,      # main_call_simsir_exp
        N_p, N_t, policys_betas, policy_days,
        T, S, E, I, R)

    print("s_n: " + str(s_n))
    print("i_n: " + str(i_n))
    print("r_n: " + str(r_n))
    print("E: " + str(E))

main()

