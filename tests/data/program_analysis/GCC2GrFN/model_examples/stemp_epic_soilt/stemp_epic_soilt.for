C=======================================================================
C  SOILT_EPIC, Subroutine
C  Determines soil temperature by layer
C-----------------------------------------------------------------------
C  Revision history
C  02/09/1933 PWW Header revision and minor changes.
C  12/09/1999 CHP Revisions for modular format.
C  01/01/2000 AJG Added surface temperature for the CENTURY-based
C                SOM/soil-N module.
C  01/14/2005 CHP Added METMP = 3: Corrected water content in temp. eqn.
!  12/07/2008 CHP Removed METMP -- use only corrected water content
!  09/16/2010 CHP / MSC modified for EPIC soil temperature method.
C-----------------------------------------------------------------------
C  Called : STEMP
C  Calls  : None
C=======================================================================

      SUBROUTINE SOILT_EPIC (
     &    B, BCV, CUMDPT, DP, DSMID, NLAYR, PESW, TAV,    !Input
     &    TAVG, TMAX, TMIN, WetDay, WFT, WW,              !Input
     &    TMA, SRFTEMP, ST, X2_AVG)                       !Output
     
    !     ------------------------------------------------------------------
        USE ModuleDefs
        IMPLICIT  NONE
        SAVE

        INTEGER  K, L, NLAYR, WetDay

        REAL B, CUMDPT, DD, DP, FX
        REAL PESW, SRFTEMP, TAV, TAVG, TMAX
        REAL WC, WW, ZD
        REAL TMA(5)
        REAL DSMID(NL) 
        REAL ST(NL)
        REAL X1, X2, X3, F, WFT, BCV, TMIN, X2_AVG, X2_PREV
        REAL LAG
        PARAMETER (LAG=0.5)

    !-----------------------------------------------------------------------
        WC = AMAX1(0.01, PESW) / (WW * CUMDPT) * 10.0
    !     frac =              cm   / (    mm     ) * mm/cm
        !WC (ratio)
        !PESW (cm)
        !WW (dimensionless)
        !CUMDPT (mm)

        FX = EXP(B * ((1.0 - WC) / (1.0 + WC))**2)
        DD = FX * DP                                  !DD in mm

    !=========================================================================
    !     Below this point - EPIC soil temperature routine differs from
    !       DSSAT original routine.
    !=========================================================================

        IF (WetDay > 0) THEN
    !       Potter & Williams, 1994, Eqn. 2
    !       X2=WFT(MO)*(TX-TMN)+TMN
        X2=WFT*(TAVG-TMIN)+TMIN
        ELSE
    !       Eqn 1
    !       X2=WFT(MO)*(TMX-TX)+TX+2.*((ST0/15.)**2-1.)
    !       Removed ST0 factor for now.
        X2=WFT*(TMAX-TAVG)+TAVG+2.
        ENDIF

        TMA(1) = X2
        DO K = 5, 2, -1
        TMA(K) = TMA(K-1)
        END DO
        X2_AVG = SUM(TMA) / 5.0     !Eqn 

    !     Eqn 4
    !     X3=(1.-BCV)*X2+BCV*T(LID(2))
        X3=(1.-BCV)*X2_AVG+BCV*X2_PREV

    !     DST0=AMIN1(X2,X3)
        SRFTEMP=AMIN1(X2_AVG,X3)

    !     Eqn 6 (partial)
    !     X1=AVT-X3
        X1=TAV-X3

        DO L = 1, NLAYR
        ZD    = DSMID(L) / DD  !Eqn 8
    !       Eqn 7
        F=ZD/(ZD+EXP(-.8669-2.0775*ZD))
    !       Eqn 6
    !       T(L)=PARM(15)*T(L)+XLG1*(F*X1+X3)
        ST(L)=LAG*ST(L)+(1.-LAG)*(F*X1+X3)
        END DO

        X2_PREV = X2_AVG

    !=========================================================================
    !     old CSM code:
    !=========================================================================
    !
    !      TA = TAV + TAMP * COS(ALX) / 2.0
    !      DT = ATOT / 5.0 - TA
    !
    !      DO L = 1, NLAYR
    !        ZD    = -DSMID(L) / DD
    !        ST(L) = TAV + (TAMP / 2.0 * COS(ALX + ZD) + DT) * EXP(ZD)
    !        ST(L) = NINT(ST(L) * 1000.) / 1000.   !debug vs release fix
    !      END DO
    !
    !-----------------------------------------------------------------------

        RETURN
        END SUBROUTINE SOILT_EPIC
C=======================================================================
