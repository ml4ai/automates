
      SUBROUTINE SOILT (
     &    ALBEDO, B, CUMDPT, DOY, DP, HDAY, NLAYR,    !Input
     &    PESW, SRAD, TAMP, TAV, TAVG, TMAX, WW, DSMID,!Input
     &    ATOT, TMA, SRFTEMP, ST)                     !Output
      
!     ------------------------------------------------------------------
      USE ModuleDefs     !Definitions of constructed variable types, 
                         ! which contain control information, soil
                         ! parameters, hourly weather data.
!     NL defined in ModuleDefs.for

      IMPLICIT  NONE
      SAVE

      INTEGER  K, L, DOY, NLAYR

      REAL ALBEDO, ALX, ATOT, B, CUMDPT, DD, DP, DT, FX
      REAL HDAY, PESW, SRAD, SRFTEMP, TA, TAMP, TAV, TAVG, TMAX
      REAL WC, WW, ZD
      REAL TMA(5)
      REAL DSMID(NL) 
      REAL ST(NL)

!-----------------------------------------------------------------------
      ALX    = (FLOAT(DOY) - HDAY) * 0.0174
      ATOT   = ATOT - TMA(5)

      DO K = 5, 2, -1
        TMA(K) = TMA(K-1)
      END DO

      TMA(1) = (1.0 - ALBEDO) * (TAVG + (TMAX - TAVG) * 
     &      SQRT(SRAD * 0.03)) + ALBEDO * TMA(1)

!     Prevents differences between release & debug modes:
!       Keep only 4 decimals. chp 06/03/03
      TMA(1) = NINT(TMA(1)*10000.)/10000.  !chp 
      ATOT = ATOT + TMA(1)

!-----------------------------------------------------------------------
!      !Water content function - compare old and new
!      SELECT CASE (METMP)
!      CASE ('O')  !Old, uncorrected equation
!        !OLD EQUATION (used in DSSAT v3.5 CROPGRO, SUBSTOR, CERES-Maize
!         WC = AMAX1(0.01, PESW) / (WW * CUMDPT * 10.0) 
!
!      CASE ('E')  !Corrected method (EPIC)
!        !NEW (CORRECTED) EQUATION
!        !chp 11/24/2003 per GH and LAH
        WC = AMAX1(0.01, PESW) / (WW * CUMDPT) * 10.0
!     frac =              cm   / (    mm     ) * mm/cm
        !WC (ratio)
        !PESW (cm)
        !WW (dimensionless)
        !CUMDPT (mm)
!      END SELECT
!-----------------------------------------------------------------------

      FX = EXP(B * ((1.0 - WC) / (1.0 + WC))**2)

      DD = FX * DP                                  !DD in mm
!     JWJ, GH 12/9/2008
!     Checked damping depths against values from literature and 
!       values are reasonable (after fix to WC equation).
!     Hillel, D. 2004. Introduction to Environmental Soil Physics.
!       Academic Press, San Diego, CA, USA.

      TA = TAV + TAMP * COS(ALX) / 2.0
      DT = ATOT / 5.0 - TA

      DO L = 1, NLAYR
        ZD    = -DSMID(L) / DD
        ST(L) = TAV + (TAMP / 2.0 * COS(ALX + ZD) + DT) * EXP(ZD)
        ST(L) = NINT(ST(L) * 1000.) / 1000.   !debug vs release fix
      END DO

!     Added: soil T for surface litter layer.
!     NB: this should be done by adding array element 0 to ST(L). Now
!     temporarily done differently.
      SRFTEMP = TAV + (TAMP / 2. * COS(ALX) + DT)
!     Note: ETPHOT calculates TSRF(3), which is surface temperature by 
!     canopy zone.  1=sunlit leaves.  2=shaded leaves.  3= soil.  Should
!     we combine these variables?  At this time, only SRFTEMP is used
!     elsewhere. - chp 11/27/01

!-----------------------------------------------------------------------
      RETURN
      END SUBROUTINE SOILT
C=======================================================================
