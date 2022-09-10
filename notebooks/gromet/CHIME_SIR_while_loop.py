def get_beta(intrinsic_growth_rate, gamma,           
             susceptible, relative_contact_rate):    
    inv_contact_rate = 1.0 - relative_contact_rate  
    updated_growth_rate = intrinsic_growth_rate + gamma  
    beta = updated_growth_rate / susceptible * inv_contact_rate 
 
    return beta  

def get_growth_rate(doubling_time): 
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
    return s, i, r  

def sim_sir(s, i, r, gamma, i_day, 
            N_p, betas, days, 
            d_a, s_a, i_a, r_a, e_a  
            ):
    n = s + i + r 
    d = i_day 
    index = 0  
    p_idx = 0 

    while p_idx < N_p:  
        beta = betas[p_idx]  
        n_days = days[p_idx]  
        
        d_idx = 0 
        while d_idx < n_days:  
            d_a[index] = d  
            s_a[index] = s  
            i_a[index] = i  
            r_a[index] = r  
            e_a[index] = i + r 
            index = index + 1  

            s, i, r = sir(s, i, r, beta, gamma, n) 
            d = d + 1  
            d_idx = d_idx + 1 
        p_idx = p_idx +  1 
    
    d_a[index] = d 
    s_a[index] = s 
    i_a[index] = i 
    r_a[index] = r 
    e_a[index] = i + r 

    return s, i, r, d_a, s_a, i_a, r_a, e_a 

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
                                           
    #print("s_n: " + str(s_n))            
    #print("i_n: " + str(i_n))            
    #print("r_n: " + str(r_n))            
    #print("E: " + str(e_a))              

    return d_a, s_a, i_a, r_a, e_a  

# main() 
