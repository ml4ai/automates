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
def get_beta(intrinsic_growth_rate, gamma,
             susceptible, relative_contact_rate):
    """
    Calculates a rate of exposure given an intrinsic growth rate for COVID-19
    :param intrinsic_growth_rate: Rate of spread of COVID-19 cases
    :param gamma: The expected recovery rate from COVID-19 for infected individuals
    :param susceptible: Current amount of individuals that are susceptible
    :param relative_contact_rate: The relative contact rate amongst individuals in the population
    :return: beta: The rate of exposure of individuals to persons infected with COVID-19
    """
    inv_contact_rate = 1.0 - relative_contact_rate  # The inverse rate of contact between individuals in the population ## get_beta_icr_exp
    updated_growth_rate = intrinsic_growth_rate + gamma  # The intrinsic growth rate adjusted for the recovery rate from infection ## get_beta_ugr_exp
    beta = updated_growth_rate / susceptible * inv_contact_rate  ## get_beta_beta_exp

    return beta


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
def get_growth_rate(doubling_time):
    """
    Calculate the expected growth rate of COVID-19 infections given a doubling time
    :param doubling_time: The time required for the amount of COVID-19 cases to double
    :return: growth_rate: Rate of spread of COVID-19 cases.
    """
    ## ggr_cond
    if doubling_time == 0:  ## ggr_cond_b0_cond
        growth_rate = 0  ## ggr_cond_b0_exp
    else:
        growth_rate = 2.0 ** (1.0 / doubling_time) - 1.0  ## ggr_cond_b1_exp

    return growth_rate


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
def sir(s, i, r, beta, gamma, n):
    """
    The SIR model, one time step
    :param s: Current amount of individuals that are susceptible
    :param i: Current amount of individuals that are infectious
    :param r: Current amount of individuals that are recovered
    :param beta: The rate of exposure of individuals to persons infected with COVID-19
    :param gamma: Rate of recovery for infected individuals
    :param n: Total population size
    :return:
    """
    s_n = (-beta * s * i) + s  # Update to the amount of individuals that are susceptible ## sir_s_n_exp
    i_n = (beta * s * i - gamma * i) + i  # Update to the amount of individuals that are infectious ## sir_i_n_exp
    r_n = gamma * i + r  # Update to the amount of individuals that are recovered ## sir_r_n_exp

    scale = n / (s_n + i_n + r_n)  # A scaling factor to compute updated disease variables ## sir_scale_exp

    s = s_n * scale  ## sir_s_exp
    i = i_n * scale  ## sir_i_exp
    r = r_n * scale  ## sir_r_exp
    return s, i, r


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
def sim_sir(s, i, r, gamma, i_day,  ### original inputs
            N_p, betas, days,  ### changes to original CHIME sim_sir to simplify policy bookkeeping
            d_a, s_a, i_a, r_a, e_a  ### changes to original CHIME sim_sir simulation bookkeeping - here, bookkeeping represented as lists that are passed in as arguments
            ):
    n = s + i + r  ## simsir_n_exp
    d = i_day  ## simsir_d_exp

    ### total_days from original CHIME sim_sir was used to determine the size of the
    ### the state bookkeeping across the simulation.
    ### Here, the array size is for this bookkeeping is determined outside of sim_sir
    ### and the arrays are passed in as arguments.

    index = 0  ## simsir_idx_exp
    for p_idx in range(N_p):  ## simsir_loop_1
        beta = betas[p_idx]  ## simsir_loop_1_beta_exp
        n_days = days[p_idx]  ## simsir_loop_1_N_d_exp
        for d_idx in range(n_days):  ## simsir_loop_1_1
            d_a[index] = d  ## simsir_loop_1_1_T_exp
            s_a[index] = s  ## simsir_loop_1_1_S_exp
            i_a[index] = i  ## simsir_loop_1_1_I_exp
            r_a[index] = r  ## simsir_loop_1_1_R_exp
            e_a[index] = i + r  # updated "ever" infected (= i + r)  ### In CHIME sir.py, this is performed at end as sum of two numpy arrays; here perform iteratively
            index += 1  ## simsir_loop_1_1_idx_exp

            s, i, r = sir(s, i, r, beta, gamma, n)  ## simsir_loop_1_1_call_sir_exp
            d += 1  ## simsir_loop_1_1_d_exp

    # Record the last update (since sir() is called at the tail of the inner loop above)
    d_a[index] = d  ## simsir_T_exp
    s_a[index] = s  ## simsir_S_exp
    i_a[index] = i  ## simsir_I_exp
    r_a[index] = r  ## simsir_R_exp
    e_a[index] = i + r  # updated "ever" infected (= i + r)  ### In CHIME sir.py, this is performed at end as sum of two numpy arrays; here perform iteratively

    return s, i, r, d_a, s_a, i_a, r_a, e_a  ### return


def main():
    """
    implements generic CHIME configuration without hospitalization calculation
    initializes parameters and population, calculates policy, and runs dynamics
    :return:
    """
    ###

    # initial parameters
    i_day = 17.0  ## main_i_day_exp
    n_days = 20  ## main_n_days_exp
    N_p = 3  ## main_N_p_exp
    N_t = 121  ## main_N_t_exp
    infections_days = 14.0  ## main_inf_days_exp
    relative_contact_rate = 0.05  ## main_rcr_exp
    gamma = 1.0 / infections_days  ## main_gamma_exp

    # initialize lists for policy and simulation state bookkeeping
    policys_betas = [0.0] * N_p  ## TODO size      # main_pbetas_seq
    policy_days = [0] * N_p  ## main_pdays_seq
    d_a = [0.0] * N_t  ## main_T_seq
    s_a = [0.0] * N_t  ## main_S_seq
    i_a = [0.0] * N_t  ## main_I_seq
    r_a = [0.0] * N_t  ## main_R_seq
    e_a = [0.0] * N_t  # "ever" infected (= I + R) ## main_E_seq

    # initial population
    s_n = 1000  ## main_s_n_exp
    i_n = 1  ## main_i_n_exp
    r_n = 1  ## main_r_n_exp

    # calculate beta under policy
    for p_idx in range(N_p):  ## main_loop_1
        doubling_time = (p_idx - 1.0) * 5.0  ## main_loop_1_dtime_exp

        growth_rate = get_growth_rate(doubling_time)  ## main_loop_1_gr_exp
        beta = get_beta(growth_rate, gamma, s_n,  ## main_loop_1_beta_exp
                        relative_contact_rate)
        policys_betas[p_idx] = beta  ## main_loop_1_pbetas_exp
        policy_days[p_idx] = n_days * p_idx  ## main_loop_1_pdays_exp

    # simulate dynamics (corresponding roughly to run_projection() )
    s_n, i_n, r_n, d_a, s_a, i_a, r_a, e_a \
        = sim_sir(s_n, i_n, r_n, gamma, i_day,  ## main_call_simsir_exp
                  N_p, policys_betas, policy_days,
                  d_a, s_a, i_a, r_a, e_a)

    print("s_n: " + str(s_n))
    print("i_n: " + str(i_n))
    print("r_n: " + str(r_n))
    print("E: " + str(e_a))

    return d_a, s_a, i_a, r_a, e_a  # return simulated dynamics


main()

