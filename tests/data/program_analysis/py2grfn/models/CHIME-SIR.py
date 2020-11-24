def get_beta(intrinsic_growth_rate, gamma,
        susceptible, relative_contact_rate,
        beta):
    inv_contact_rate = 1.0 - relative_contact_rate
    updated_growth_rate = intrinsic_growth_rate + gamma
    beta = updated_growth_rate / susceptible * inv_contact_rate

    return beta

def get_growth_rate(doubling_time, growth_rate):
    if doubling_time == 0:
        growth_rate = 0
    else:
        growth_rate = 2.0 ** (1.0 / doubling_time) - 1.0
    
    return growth_rate

def sir(s, i, r, beta, gamma, n):
    s_n = (-beta * s * i) + s
    i_n = (beta * s * i - gamma * i) + i
    r_n = gamma * i + r

    scale = n / (s_n + i_n + r_n)

    s = s_n * scale
    i = i_n * scale
    r = r_n * scale
    return (s, i, r)

def sim_sir(s_n, i_n, r_n, gamma, i_day, 
        N_p, N_t, betas, days, T, S, E, I, R):

    n = s_n + i_n + r_n
    d = i_day

    idx = 1
    for p_idx in range(N_p):
        beta = betas[p_idx]
        N_d = days[p_idx]
        for d_idx in range(N_d):
            T[idx] = d
            S[idx] = s_n
            I[idx] = i_n
            R[idx] = r_n
            idx += 1
            (s_n, i_n, r_n) = sir(s_n, i_n, r_n, beta, gamma, n)
            d += 1


    T[idx] = d
    S[idx] = s_n
    I[idx] = i_n
    R[idx] = r_n

    return (s_n, i_n, r_n, E)


def main():
    growth_rate = 0.0
    beta = 0.0

    i_day = 17.0
    n_days = 20
    N_p = 3
    N_t = 121
    infections_days = 14.0
    relative_contact_rate = 0.05
    gamma = 1.0 / infections_days

    policys_betas = [0.0] * N_p # TODO size
    policy_days = [0] * N_p
    T = [0.0] * N_t
    S = [0.0] * N_t
    E = [0.0] * N_t 
    I = [0.0] * N_t 
    R = [0.0] * N_t
    
    s_n = 1000
    i_n = 1
    r_n = 1

    for p_idx in range(N_p):
        doubling_time = (p_idx - 1.0) * 5.0

        growth_rate = get_growth_rate(doubling_time, growth_rate)
        beta = get_beta(growth_rate, gamma, s_n, 
            relative_contact_rate, beta)
        policys_betas[p_idx] = beta
        policy_days[p_idx] = n_days * p_idx

    (s_n, i_n, r_n, E) = sim_sir(s_n, i_n, r_n, gamma, i_day,
        N_p, N_t, policys_betas, policy_days,
        T, S, E, I, R)

    print("s_n: " + str(s_n))
    print("i_n: " + str(i_n))
    print("r_n: " + str(r_n))
    print("E: " + str(E))

main()

