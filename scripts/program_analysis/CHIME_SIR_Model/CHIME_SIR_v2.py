### =============================================================================
### NOTATIONAL CONVENTIONS:
###   Comments starting with single hash - '#' - are "normal" comments
###   Comments starting with double hash - '##' - represent name corresopnding
###       named component in hand-developed GroMEt representation
###   Comments starting with triple_hash - '###' - represent comment about differences
###       from original CHIME sir.py:
###       https://github.com/CodeForPhilly/chime/blob/develop/src/penn_chime/model/sir.py
### =============================================================================


# ===============================================================================
# get_beta
# Calculates a rate of exposure given an intrinsic growth rate for COVID-19
# -------------------------------------------------------------------------------
#     Input Variables:
#     intrinsic_growth_rate   Rate of spread of COVID-19 cases
#     gamma         The expected recovery rate from COVID-19 for infected individuals
#     s_c           Current amount of individuals that are susceptible
#     contact_rate  The relative contact rate amongst individuals in the population
#
#     State Variables:
#     inv_contact_rate      The inverse rate of contact between individuals in the population
#     updated_growth_rate   The intrinsic growth rate adjusted for the recovery rate from infection
#
#     Output Variables:
#     beta              The rate of exposure of individuals to persons infected with COVID-19
#
# -------------------------------------------------------------------------------
#  Called by:   main
#  Calls:       None
# ==============================================================================
def get_beta(intrinsic_growth_rate, gamma,           # get_beta: ID 0 
             susceptible, relative_contact_rate):    # instrinsic_groth rate: ID 5, gamma: ID 6, susceptible: ID 7, rel_cont_rate: ID 8
    #"""
    #Calculates a rate of exposure given an intrinsic growth rate for COVID-19
    #:param intrinsic_growth_rate: Rate of spread of COVID-19 cases
    #:param gamma: The expected recovery rate from COVID-19 for infected individuals
    #:param susceptible: Current amount of individuals that are susceptible
    #:param relative_contact_rate: The relative contact rate amongst individuals in the population
    #:return: beta: The rate of exposure of individuals to persons infected with COVID-19
    #"""
    inv_contact_rate = 1.0 - relative_contact_rate  # inv_contact_rate: ID 9 = 1.0 - ID 8
    updated_growth_rate = intrinsic_growth_rate + gamma  # updated_growth_rate: ID 10 = ID 5 + ID 6
    beta = updated_growth_rate / susceptible * inv_contact_rate # beta: ID 11 = ID 10 / ID 7 * ID 9
 
    return beta  # returns ID 11


# ===============================================================================
# GET_GROWTH_RATE, subroutine, by P. Hein
# Calculate the expected growth rate of COVID-19 infections given a doubling time
# -------------------------------------------------------------------------------
#     Input Variables:
#     doubling_time     The time required for the amount of COVID-19 cases to double
#
#     Output Variables:
#     growth_rate       Rate of spread of COVID-19 cases
#
# -------------------------------------------------------------------------------
#  Called by:   main
#  Calls:       None
# ==============================================================================
def get_growth_rate(doubling_time): # get_growth_rate: ID 1, doubling_time: ID 12
    #"""
    #Calculate the expected growth rate of COVID-19 infections given a doubling time
    #:param doubling_time: The time required for the amount of COVID-19 cases to double
    #:return: growth_rate: Rate of spread of COVID-19 cases.
    #"""
    ## ggr_cond
    if doubling_time == 0:  # ID 12 == 0
        growth_rate = 0  # growth_rate: ID 13
    else:
        growth_rate = 2.0 ** (1.0 / doubling_time) - 1.0 # growth_rate: ID 13 = expr / ID 12

    return growth_rate # return ID 13


# ===============================================================================
#  SIR, Subroutine, P. Hein
#  Updates all disease states given the current state values
# -------------------------------------------------------------------------------
#     Input/Output Variables:
#     s           Current amount of individuals that are susceptible
#     i           Current amount of individuals that are infectious
#     r           Current amount of individuals that are recovered
#     beta        The rate of exposure of individuals to persons infected with COVID-19
#     gamma       Rate of recovery for infected individuals
#     n           Total population size
#
#     State Variables:
#     s_n         Update to the amount of individuals that are susceptible
#     i_n         Update to the amount of individuals that are infectious
#     r_n         Update to the amount of individuals that are recovered
#     scale       A scaling factor to compute updated disease variables
#
# -------------------------------------------------------------------------------
#  Called by:   sim_sir
#  Calls:       None
# ==============================================================================
def sir(s, i, r, beta, gamma, n): # sir: ID 2 s: ID 14, i: ID 15, r: ID 16, beta: ID 17, gamma: ID 18, n: ID 19
    #"""
    #The SIR model, one time step
    #:param s: Current amount of individuals that are susceptible
    #:param i: Current amount of individuals that are infectious
    #:param r: Current amount of individuals that are recovered
    #:param beta: The rate of exposure of individuals to persons infected with COVID-19
    #:param gamma: Rate of recovery for infected individuals
    #:param n: Total population size
    #:return:
    #"""
    s_n = (-beta * s * i) + s  # s_n: ID 20 = ID 17 * ID 14 * ID 15 + ID 14
    i_n = (beta * s * i - gamma * i) + i # i_n: ID 21 = ID 17 * ID 14 * ID 15 - ID 18 * ID 15 + ID 15
    r_n = gamma * i + r  # r_n: ID 22 = ID 18 * ID 15 + ID 16

    scale = n / (s_n + i_n + r_n) # scale: ID 23 = ID 19 / (ID 20 + ID 21 + ID 22)

    s = s_n * scale # ID 14 = ID 20 * ID 23 
    i = i_n * scale # ID 15 = ID 21 * ID 23
    r = r_n * scale # ID 16 = ID 22 * ID 23
    return s, i, r  # return ID 14, ID 15, ID 16 


# ===============================================================================
# SIM_SIR, subroutine, by P. Hein
# Simulates a COVID-19 outbreak where a policy intervention is attempted in
# order to lower the relative contact rate amongst individuals.
# -------------------------------------------------------------------------------
#     Input/Output Variables:
#     s           Current amount of individuals that are susceptible
#     i           Current amount of individuals that are infectious
#     r           Current amount of individuals that are recovered
#     d_a         An array (list) used to record the current day during the simulation
#     s_a         An array (list) used to record the susceptible population changes during the simulation
#     i_a         An array (list) used to record the currently infected population changes during the simulation
#     r_a         An array (list) used to record the recovered population changes during the simulation
#     e_a         An array (list) used to record the total (ever) infected (i + r) population changes during the simulation
#
#     Input Variables:
#     gamma       The expected recovery rate from COVID-19 for infected individuals
#     i_day       Start day of COVID-19 infections
#     N_p         Number of policies to use for the simulation
#     betas       An array of beta values with one entry per beta
#     days        An array of time periods with one entry per policy
#
#     State Variables:
#     n           Total population size
#     beta        The rate of exposure of indidivuals to persons infected with COVID-19
#     n_days      The amount of days for for the current policy to be simulated
#     d           Tracks the current day in the simulation
#     p_idx       Index to use for accessing policy variables
#     d_idx       Index to be used for days in the current policy
#     idx         Index to be used to access arrays for storing simulated outputs
#     total_inf   The total population that is ever infected at a timestep during the simulation
#
# -------------------------------------------------------------------------------
#  Called by:   main
#  Calls:       sir
# ==============================================================================
# sim_sir: ID 3
def sim_sir(s, i, r, gamma, i_day, # s: ID 24, i: ID 25, r: ID 26, gamma: ID 27, i_day: ID 28
            N_p, betas, days, # N_p: ID 29, betas: ID 30, days: ID 31 
            d_a, s_a, i_a, r_a, e_a  # d_a: ID 32, s_a: ID 33, i_a: ID 34, r_a: ID 35, e_a: ID 36
            ):
    n = s + i + r # n: ID 37 = ID 24 + ID 25 + ID 26
    d = i_day # d: ID 38 = ID 28

    ### total_days from original CHIME sim_sir was used to determine the size of the
    ### the state bookkeeping across the simulation.
    ### Here, the array size is for this bookkeeping is determined outside of sim_sir
    ### and the arrays are passed in as arguments.

    index = 0  # ID 39
    # for p_idx in range(N_p):  #
    p_idx = 0 # NOTE: ADDED
    while p_idx < N_p:  # NOTE: CHANGED
        beta = betas[p_idx]  #
        n_days = days[p_idx]  #
        # for d_idx in range(n_days):  #
        d_idx = 0 # NOTE: ADDED
        while d_idx < n_days:  # NOTE: CHANGED
            d_a[index] = d  # ID 32 index ID 39 = ID 38
            s_a[index] = s  # ID 33  ""         = ID 24
            i_a[index] = i  # ID 34  ""         = ID 25
            r_a[index] = r  # ID 35  ""         = ID 26
            e_a[index] = i + r # ID 36 ""       = ID 25 + ID 26
            index = index + 1  #

            s, i, r = sir(s, i, r, beta, gamma, n) # ID 24, ID 25, ID 26 = Call ID 2(ID 24, ID 25, ID 26, ??, ID 27, ID 37)
            d = d + 1  # ID 38
            d_idx = d_idx + 1 # NOTE: ADDED
        p_idx = p_idx +  1 # NOTE: ADDED

    # Record the last update (since sir() is called at the tail of the inner loop above)
    d_a[index] = d # ID 32 = ID 38
    s_a[index] = s # ID 33 = ID 24
    i_a[index] = i # ID 34 = ID 25
    r_a[index] = r # ID 35 = ID 26
    e_a[index] = i + r # ID 36 = ID 25 + ID 26

    return s, i, r, d_a, s_a, i_a, r_a, e_a # ID 24, ID 25, ID 26, ID 32, ID 33, ID 34, ID 35, ID 36


def main(): # main: ID 4
    #"""
    #implements generic CHIME configuration without hospitalization calculation
    #initializes parameters and population, calculates policy, and runs dynamics
    #:return:
    #"""
    ###

    # initial parameters
    i_day = 17.0  # ID 51
    n_days = 20   # ID 52
    N_p = 3       # ID 53
    N_t = 121     # ID 54
    infections_days = 14.0  # ID 55
    relative_contact_rate = 0.05  # ID 56
    gamma = 1.0 / infections_days  # ID 57 = expr / ID 55

    # initialize lists for policy and simulation state bookkeeping
    policys_betas = [0.0] * N_p  # ID 58 = expr * ID 53
    policy_days = [0] * N_p      # ID 59 = expr * ID 53
    d_a = [0.0] * N_t  # ID 60 = expr * ID 54
    s_a = [0.0] * N_t  # ID 61    ""
    i_a = [0.0] * N_t  # ID 62    ""
    r_a = [0.0] * N_t  # ID 63    "" 
    e_a = [0.0] * N_t  # ID 64    "" 

    # initial population
    s_n = 1000 # ID 65
    i_n = 1  # ID 66
    r_n = 1  # ID 67

    # calculate beta under policy
    # for p_idx in range(N_p):  ## main_loop_1
    p_idx = 0 # NOTE: ADDED
    while p_idx < N_p:  ## main_loop_1 NOTE: CHANGED
        doubling_time = (p_idx - 1.0) * 5.0  ## main_loop_1_dtime_exp

        growth_rate = get_growth_rate(doubling_time) # Call ID 1 
        beta = get_beta(growth_rate, gamma, s_n,     # Call ID 1
                        relative_contact_rate)
        policys_betas[p_idx] = beta  ## main_loop_1_pbetas_exp
        policy_days[p_idx] = n_days * p_idx  ## main_loop_1_pdays_exp
        p_idx = p_idx + 1

    # simulate dynamics (corresponding roughly to run_projection() )
    # 65  66   67  60   61   62   63   64 
    s_n, i_n, r_n, d_a, s_a, i_a, r_a, e_a \
        = sim_sir(s_n, i_n, r_n, gamma, i_day,  ## main_call_simsir_exp
                  N_p, policys_betas, policy_days,
                  d_a, s_a, i_a, r_a, e_a) # Call ID 3(65,66,67,57,51
                                           #           53,58,59,
                                           #           60,61,62,63,64)

    #print("s_n: " + str(s_n))            # Call ID 75(Call ID 74(ID 65))
    #print("i_n: " + str(i_n))            # Call ID 75(Call ID 74(ID 66))
    #print("r_n: " + str(r_n))            # Call ID 75(Call ID 74(ID 67))
    #print("E: " + str(e_a))              # Call ID 75(Call ID 74(ID 64))

    return d_a, s_a, i_a, r_a, e_a  # return simulated dynamics 60,61,62,63,64


#main() # Call ID 4

# ID matching looks good - tito 5/3/22
