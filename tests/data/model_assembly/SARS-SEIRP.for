!===============================================================================
!     Fortranification of SEIRP disease model for two simultaneous disease outbreaks
!     Euler method simulation
!===============================================================================


!===============================================================================
!  SARS_SEIRP, Subroutine, P. Hein
!  Calculates growth rates for all disease states given the current state values
!-------------------------------------------------------------------------------
!     Input Variables:
!     S_t         Current count of individuals that are susceptible to either disease ($S(t)$)
!     Ea_t        Current count of individuals that are exposed to disease A ($E(t)$)
!     Ia_t        Current count of individuals that are infectious with disease A ($I(t)$)
!     Ra_t        Current count of individuals that have recovered from disease A ($R(t)$)
!     Ib_t        Current count of individuals that are infectious with disease B ($I_p(t)$)
!     Rb_t        Current count of individuals that have recovered from disease B ($R_p(t)$)
!     t_a         Rate of transmissibility amongst susceptibles for disease A ($r$)
!     t_b         Rate of transmissibility amongst susceptibles for disease B ($r_p$)
!     et_a        Rate of transmissibility amongst exposed individuals for disease A ($b$)
!     r_a         Rate of recovery from disease A ($a$)
!     r_b         Rate of recovery from disease B ($a_p$)
!
!     State Variables:
!     inc_exposed_a     rate of increase of individuals exposed to diesease A
!     inc_infectives_a  rate of increase of individuals infected with diesease A
!     inc_infectives_b  rate of increase of individuals infected with diesease B
!     inc_recovered_a   rate of increase of individuals recovered from diesease A
!     inc_recovered_b   rate of increase of individuals recovered from diesease A
!
!     Output Variables:
!     dSdt        Change in amount of individuals who are susceptible to either disease
!     dEadt       Change in amount of individuals who are exposed to disease A
!     dIadt       Change in amount of individuals who are infectious with disease A
!     dRadt       Change in amount of individuals who have recovered from disease A
!     dIbdt       Change in amount of individuals who are infectious with disease B
!     dRbdt       Change in amount of individuals who have recovered from disease B
!
!-------------------------------------------------------------------------------
!  Called by:   main
!  Calls:       None
!===============================================================================
      subroutine SARS_SEIRP(S_t, Ea_t, Ia_t, Ra_t, Ib_t, Rb_t,
     &                      t_a, t_b, et_a, r_a, r_b,
     &                      dSdt, dEadt, dIadt, dRadt, dIbdt, dRbdt)
        real S_t, Ea_t, Ia_t, Ra_t, Ib_t, Rb_t
        real t_a, t_b, et_a, r_a, r_b
        real inc_exposed_a, inc_infectives_a, inc_infectives_b
        real inc_recovered_a, inc_recovered_b
        real dSdt, dEadt, dIadt, dRadt, dIbdt, dRbdt

        inc_exposed_a = t_a * S_t * Ia_t
        inc_infectives_a = et_a * Ea_t
        inc_infectives_b = t_b * S_t * Ib_t
        inc_recovered_a = r_a * Ia_t
        inc_recovered_b = r_b * Ib_t

        dSdt = -inc_exposed_a - inc_infectives_b
        dEadt = inc_exposed_a - inc_infectives_a
        dIadt = inc_infectives_a - inc_recovered_a
        dRadt = inc_recovered_a
        dIbdt = inc_infectives_b - inc_recovered_b
        dRbdt = inc_recovered_b
      end subroutine SARS_SEIRP

!===============================================================================
! MAIN, program, by C. Morrison
! Simulates the Hong Kong case (b) extreme SARS outbreak using dynamics
! provided by Tuen Wai Ng et al.
! Euler method simulation
!-------------------------------------------------------------------------------
!     State Variables:
!     day     index into the discretized arrays of daily counts
!
!     Euler Method parameter:
!     delta_t     Update granularity
!-------------------------------------------------------------------------------
!  Called by:   None
!  Calls:       SARS_SEIRP
!===============================================================================
      program main
      	real S_t, Ea_t, Ia_t, Ra_t, Ib_t, Rb_t
        real dSdt, dEadt, dIadt, dRadt, dIbdt, dRbdt
        integer t, day

!       Assuming parameters and initial conditions from
!       SARS Hong Kong case (b) extreme outbreak
        real, parameter :: t_a = 10.08E-8, t_b = 7.94E-8
        real, parameter :: et_a = 0.105, r_a = 0.52, r_b = 0.12

!		Total days to predict
        integer, parameter :: Tmax = 1000
!   The precision of the Euler method estimation
        integer, parameter :: precision = 1

!		The Euler method update step size
        real, parameter :: delta_t = 1.0 / real(precision)

!		Total simulator steps to run
        integer, parameter :: Tmax_sim = Tmax * precision

!		Bookkeeping of the Euler method simulated states (real)
        real, dimension(0:Tmax_sim) :: S_sim, Ea_sim, Ia_sim
        real, dimension(0:Tmax_sim) :: Ra_sim, Ib_sim, Rb_sim

!		Bookkeeping of the predicted observables (each day) -- will be cast to integer
        integer, dimension(0:Tmax) :: S, Ea, Ia, Ra, Ib, Rb

!		Initial measured states
        S(0) = 6800000
        Ea(0) = 100
        Ia(0) = 50
        Ra(0) = 0
        Ib(0) = 10
        Rb(0) = 0

!		Initial real simulation states
        S_sim(0) = real(S(0))
        Ea_sim(0) = real(Ea(0))
        Ia_sim(0) = real(Ia(0))
        Ra_sim(0) = real(Ra(0))
        Ib_sim(0) = real(Ib(0))
        Rb_sim(0) = real(Rb(0))

!		Initialize day (observables) index
        day = 0

!		Euler method simulation update loop
        do t = 1, Tmax_sim, 1

!		  Get previous Euler method simulation state
          S_t = S_sim(t - 1)
          Ea_t = Ea_sim(t - 1)
          Ia_t = Ia_sim(t - 1)
          Ra_t = Ra_sim(t - 1)
          Ib_t = Ib_sim(t - 1)
          Rb_t = Rb_sim(t - 1)

!         Call SIR update
          call SARS_SEIRP(S_t, Ea_t, Ia_t, Ra_t, Ib_t, Rb_t,
     &                    t_a, t_b, et_a, r_a, r_b,
     &                    dSdt, dEadt, dIadt, dRadt, dIbdt, dRbdt)

!		  Euler method update
          S_sim(t) = S_t + ( dSdt * delta_t )
          Ea_sim(t) = Ea_t + ( dEadt * delta_t )
          Ia_sim(t) = Ia_t + ( dIadt * delta_t )
          Ra_sim(t) = Ra_t + ( dRadt * delta_t )
          Ib_sim(t) = Ib_t + ( dIbdt * delta_t )
          Rb_sim(t) = Rb_t + ( dRbdt * delta_t )

!		  Update state at day
          if ( mod(t, precision) .eq. 0 ) then
!			Advance the day index
          	day = day + 1

!			Record the day prediction (cast sim to integer)
            S(day) = nint(S_sim(t))
          	Ea(day) = nint(Ea_sim(t))
          	Ia(day) = nint(Ia_sim(t))
          	Ra(day) = nint(Ra_sim(t))
          	Ib(day) = nint(Ib_sim(t))
          	Rb(day) = nint(Rb_sim(t))

!			Make next simulator state be the integer value (cast to real)
          	S_sim(t) = real(S(day))
          	Ea_sim(t) = real(Ea(day))
          	Ia_sim(t) = real(Ia(day))
          	Ra_sim(t) = real(Ra(day))
          	Ib_sim(t) = real(Ib(day))
          	Rb_sim(t) = real(Rb(day))
          end if

        end do

!		Print the estimated (integer) values for the final day
        print*, S(Tmax - 1)
        print*, Ea(Tmax - 1)
        print*, Ia(Tmax - 1)
        print*, Ra(Tmax - 1)
        print*, Ib(Tmax - 1)
        print*, Rb(Tmax - 1)
      end program main
!===============================================================================
