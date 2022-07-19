def main(): 
    
    i_day = 17.0  
    n_days = 20   
    N_p = 3       
    N_t = 121     
    infections_days = 14.0  
    relative_contact_rate = 0.05  
    gamma = 1.0 / infections_days  
    
    policys_betas = [0.0] * N_p  
    policy_days = [0] * N_p      
    d_a = [0.0] * N_t  
    s_a = [0.0] * N_t  
    i_a = [0.0] * N_t  
    r_a = [0.0] * N_t  
    e_a = [0.0] * N_t  

    s_n = 1000 
    i_n = 1  
    r_n = 1  

    p_idx = 0 
    while p_idx < N_p:  
        doubling_time = (p_idx - 1.0) * 5.0  

        growth_rate = get_growth_rate(doubling_time) 
        beta = get_beta(growth_rate, gamma, s_n,     
                        relative_contact_rate)
        policys_betas[p_idx] = beta  
        policy_days[p_idx] = n_days * p_idx  
        p_idx = p_idx + 1

    
    
    s_n, i_n, r_n, d_a, s_a, i_a, r_a, e_a \
        = sim_sir(s_n, i_n, r_n, gamma, i_day,  
                  N_p, policys_betas, policy_days,
                  d_a, s_a, i_a, r_a, e_a) 
                                           
    return d_a, s_a, i_a, r_a, e_a  
