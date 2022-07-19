def get_beta(intrinsic_growth_rate, gamma,           
             susceptible, relative_contact_rate):    
    inv_contact_rate = 1.0 - relative_contact_rate  
    updated_growth_rate = intrinsic_growth_rate + gamma  
    beta = updated_growth_rate / susceptible * inv_contact_rate 
 
    return beta  
