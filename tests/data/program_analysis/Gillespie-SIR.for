********************************************************************************
C     Input Variables:
C     S        Susceptible population
C     I        Infected population
C     R        Recovered population
C     gamma    Rate of recovery from an infection
C     rho      Basic reproduction Number
C
C     State Variables:
C     beta          Rate of infection
C     rateInfect    Current state dependent rate of infection
C     rateRecover   Current state dependent rate of recovery
C
C     Output Variables:
C     S        Susceptible population
C     I        Infected population
C     R        Recovered population
C     totalRates    Sum of total rates; taking advantage of Markovian identities
C                       to improve performance.
********************************************************************************
      subroutine SIR(S, I, R, gamma, rho,
     &                 totalRates)
      integer S, I, R

      double precision rateInfect, rateRecover, totalRates, gamma, rho
      double precision, parameter :: beta = rho * gamma !

      rateInfect = beta * S * I / (S + I + R)
      rateRecover = gamma * I
      totalRates = rateInfect + rateRecover

      ! Determine which event fired.  With probability rateInfect/totalRates
      ! the next event is infection.
      if (rand() < (rateInfect/totalRates)) then
          ! Delta for infection
          S = S - 1
          I = I + 1
      ! Determine the event fired.  With probability rateRecover/totalRates
      ! the next event is recovery.
      else
          ! Delta for recovery
          I = I - 1
          R = R + 1
      endif
      end subroutine SIR
