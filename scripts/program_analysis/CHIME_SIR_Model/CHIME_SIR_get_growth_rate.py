def get_growth_rate(doubling_time): 
    if doubling_time == 0:  
        growth_rate = 0  
    else:
        growth_rate = 2.0 ** (1.0 / doubling_time) - 1.0 

    return growth_rate 