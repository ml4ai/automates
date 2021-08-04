      PROGRAM ASKEE

      USE ModuleDefs

      IMPLICIT NONE
C-----------------------------------------------------------------------
      CHARACTER*1   ANS,RNMODE,BLANK,UPCASE,ISWWAT
      CHARACTER*6   ERRKEY,FINDCH,TRNARG
      CHARACTER*30  FILEIO
      
      REAL ABD, ALBEDO, ATOT, B, CUMDPT 
      REAL DP, FX, HDAY, ICWD, PESW, MSALB, SRAD, SRFTEMP 
      REAL TAMP, TAV, TAVG, TBD, TMAX, XLAT, WW
      REAL TDL, TLL, TSW
      REAL TMA(5)
      REAL, DIMENSION(NL) :: BD, DLAYR, DLI, DS, DSI, DSMID, DUL, LL, 
     &      ST, SW, SWI

      PARAMETER (ERRKEY = 'ASKEE ')      
      PARAMETER (BLANK  = ' ')

C     Define constructed variable types based on definitions in
C     ModuleDefs.for.

C     The variable "CONTROL" is of type "ControlType".
      TYPE (ControlType) CONTROL

C     The variable "ISWITCH" is of type "SwitchType".
      TYPE (SwitchType) ISWITCH
      
      TYPE (SoilType) SOILPROP

!C-----------------------------------------------------------------------

      FILEIO = 'DSSAT47.INP'

C*********************************************************************** 
C*********************************************************************** 
C     RUN INITIALIZATION
C***********************************************************************

      CONTROL % FILEIO  = FILEIO
      CONTROL % RNMODE  = RNMODE
      CONTROL % ERRCODE = 0
      CONTROL % DYNAMIC = 2
      
      ISWITCH % ISWWAT = 'N'
      
      SOILPROP % BD    = 0.0
      SOILPROP % DLAYR = 0.0
      SOILPROP % DS    = 0.0 
      SOILPROP % DUL   = 0.0 
      SOILPROP % LL    = 0.0 
      SOILPROP % NLAYR = 0.0 
      SOILPROP % MSALB = 0.0
      
      
      SRAD    = 0.0 
      SW      = 0.0
      TAVG    = 0.0
      TMAX    = 0.0
      XLAT    = 0.0
      TAV     = 0.0
      TAMP    = 0.0
      SRFTEMP = 0.0
      ST      = 0.0

C*********************************************************************** 
C*********************************************************************** 
C     CALL SOIL TEMPERATURE SUBROUTINE
C***********************************************************************
      DO WHILE (CONTROL % DYNAMIC .LT. SEASEND)
        
          CALL STEMP(CONTROL, ISWITCH,  
     &      SOILPROP, SRAD, SW, TAVG, TMAX, XLAT, TAV, TAMP,!Input
     &      SRFTEMP, ST)                                    !Output
      
      ENDDO


      END PROGRAM ASKEE

!===========================================================================
! Variable listing
! ---------------------------------
! BLANK   Blank character 
! CONTROL Composite variable containing variables related to control and/or 
!           timing of simulation.  The structure of the variable 
!           (ControlType) is defined in ModuleDefs.for. 
!===========================================================================
