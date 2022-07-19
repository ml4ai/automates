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