package org.clulab.aske.automates.text

import org.clulab.aske.automates.TestUtils._

class TestFunctions extends ExtractionTest {

  // todo: how should we test functions that have multiple inputs, or just one input (more than or less than 2)?
  // Tests from paper: ASCE-2005-The ASCE Standardized Reference-TechReport-petasce

  val t1a = "Rnl, net long-wave radiation, is the difference between upward long-wave radiation from the standardized surface (Rlu) and downward long-wave radiation from the sky (Rld),"
  failingTest should s"find functions from t1a: ${t1a}" taggedAs(Somebody) in {
    val desired = Seq(
      "Rnl" -> Seq("difference between upward long-wave radiation from the standardized surface", "downward long-wave radiation from the sky")
    )
    val mentions = extractMentions(t1a)
    testFunctionEvent(mentions, desired)
  }

  val t2a = "Similar to equation 2, E0 is calculated as the product of Kcd and ETpm."
  passingTest should s"find functions from t2a: ${t2a}" taggedAs(Somebody) in {
    val desired = Seq(
      "E0" -> Seq("Kcd", "ETpm")
    )
    val mentions = extractMentions(t2a)
    testFunctionEvent(mentions, desired)
  }

  val t3a = "Daily Rso is a function of the time of year and latitude."
  failingTest should s"find functions from t3a: ${t3a}" taggedAs(Somebody) in {
    val desired = Seq(
      "Daily Rso" -> Seq("time of year", "latitude")
    )
    val mentions = extractMentions(t3a)
    testFunctionEvent(mentions, desired)
  }

  // Tests from paper: COVID_ACT_NOW
  val t1b = "Initial conditions for total cases and total exposed are calculated by dividing hospitalizations by the hospitalization rate."
  failingTest should s"find functions from t1b: ${t1b}" taggedAs(Somebody) in {
    val desired = Seq(
      "Initial conditions for total cases and total exposed" -> Seq("hospitalizations", "hospitalization rate")
    )
    val mentions = extractMentions(t1b)
    testFunctionEvent(mentions, desired)
  }

  // Tests from CHIME-online-manual
  // fixme: inverse_of rule contains only one input. how should we test such rules?
  val t1c = "γ is the inverse of the mean recovery time, in days."
  passingTest should s"find functions from t1c: ${t1c}" taggedAs(Somebody) in {
    val desired = Seq(
      "γ" -> Seq("mean recovery time")
    )
    val mentions = extractMentions(t1c)
    testFunctionEvent(mentions, desired)
  }

  // Tests from PT-2012-ET Measurement and Estimation Using Modified PT in Maise with Mulching-petpt_2012
  val t1d = "In this model, ET is a product of the equilibrium evaporation (ETeq) and PT coefficient (α), where ETeq can be obtained from meteorological data (net radiation, soil heat flux, and air temperature)."
  failingTest should s"find functions from t1d: ${t1d}" taggedAs(Somebody) in {
    val desired = Seq(
      "ET" -> Seq("equilibrium evaporation", "PT coefficient")
    )
    val mentions = extractMentions(t1d)
    testFunctionEvent(mentions, desired)
  }

  val t2d = "where αb was a function of LAI and soil evaporation loss."
  passingTest should s"find functions from t2d: ${t2d}" taggedAs(Somebody) in {
    val desired = Seq(
      "αb" -> Seq("LAI", "soil evaporation loss")
    )
    val mentions = extractMentions(t2d)
    testFunctionEvent(mentions, desired)
  }

  // Tests from Global estimation of evapotranspiration using a leaf area index-based surface energy and water balance model
  val t1e = "calculating total E (E0) as the sum of the canopy transpiration and soil evaporation, assuming the absence of soil water stress"
  passingTest should s"find functions from t1e: ${t1e}" taggedAs(Somebody) in {
    val desired = Seq(
      "total E" -> Seq("canopy transpiration", "soil evaporation")
    )
    val mentions = extractMentions(t1e)
    testFunctionEvent(mentions, desired)
  }

  val t2e = "Since air Rh, defined as ea divided by es, is also capable of representing the humidity deficit of air, there are arguments about the choice between Rh and D in E or stomatal conductance estimation."
  passingTest should s"find functions from t2e: ${t2e}" taggedAs(Somebody) in {
    val desired = Seq(
      "air Rh" -> Seq("ea", "es")
    )
    val mentions = extractMentions(t2e)
    testFunctionEvent(mentions, desired)
  }

  val t3e = "Wilting point Wp and field capacity Wc were calculated from soil depth and soil texture information, i.e., the relative proportion of sand, silt and clay, according to a set of prediction equations developed by Saxton et al. (1986)."
  passingTest should s"find functions from t3e: ${t3e}" taggedAs(Somebody) in {
    val desired = Seq(
      "Wilting point Wp and field capacity Wc" -> Seq("soil depth", "soil texture information")
    )
    val mentions = extractMentions(t3e)
    testFunctionEvent(mentions, desired)
  }

}


  // Tests from paper: ASCE-2005-The ASCE Standardized Reference-TechReport-petasce
  // todo: "The values for Cn consider the time step and aerodynamic roughness of the surface (i.e., reference type)."
  // todo: "The constant in the denominator, Cd, considers the time step, bulk surface resistance, and aerodynamic roughness of the surface (the latter two terms vary with reference type, time step and daytime/nighttime)."
  // todo: "The density of water (ρw) is taken as 1.0 Mg m-3 so that the inverse ratio of λ ρw times energy flux in MJ m-2 d-1 equals 1.0 mm d-1."
  // todo: "The actual vapor pressure can be measured or it can be calculated from various humidity data, such as measured dew point temperature, wet-bulb and dry-bulb temperature, or relative humidity and air temperature data."
  // todo: "For daily calculation time steps, average dew point temperature can be computed by averaging over hourly periods"
  // todo: "Extraterrestrial radiation, Ra, defined as the short-wave solar radiation in the absence of an atmosphere, is a well-behaved function of the day of the year, time of day, and latitude."
  // todo: "For daily (24-hour) periods, Ra can be estimated from the solar constant, the solar declination, and the day of the year"
  // todo: "The value for Rso is a function of the time of year and latitude, and, in addition, the time of day for hourly calculation periods."
  // todo: "Extraterrestrial radiation, Ra, defined as the short-wave solar radiation in the absence of an atmosphere, is a well-behaved function of the day of the year, time of day, latitude, and longitude."

  // Tests from COVID_ACT_NOW
  // todo: "Cases estimated by multiplying confirmed cases by 20."

  // Tests from CHIME-online-manual
  // todo: "which is the transmissibility τ multiplied by the average number of people exposed c."
  
  // Tests from 2003-A-double-epidemic-model for the SARS_propagation
  // todo: "The rate of removal of the people in class E to the infective class I is proportional to the number of people in class E, that is bE(t), where b is a positive number."
  // todo: "The incubation period (the time from first infection to the appearances of symptoms) plus the onset to admission interval is equal to the sum of the latent period and the infectious period and is therefore equal to 1/b + 1/a."

  // Tests from PT-2012-ET Measurement and Estimation Using Modified PT in Maise with Mulching-petpt_2012
  // todo: "De Bruin (1983) developed the PT coefficient model as a function of surface resistance."
  // todo: "The different growing stages were divided by our local visual observations of maize development characteristics and phenology, combined with changes of maize height and leaf area (Allen et al., 1998; Xu et al., 2002)."

  // Tests from Global estimation of evapotranspiration using a leaf area index-based surface energy and water balance model
  // todo: "introducing a simple biophysical model for canopy conductance (Gc), defined as a constant maximumstomatal conductance gsmax of 12.2mm s−1 multiplied by air relative humidity (Rh) and Lai (Gc=gs max×Rh×Lai)"
  // todo: "The surface energy balance partitions the available energy (Rn−G) between turbulent heat fluxes (λE and H):"
  // todo: "The ARTS E model requires inputs of Lai, net radiation, Rh, air temperature, wind speed, canopy height, precipitation, and maximum soil available water content (Mawc) as model parameters."
  // todo: "The SWB model requires as inputs precipitation, E0, air temperature, and Mawc. Its outputs are Ea, soil water content, and runoff."
