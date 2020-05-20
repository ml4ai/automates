C===========================================================================
C CHIME model
C Simulates Susceptible, Infected, Recovered Population by taking into
C account SIR model parameters as long as hospitalization parameters and
C policy initiatives
C===========================================================================
C Policy Module
      module PolicyMod
        implicit none
        type Policy   ! Derived Type : Mimics Tuple From  Python Code    
          real beta    ! Variable (SIR model parameter)
          integer num_days  ! Variable (Number of Days over which beta
                            ! is effective)
        end type Policy
      end module PolicyMod


C============================================================================
C Subroutine to calculate beta of SIR model from intrinsic growth rate,
C gamma (1/infectious days), relative contact rate (social distancing
C parameter)
C===========================================================================

      subroutine get_beta(intrinsic_growth_rate, gamma,         !Input
     &                    susceptible, relative_contact_rate,   !Input
     &                    beta)                                 !Output
!----------------------------------------------------------------------------
!       Input Variables:
        real intrinsic_growth_rate, susceptible
     &       relative_contact_rate, gamma
!----------------------------------------------------------------------------
!       Local Variables:
        real inv_contact_rate, updated_growth_rate
!----------------------------------------------------------------------------
!       Output Variable:
        real  beta
!----------------------------------------------------------------------------

        inv_contact_rate = 1.0 - relative_contact_rate
        updated_growth_rate = intrinsic_growth_rate + gamma
        beta = updated_growth_rate / susceptible * inv_contact_rate

      end subroutine get_beta

C============================================================================
C Subroutine to calculate intrinsic growth rate necessary for
C calculating beta from doubling time (doubling_time) as the input
C parameter
C===========================================================================

      subroutine get_growth_rate(doubling_time,      !Input
     &  growth_rate)                                 !Output
!----------------------------------------------------------------------------
!       Input Variables:
        real doubling_time
!----------------------------------------------------------------------------
!       Output Variable:
        real growth_rate
!----------------------------------------------------------------------------

        if (doubling_time .eq. 0.0) then
            growth_rate = 0.0
        else
          growth_rate = 2.0 ** (1.0 / doubling_time) - 1.0
        endif

      end subroutine get_growth_rate

C============================================================================
C Subroutine to calculate susceptible (s), infected (i), and recovered (r)
C group of people in one day. The populations are normaized based
C on a scaling factor (scale) from beta, gamma parameters 
C===========================================================================

      subroutine sir(beta, gamma, n,                       !Input
     &                s, i, r)                             !Output

!----------------------------------------------------------------------------
!       Input Variables:
        real  beta, gamma, n
!----------------------------------------------------------------------------
!       Local Variables:
        real s_n, i_n, r_n, scale
!----------------------------------------------------------------------------
!       Input and Output Variables:
        real s, i, r
!----------------------------------------------------------------------------

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


C============================================================================
C Subroutine to simulate susceptible (s), infected (i), and recovered (r)
C group of people over the total number of days included in policies.
C Number  of policies is given by N_p
C Total number of days is given  by N_t
C Number of days  over which a given beta is effective after which a
C different policy initiative is underaken is given by N_d
C policies is a derived type which contain N_p number of (beta, N_d)
C T is an array with a list of total days ranging from 1 to N_t
C S, I, R are arrays with their respective populations simulated over
C N_t days. E is the array which contains a list of people who have been infected
C (infected + recovered) at some point in time
C===========================================================================
      subroutine sim_sir(s_n, i_n, r_n, gamma, i_day, N_p,       !Input
     &                    N_t, policies,                         
     &                    T, S, E,  I, R)                        !Output 
        use PolicyMod
!----------------------------------------------------------------------------
!       Input Variables:
        real s_n, i_n, r_n, gamma
        integer i_day,  N_p, N_t
        type (Policy) policies(N_p)

!----------------------------------------------------------------------------
!       Local Variables:
        real n, beta
        integer d, idx, p_idx, d_idx, N_d

!----------------------------------------------------------------------------
!       Output Variables:
        integer T(N_t+1)
        real S(N_t+1), E(N_t+1), I(N_t+1), R(N_t+1)
!----------------------------------------------------------------------------

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
