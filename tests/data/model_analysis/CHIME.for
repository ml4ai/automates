***************************************************************************

!                           CHIME model
! Simulates Susceptible, Infected, Recovered Population by taking into
! account SIR model parameters as long as hospitalization parameters and
! policy initiatives

****************************************************************************
!       Policy Module

!       State Variables:
!       beta       Rate  of transmission via contact
!       num_days   Number of  days over which a certain policy is active
****************************************************************************      
      module PolicyMod
        implicit none
        type Policy       
          real beta    
          integer num_days  
                            
        end type Policy
      end module PolicyMod

*****************************************************************************
!       Subroutine to calculate beta of SIR model from intrinsic growth rate,
!       gamma (1/infectious days), relative contact rate (social distancing
!       parameter)
!
!       Input Variables:
!       intrinsic_growth_rate     Rate at which rate of infection  is growing      
!       gamma                     Rate of recovery  from infection
!       susceptible               Size of Susceptible Population
!       relative_contact_rate     Contact rate between members of susceptible and infected groups
!       
!       Local Variables:
!       inv_contact_rate          Complement of relative_contact_rate
!       updated_growth_rate       modified growth rate
!
!       Output  Variable:
!       beta                      Rate  of transmission  via contact
*****************************************************************************
      subroutine get_beta(intrinsic_growth_rate, gamma,         
     &                    susceptible, relative_contact_rate,   
     &                    beta)                                 
        real intrinsic_growth_rate, susceptible
     &       relative_contact_rate, gamma
        real inv_contact_rate, updated_growth_rate
        real  beta

        inv_contact_rate = 1.0 - relative_contact_rate
        updated_growth_rate = intrinsic_growth_rate + gamma
        beta = updated_growth_rate / susceptible * inv_contact_rate

      end subroutine get_beta

*****************************************************************************
!       Subroutine to calculate intrinsic growth rate necessary for
!       calculating beta from doubling time (doubling_time) as the input
!       parameter
!
!       Input Variable:
!       doubling_time       Time taken for the  number of infected people to  double      
!     
!       Output Variable:
!       growth_rate         Intrinsic  growth rate      
****************************************************************************

      subroutine get_growth_rate(doubling_time,      
     &  growth_rate)                                 

        real doubling_time
        real growth_rate

        if (doubling_time .eq. 0.0) then
            growth_rate = 0.0
        else
          growth_rate = 2.0 ** (1.0 / doubling_time) - 1.0
        endif

      end subroutine get_growth_rate


*****************************************************************************
!       Subroutine to calculate susceptible (s), infected (i), and recovered (r)
!       group of people in one day. The populations are normaized based
!       on a scaling factor (scale) from beta, gamma parameters 
!
!       Input Variables:
!       beta        Rate of transmission via contact
!       gamma       Rate of recovery from infection
!       n           Total number of members (s+i+r)
!       s           Amount of susceptble members at previous timestep
!       i           Amount of infected members at previous timestep
!       r           Amount of recovered members at current timestep
!
!       State Variables:
!       s_n         Amount of susceptible members at current timestep
!       i_n         Amount of infected members at current timestep
!       r_n         Amount of recovered members at current timestep
!       scale       scaling factor
*****************************************************************************

      subroutine sir(beta, gamma, n,                       
     &                s, i, r)                             

        real  beta, gamma, n
        real s, i, r
        real s_n, i_n, r_n, scale

        ! Calculate current day's susceptible (s_n), infected (i_n),
        ! recovered (r_n) populations from  previous day's populations
        ! using SIR model
        s_n = (-beta * s * i) + s
        i_n = (beta * s * i - gamma * i) + i
        r_n = gamma * i + r

        ! Calculate scaling factor
        scale = n / (s_n + i_n + r_n)

        ! Scale s, i, r populations
        s = s_n * scale
        i = i_n * scale
        r = r_n * scale

      end subroutine sir

*****************************************************************************
!       Subroutine to simulate susceptible (s), infected (i), and recovered (r)
!       group of people over the total number of days spanning over all policies
!       
!       Input Variables:
!       s_n         Amount of susceptible members at current timestep
!       i_n         Amount of infected members at current timestep
!       r_n         Amount of recovered members at current timestep
!       gamma       Rate of recovery from infection
!       i_day       Index of day beyond which SIR  model is simulated  
!       N_p         Number  of policies
!       N_t         Total number of days over which  policies are active
!       policy      list of policies containing both beta and number of  days over
!                   which a particular  policy is active
!
!       Local Variables:
!       n           Total population
!       beta        Rate of  transmission via contact
!       N_d         Number  of days in each policy
!       d           Day Index
!       idx         Counter over arrays
!       p_idx       Counter over policies
!       d_idx       Counter over  N_d
!       
!       Output  Variables:
!       T           Array for storing indices of total number  of days
!       S           Array  for  storing amount of susceptible members on a  particular day
!                   over all sets  of policies
!       I           Array  for  storing amount of infected members on a  particular day
!                   over all sets  of policies
!       R           Array  for  storing amount of recovered members on a  particular day
!                   over all sets  of policies
!       E           Arrau for  storing amount of  members to have ever been infected on a
!                   particular day over all  policies
*****************************************************************************
      subroutine sim_sir(s_n, i_n, r_n, gamma, i_day, N_p,       
     &                    N_t, policies,                         
     &                    T, S, E,  I, R)                         
        use PolicyMod

        real s_n, i_n, r_n, gamma
        integer i_day,  N_p, N_t
        type (Policy) policies(N_p)
        real n, beta
        integer d, idx, p_idx, d_idx, N_d
        integer T(N_t+1)
        real S(N_t+1), E(N_t+1), I(N_t+1), R(N_t+1)

        n = s_n + i_n + r_n
        d = i_day

        idx = 1
        do p_idx = 1, N_p
          beta = policies(p_idx) % beta
          N_d = policies(p_idx) % num_days
          do d_idx = 1, N_d
            T(idx) = d
            S(idx) = s_n
            I(idx) = i_n
            R(idx) = r_n
            E(idx) = i_n + r_n
            idx = idx + 1
            call sir(beta, gamma, n, s_n, i_n, r_n)
            d = d + 1
          enddo
        enddo

        T(idx) = d
        S(idx) = s_n
        I(idx) = i_n
        R(idx) = r_n
        E(idx) = i_n + r_n

      end subroutine sim_sir


      program main
        use PolicyMod
        implicit none
        real s_n, i_n, r_n, beta, doubling_time, growth_rate
        integer p_idx
        integer, parameter :: i_day = 0, n_days = 20
        integer, parameter :: N_p = 2, infectious_days = 14
        real, parameter :: relative_contact_rate = 0.05
        real, parameter :: gamma = 1.0 / infectious_days
        type (Policy), dimension(1:N_p) :: policies
        integer N_t
        integer, dimension(:), allocatable :: T
        real, dimension(:), allocatable :: S, E, I, R

        s_n = 1000
        i_n = 0
        r_n = 0

        N_t = 0
        do p_idx = 1, N_p
          doubling_time = p_idx * 5.0
          call get_growth_rate(doubling_time, growth_rate)
          call get_beta(growth_rate, gamma, s_n,
     &                  relative_contact_rate, beta)
          policies(p_idx) % beta = beta
          policies(p_idx) % num_days = n_days * p_idx
          N_t = N_t + policies(p_idx) % num_days
        end do

        allocate(T(N_t+1)); allocate(S(N_t+1)); allocate(E(N_t+1));
        allocate(I(N_t+1)); allocate(R(N_t+1));

        call sim_sir(s_n, i_n, r_n, gamma, i_day, N_p, N_t, policies,
     &                  T, S, E, I, R)
      end program main
