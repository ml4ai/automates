def sir(s, i, r, beta, gamma, n): 
    s_n = (-beta * s * i) + s  
    i_n = (beta * s * i - gamma * i) + i 
    r_n = gamma * i + r  

    scale = n / (s_n + i_n + r_n) 

    s = s_n * scale 
    i = i_n * scale 
    r = r_n * scale 
    return s, i, r  