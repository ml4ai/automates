def drive(start, end, step, parameters):
    step_results = {
        "SIR-simple::SIR-simple::sir::0::--::s::1": list(),
        "SIR-simple::SIR-simple::sir::0::--::i::1": list(),
        "SIR-simple::SIR-simple::sir::0::--::r::1": list(),
        "SIR-simple::SIR-simple::sir::0::--::dt::0": list(),
    }

    S = parameters["SIR-simple::SIR-simple::sir::0::--::s::0"]
    I = parameters["SIR-simple::SIR-simple::sir::0::--::i::0"]
    R = parameters["SIR-simple::SIR-simple::sir::0::--::r::0"]

    for i in range(start, end + 1, step):
        (S, I, R) = sir(
            S,
            I,
            R,
            parameters["SIR-simple::SIR-simple::sir::0::--::beta::0"],
            parameters["SIR-simple::SIR-simple::sir::0::--::gamma::0"],
            step,
        )

        step_results["SIR-simple::SIR-simple::sir::0::--::s::1"].append(S)
        step_results["SIR-simple::SIR-simple::sir::0::--::i::1"].append(I)
        step_results["SIR-simple::SIR-simple::sir::0::--::r::1"].append(R)
        step_results["SIR-simple::SIR-simple::sir::0::--::dt::0"].append(i)

    return step_results


"""
Derived from the following:

    ********************************************************************************
    !     Input Variables:
    !     S        Amount of susceptible members at the current timestep
    !     I        Amount of infected members at the current timestep
    !     R        Amount of recovered members at the current timestep
    !     beta     Rate of transmission via contact
    !     gamma    Rate of recovery from infection
    !     dt       Next inter-event time
    !
    !     State Variables:
    !     infected    Increase in infected at the current timestep
    !     recovered   Increase in recovered at the current timestep
    ********************************************************************************
        subroutine sir(S, I, R, beta, gamma, dt)
            implicit none
            double precision S, I, R, beta, gamma, dt
            double precision infected, recovered

            infected = ((beta*S*I) / (S + I + R)) * dt
            recovered = (gamma*I) * dt

            S = S - infected
            I = I + infected - recovered
            R = R + recovered
        end subroutine sir
"""


def sir(S: float, I: float, R: float, beta: float, gamma: float, dt: float):
    """
    !     Input Variables:
    !     S        Amount of susceptible members at the current timestep
    !     I        Amount of infected members at the current timestep
    !     R        Amount of recovered members at the current timestep
    !     beta     Rate of transmission via contact
    !     gamma    Rate of recovery from infection
    !     dt       Next inter-event time
    !
    !     State Variables:
    !     infected    Increase in infected at the current timestep
    !     recovered   Increase in recovered at the current timestep
    """

    infected = ((beta * S * I) / (S + I + R)) * dt
    recovered = (gamma * I) * dt

    S = S - infected
    I = I + infected - recovered
    R = R + recovered

    return (S, I, R)
