C=======================================================================
C  OPSTEMP, Subroutine, C.H.Porter 
C  Generates output for daily soil temperature data
C-----------------------------------------------------------------------
C  REVISION HISTORY
C  11/01/2001 CHP Written
C  06/07/2002 GH  Modified for crop rotations
C-----------------------------------------------------------------------
C  Called from:   STEMP
C  Calls:         None
C=======================================================================
      SUBROUTINE OPSTEMP(CONTROL, ISWITCH, DOY, SRFTEMP, ST, TAV, TAMP)

!-----------------------------------------------------------------------
      USE ModuleDefs

      IMPLICIT NONE
      SAVE
!-----------------------------------------------------------------------
      CHARACTER*1  RNMODE
      CHARACTER*12 OUTT

      INTEGER DAS, DOY, DYNAMIC, ERRNUM, FROP, L, N_LYR
      INTEGER NOUTDT, RUN, YEAR, YRDOY, REPNO
      REAL ST(NL), SRFTEMP, TAV, TAMP

      LOGICAL FEXIST, DOPRINT

!-----------------------------------------------------------------------
!     The variable "CONTROL" is of constructed type "ControlType" as 
!     defined in ModuleDefs.for, and contains the following variables.
!     The components are copied into local variables for use here.
!-----------------------------------------------------------------------
      TYPE (ControlType) CONTROL
      TYPE (SwitchType)  ISWITCH
      TYPE (SoilType)    SOILPROP

      DAS     = CONTROL % DAS
      DYNAMIC = CONTROL % DYNAMIC
      FROP    = CONTROL % FROP
      YRDOY   = CONTROL % YRDOY
      
!***********************************************************************
!***********************************************************************
!     Seasonal initialization - run once per season
!***********************************************************************
!      ELSEIF (DYNAMIC .EQ. SEASINIT) THEN
      IF (DYNAMIC .EQ. SEASINIT) THEN
!-----------------------------------------------------------------------
!       Open the output files
        OUTT = 'SoilTemp.OUT'
        OPEN (UNIT=NOUTDT, FILE=OUTT, STATUS='NEW',
     &      IOSTAT = ERRNUM)
 !        Write headers info to daily output file
          WRITE(NOUTDT,'("*SOIL TEMPERATURE OUTPUT FILE (DAILY)")')
C-----------------------------------------------------------------------
C     Variable heading for SoilTemp.OUT
C-----------------------------------------------------------------------                  
!        CALL GET(SOILPROP)
        N_LYR = MIN(10, MAX(4,SOILPROP%NLAYR))
          
          IF (N_LYR < 10) THEN
            WRITE (NOUTDT,120) ("TS",L,"D",L=1,N_LYR)
  120       FORMAT('@YEAR DOY   DAS    TS0D',10("    ",A2,I1,A1))

          ELSE
            WRITE (NOUTDT,122) ("TS",L,"D",L=1,9), "    TS10"
  122       FORMAT('@YEAR DOY   DAS    TS0D',9("    ",A2,I1,A1),A8)
          ENDIF

      ENDIF !DYNAMIC

!***********************************************************************
!***********************************************************************
!     Output
!***********************************************************************
      IF (DYNAMIC .EQ. OUTPUT) THEN
        CALL YR_DOY(YRDOY, YEAR, DOY)
!         Generate output for file SoilTemp.OUT
          WRITE (NOUTDT,300) YEAR, DOY, DAS, SRFTEMP, (ST(L),L=1,N_LYR)
  300     FORMAT(1X,I4,1X,I3.3,1X,I5,11F8.1)
      ENDIF
!***********************************************************************
!***********************************************************************
!     SEASEND
!***********************************************************************
      IF (DYNAMIC .EQ. SEASEND) THEN
!-----------------------------------------------------------------------
        CLOSE (NOUTDT)
!***********************************************************************
!***********************************************************************
!     END OF DYNAMIC IF CONSTRUCT
!***********************************************************************
      ENDIF
!***********************************************************************
      RETURN
      END SUBROUTINE OPSTEMP
!***********************************************************************
