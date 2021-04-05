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
  failingTest should s"find functions from t3e: ${t3e}" taggedAs(Somebody) in {
    val desired = Seq(
      "Wilting point Wp" -> Seq("soil depth", "soil texture information"), // multiple outputs: needs to be addressed in the next meeting!
      "field capacity Wc" -> Seq("soil depth", "soil texture information")
    )
    val mentions = extractMentions(t3e)
    testFunctionEvent(mentions, desired)
  }

  // Tests from 2003-DSSAT

  val t1f = "the soil water content of each layer is updated by adding or subtracting daily flows of water to or from the layer due to each process."
  failingTest should s"find functions from t1f: ${t1f}" taggedAs(Somebody) in {
    val desired = Seq(
      "the soil water content of each layer" -> Seq("daily flows of water", "the layer due to each process"), // note: same inputs, same output but different trigger word. (add and subtract, each) how can we capture such cases?
      "the soil water content of each layer" -> Seq("daily flows of water", "the layer due to each process")
    )
    val mentions = extractMentions(t1f)
    testFunctionEvent(mentions, desired)
  }

  val t2f = "Soil temperature is computed from air temperature and a deep soil temperature boundary condition that is calculated from the average annual air temperature and the amplitude of monthly mean temperatures."
  failingTest should s"find functions from t2f: ${t2f}" taggedAs(Somebody) in {
    val desired = Seq(
      "Soil temperature" -> Seq("air temperature", "deep soil temperature boundary condition"), // note: only one rule applies even when multiple rules should apply. needs to find out why.
      "deep soil temperature boundary condition" -> Seq("average annual air temperature", "amplitude of monthly mean temperatures")
    )
    val mentions = extractMentions(t2f)
    testFunctionEvent(mentions, desired)
  }

  val t3f = "This module brings together soil, plant and atmosphere inputs and computes light interception by the canopy, potential evapotranspiration (ET) as well as actual soil evaporation and plant transpiration"
  failingTest should s"find functions from t3f: ${t3f}" taggedAs(Somebody) in {
    val desired = Seq(
      "light interception" -> Seq("canopy", "potential evapotranspiration", "actual soil evaporation", "plant transpiration")
    )
    val mentions = extractMentions(t3f)
    testFunctionEvent(mentions, desired)
  }

  val t4f = "Actual soil evaporation is the minimum of the potential and soil-limiting calculations on a daily basis."
  failingTest should s"find functions from t4f: ${t4f}" taggedAs(Somebody) in {
    val desired = Seq(
      "Actual soil evaporation" -> Seq("potential and soil-limiting calculations on a daily basis") // note: would input be one chunk? or two with conjunction?
    )
    val mentions = extractMentions(t4f)
    testFunctionEvent(mentions, desired)
  }

  val t5f = "Photosynthesis of sunlit and shaded leaves is computed hourly using the asymptotic exponential response equation, " +
    "where quantum efficiency and light-saturated photosynthesis rate variables are dependent on CO2 and temperature"
  failingTest should s"find functions from t5f: ${t5f}" taggedAs(Somebody) in {
    val desired = Seq(
      "quantum efficiency" -> Seq("CO2", "temperature"), // fixme: for now, function extraction is done only once.
      "light-saturated photosynthesis rate variables" -> Seq("CO2", "temperature")
    )
    val mentions = extractMentions(t5f)
    testFunctionEvent(mentions, desired)
  }

  val t6f = "Hourly canopy photosynthesis on a land area basis is computed from the sum of sunlit and shaded leaf contributions " +
    "by multiplying sunlit and shaded leaf photosynthetic rates by their respective LAIs."
  failingTest should s"find functions from t6f: ${t6f}" taggedAs(Somebody) in {
    val desired = Seq(
      "Hourly canopy photosynthesis on a land area basis" -> Seq("sunlit and shaded leaf contributions"),
      "Hourly canopy photosynthesis on a land area basis" -> Seq("sunlit and shaded leaf photosynthetic rates", "their respective LAIs") // note: Photosynthesis is not captured as a concept here. What could be the reason for this?
    )
    val mentions = extractMentions(t6f)
    testFunctionEvent(mentions, desired)
  }

  val t7f = "Maintenance respiration depends on temperature as well as gross photosynthesis and total crop mass minus protein and oil in the seed."
  failingTest should s"find functions from t7f: ${t7f}" taggedAs(Somebody) in {
    val desired = Seq(
      "Maintenance respiration" -> Seq("temperature", "gross photosynthesis", "total crop mass minus protein", "oil in the seed")
    )
    val mentions = extractMentions(t7f)
    testFunctionEvent(mentions, desired)
  }

  val t8f = "Daily growth rate is modified by temperature and assimilate availability."
  failingTest should s"find functions from t8f: ${t8f}" taggedAs(Somebody) in {
    val desired = Seq(
      "Daily growth rate" -> Seq("temperature", "assimilate availability") //fixme: "assimilate availability" is not captured as an input (bad parsing)
    )
    val mentions = extractMentions(t8f)
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

  // Tests from 2003-DSSAT
  // todo: potential root water uptake is computed by calculating a maximum water flow to roots in each layer and summing these values
  // todo: It also computes the root water uptake of each soil layer. The daily weather values as well as all soil properties and current soil water content, by layer, are required as input. In addition, leaf area index (LAI) and root length density for each layer are needed.
  // todo: The potential ET is partitioned into potential soil evaporation based on the fraction of solar energy reaching the soil surface, based on a negative exponential function of LAI, and potential plant transpiration.
  // todo: This ratio is typically used in the Plant modules to reduce photosynthesis in proportion to relative decreases in transpiration.
  // todo: a ratio of potential root water uptake and potential transpiration is used to reduce plant turgor and expansive growth of crops
  // todo: The daily canopy photosynthesis option, modified from the method used in SOYGRO V5.4 (Jones et al., 1989), predicts daily gross photosynthesis as a function of daily irradiance for a full canopy, which is then multiplied by factors 0/1 for light interception, temperature, leaf nitrogen status, and water deficit.
  // todo: Daylength may affect the total number of leaves formed by altering the duration of the floral induction phase, and thus, floral initiation. //note: does this counts as a function example?
  // todo: The amount of new dry matter available for growth each day may also be modified by the most limiting of water or nitrogen stress, and temperature, and is sensitive to atmospheric CO2 concentration.
  // todo: An important aspect of many of these studies is a consideration that weather influences the performance of crops, interacting in complex ways with soil and management. # note: influence - function?
