package org.clulab.aske.automates.text

import org.clulab.aske.automates.TestUtils._

class TestFunctions extends ExtractionTest {

  // Tests from paper: ASCE-2005-The ASCE Standardized Reference-TechReport-petasce

  val t1a = "Rnl, net long-wave radiation, is the difference between upward long-wave radiation from the standardized surface (Rlu) and downward long-wave radiation from the sky (Rld),"
  failingTest should s"find functions from t1a: ${t1a}" taggedAs(Somebody) in {
    val desired = Seq(
      "Rnl" -> Seq("upward long-wave radiation from the standardized surface", "downward long-wave radiation from the sky")
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

  val t4a = "The actual vapor pressure can be measured or it can be calculated from various humidity data, such as measured dew point temperature, wet-bulb and dry-bulb temperature, or relative humidity and air temperature data."
  failingTest should s"find functions from t4a: ${t4a}" taggedAs(Somebody) in {
    val desired = Seq(
      "The actual vapor pressure" -> Seq("various humidity data") // todo: how can we deal with pronouns (i.e. it)? + another issue is the "such as" part. (needs discourse parsing?)
    )
    val mentions = extractMentions(t4a)
    testFunctionEvent(mentions, desired)
  }

  val t5a = "Extraterrestrial radiation, Ra, defined as the short-wave solar radiation in the absence of an atmosphere, is a well-behaved function of the day of the year, time of day, and latitude."
  failingTest should s"find functions from t5a: ${t5a}" taggedAs(Somebody) in {
    val desired = Seq(
      "Extraterrestrial radiation" -> Seq("day of the year", "time of day", "latitude") // todo: trigger should not expand + output part is expanded too broadly.
    )
    val mentions = extractMentions(t5a)
    testFunctionEvent(mentions, desired)
  }

  val t6a = "For daily (24-hour) periods, Ra can be estimated from the solar constant, the solar declination, and the day of the year."
  failingTest should s"find functions from t6a: ${t6a}" taggedAs(Somebody) in {
    val desired = Seq(
      "Ra" -> Seq("solar constant", "solar declination", "day of the year") // fixme: output is not captured correctly. + overlap in inputs is not solved.
    )
    val mentions = extractMentions(t6a)
    testFunctionEvent(mentions, desired)
  }

  val t7a = "The value for Rso is a function of the time of year and latitude, and, in addition, the time of day for hourly calculation periods."
  failingTest should s"find functions from t7a: ${t7a}" taggedAs(Somebody) in {
    val desired = Seq(
      "value for Rso" -> Seq("time of year", "latitude", "time of day for hourly calculation periods") // fixme: the last input is not captured. ("and, in addition" part is blocking it from extracted.) -> fixed
    )
    val mentions = extractMentions(t7a)
    testFunctionEvent(mentions, desired)
  }

  // Tests from paper: COVID_ACT_NOW
  val t1b = "Initial conditions for total cases and total exposed are calculated by dividing hospitalizations by the hospitalization rate."
  passingTest should s"find functions from t1b: ${t1b}" taggedAs(Somebody) in {
    val desired = Seq(
      "Initial conditions for total cases and total exposed" -> Seq("hospitalizations", "hospitalization rate")
    )
    val mentions = extractMentions(t1b)
    testFunctionEvent(mentions, desired)
  }

  val t2b = "Cases estimated by multiplying confirmed cases by 20."
  failingTest should s"find functions from t2b: ${t2b}" taggedAs(Somebody) in {
    val desired = Seq(
      "Cases" -> Seq("confirmed cases", "20")
    )
    val mentions = extractMentions(t2b)
    testFunctionEvent(mentions, desired)
  }

  // Tests from CHIME-online-manual
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
  passingTest should s"find functions from t1d: ${t1d}" taggedAs(Somebody) in {
    val desired = Seq(
      "ET" -> Seq("equilibrium evaporation", "PT coefficient"),
//      "ETeq" -> Seq("meteorological data") # note: the rule "obtained_with" was disabled because it was producing too many false positives, and thus this part is disabled too.
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

  val t3d = "Leaf area was calculated by summing rectangular area of each leaf (product of leaf length and maximum width) multiplied by a factor of 0.74, which was obtained by analyzing the ratio of rectangular area to real area, measured by an AM300 (ADC BioScientific Ltd., UK)."
  failingTest should s"find functions from t3d: ${t3d}" taggedAs(Somebody) in {
    val desired = Seq(
      "Leaf area" -> Seq("rectangular area of each leaf (product of leaf length and maximum width) multiplied by a factor of 0.74"), // NOTE: how can be extract the whole phrase?? (parentheses))
      "rectangular area of each leaf" -> Seq("leaf length", "maximum width"),
      "a factor of 0.74" -> Seq("ratio of rectangular area to real area")
    )
    val mentions = extractMentions(t3d)
    testFunctionEvent(mentions, desired)
  }

  val t4d = "where τ is the fraction of net radiation transmission reached soil surface;"
  failingTest should s"find functions from t4d: ${t4d}" taggedAs(Somebody) in {
    val desired = Seq(
      "τ" -> Seq("net radiation transmission reached soil surface")
    )
    val mentions = extractMentions(t4d)
    testFunctionEvent(mentions, desired)
  }

  val t5d = "κ, canopy extinction coefficient of radiation, is dependent on foliage orientation and solar zenith angle, 0.45 for this study (Campbell and Norman, 1998)."
  passingTest should s"find functions from t5d: ${t5d}" taggedAs(Somebody) in {
    val desired = Seq(
      "κ" -> Seq("foliage orientation", "solar zenith angle") // note: 0.45 is wrongly captured as one of the inputs here due to bad parsing.
    )
    val mentions = extractMentions(t5d)
    testFunctionEvent(mentions, desired)
  }

  val t6d = "fs is fraction of leaf senescence, defined as the difference between unit and the ratio of chlorophyll content at the maturity stage (Cc,m) to that at the filling stage (Cc,f), i.e. (1.0 - Cc,m//Cc,f)."
  failingTest should s"find functions from t6d: ${t6d}" taggedAs(Somebody) in {
    val desired = Seq(
      "fs" -> Seq("leaf senescence"),
      "fs" -> Seq("unit and the ratio of chlorophyll content at the maturity stage (Cc,m) to that at the filling stage (Cc,f)") // note: expansion stops when there's a parentheses, how could that be fixed?
    )
    val mentions = extractMentions(t6d)
    testFunctionEvent(mentions, desired)
  }

  val t7d = "Although the difference of total ET between two years was about 10%, the difference of total ET per LAI was less than 3%, suggesting that inter-annual difference of ET was primarily related to LAI."
  failingTest should s"find functions from t7d: ${t7d}" taggedAs(Somebody) in {
    val desired = Seq(
      "about 10%" -> Seq("total ET"), // note: should it be just total ET, or total ET between two years?
      "less than 3%"-> Seq("total ET per LAI"), // fixme: simple-np rule is not working properly here
      "inter-annual difference of ET"-> Seq("LAI")
    )
    val mentions = extractMentions(t7d)
    testFunctionEvent(mentions, desired)
  }

  // Tests from Global estimation of evapotranspiration using a leaf area index-based surface energy and water balance model
  val t1e = "calculating total E (E0) as the sum of the canopy transpiration and soil evaporation, assuming the absence of soil water stress"
  failingTest should s"find functions from t1e: ${t1e}" taggedAs(Somebody) in {
    val desired = Seq(
      "total E" -> Seq("canopy transpiration", "soil evaporation") // this test failed after allowing inputs/outputs to have VBG tag ("calculating" captured as output)
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
      "Wilting point Wp" -> Seq("soil depth", "soil texture information"), // multiple outputs: needs to be addressed in the next meeting!
      "field capacity Wc" -> Seq("soil depth", "soil texture information")
    )
    val mentions = extractMentions(t3e)
    testFunctionEvent(mentions, desired)
  }

  // Tests from 2003-DSSAT

  val t1f = "the soil water content of each layer is updated by adding or subtracting daily flows of water to or from the layer due to each process."
  passingTest should s"find functions from t1f: ${t1f}" taggedAs(Somebody) in {
    val desired = Seq(
      "soil water content of each layer" -> Seq("daily flows of water", "layer"),
      "soil water content of each layer" -> Seq("daily flows of water", "layer")
    )
    val mentions = extractMentions(t1f)
    testFunctionEvent(mentions, desired)
    val functionMentions = mentions.filter(_.label == "Function")
    functionMentions.head.text shouldEqual functionMentions.last.text
  }

  val t2f = "Soil temperature is computed from air temperature and a deep soil temperature boundary condition that is calculated from the average annual air temperature and the amplitude of monthly mean temperatures."
  passingTest should s"find functions from t2f: ${t2f}" taggedAs(Somebody) in {
    val desired = Seq(
      "Soil temperature" -> Seq("air temperature", "deep soil temperature boundary condition"),
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
  passingTest should s"find functions from t4f: ${t4f}" taggedAs(Somebody) in {
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
      "Hourly canopy photosynthesis on a land area basis" -> Seq("sunlit leaf contribution", "shaded leaf contribution"),
      "Hourly canopy photosynthesis on a land area basis" -> Seq("sunlit and shaded leaf photosynthetic rates", "their respective LAIs")
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

  // model for predicting evaporation from a row crop with incomplete cover
  val t1g = "The crop evaporation rate is calculated by adding the soil surface and plant surface components (each of these requiring daily numbers for the leaf area index), the potential evaporation, the rainfall, and the net radiation above the canopy."
  failingTest should s"find functions from t1g: ${t1g}" taggedAs(Somebody) in {
    val desired = Seq(
      "crop evaporation rate" -> Seq("soil surface components", "plant surface components", "the potential evaporation", "the rainfall", "the net radiation above the canopy") // fixme: This example has a conjunction issue.
    )
    val mentions = extractMentions(t1g)
    testFunctionEvent(mentions, desired)
  }

  val t2g = "The evaporation from the soil surface Es is calculated in two stages: (1) the constant rate stage in which Es is limited only by the supply of energy to the surface and (2) the falling rate stage in which water movement to the evaporating sites near the surface is controlled by the hydraulic properties of the soil."
  passingTest should s"find functions from t2g: ${t2g}" taggedAs(Somebody) in {
    val desired = Seq(
      "Es" -> Seq("supply of energy to the surface"), // fixme: one additional, unwanted concept is captured as an input due to bad parsing.
      "water movement to the evaporating sites near the surface" -> Seq("hydraulic properties of the soil")
    )
    val mentions = extractMentions(t2g)
    testFunctionEvent(mentions, desired)
  }

  val t3g = "The model was used to obtain the total evaporation rate E = Es + Ep of a developing grain sorghum (Sorghum bicolor L.) canopy in central Texas."
  failingTest should s"find functions from t3g: ${t3g}" taggedAs(Somebody) in {
    val desired = Seq(
      "E" -> Seq("Es", "Ep") // fixme: "Es" is expanded too broadly due to bad parsing
    )
    val mentions = extractMentions(t3g)
    testFunctionEvent(mentions, desired)
  }

  val t4g = "Albedo values ε used for converting daily solar radiation Rs to net solar radiation are calculated for a developing canopy on the basis of the leaf area index Laε from an empirical equation developed from local data,"
  failingTest should s"find functions from t4g: ${t4g}" taggedAs(Somebody) in {
    val desired = Seq(
      "net solar radiation" -> Seq("ε", "Rs"), // fixme: inputs are not filtered properly
      "ε" -> Seq("Laε")
    )
    val mentions = extractMentions(t4g)
    testFunctionEvent(mentions, desired)
  }

  val t5g = "Wind speed, Rno, and the vapor pressure deficit are all lowered in approximate proportion to the canopy density."
  passingTest should s"find functions from t5g: ${t5g}" taggedAs(Somebody) in {
    val desired = Seq(
      "Wind speed" -> Seq("canopy density"), // fixme: same rule does not extract more than one set of input/output. -> fixed
      "Rno" -> Seq("canopy density"),
      "vapor pressure deficit" -> Seq("canopy density")
    )
    val mentions = extractMentions(t5g)
    testFunctionEvent(mentions, desired)
  }

  val t6g = "The evaporation rate in this special case Esx is first approximated as equal to 0.8P."
  failingTest should s"find functions from t6g: ${t6g}" taggedAs(Somebody) in {
    val desired = Seq(
      "Esx" -> Seq("0.8", "P") // fixme: a description part ("evaporation rate") is captured as an output, instead of the variable ("Esx"). Also, the numeral value ("0.8") and the variable ("P") is not captured separately.
    )
    val mentions = extractMentions(t6g)
    testFunctionEvent(mentions, desired)
  }

  val t7g = "The model was used to compute daily Es, Ep, and total E."
  failingTest should s"find NO functions from t7g: ${t7g}" taggedAs(Somebody) in {
    val desired = Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t7g) // fixme: models and equations should not be captured as an input (make a list to avoid?)
    testFunctionEvent(mentions, desired)
  }

  val t8g = "For example, consider a case in which the average air temperature is 32°C, Lai = 2.7, Rn0 = 5.0, E0 = 5.0, and ΣEs1 < U."
  passingTest should s"find NO functions from t8g: ${t8g}" taggedAs(Somebody) in {
    val desired = Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t8g) // fixme: when the right side of an equal sign is only a numerical value, the equation should not be captured as a function, but as a parameter setting.
    testFunctionEvent(mentions, desired)
  }

  // Tests from paper: 1982-Comparison-of-PT and Penman Methods-petpt and petpen_PM_and_PT

  val t1h = "In both cases Et was derived indirectly from calculated values of open water evaporation(Eo), using the equation: Et = f Eo where f was an empirical factor."
  failingTest should s"find functions from t1h: ${t1h}" taggedAs(Somebody) in {
    val desired = Seq(
      "Et" -> Seq("calculated values of open water evaporation(Eo)"),
      "Et" -> Seq("f", "Eo")
    )
    val mentions = extractMentions(t1h)
    testFunctionEvent(mentions, desired)
  }

  // Tests from 1985-description and performance of CERES-Wheat_A_user-oriented wheat yield model

  val t1i = "The primary variable influencing development rate is temperature."
  failingTest should s"find functions from t1i: ${t1i}" taggedAs(Somebody) in {
    val desired = Seq(
      "development rate" -> Seq("temperature") //note: overlap between trigger and output??
    )
    val mentions = extractMentions(t1i)
    testFunctionEvent(mentions, desired)
  }

  // Tests from paper: PT-1972-On the Assessment of Surface Heat Flux and Evaporation using Large-Scale Parameters-petpt

  val t1j = "The rate of conduction of heat near the interface between two media is governed by the quantity pc√K pertaining to each medium."
  failingTest should s"find functions from t1j: ${t1j}" taggedAs(Somebody) in {
    val desired = Seq(
      "The rate of conduction of heat near the interface between two media" -> Seq("quantity pc√K pertaining to each medium") //todo: identifier within Phrase should be filtered out
    )
    val mentions = extractMentions(t1j)
    testFunctionEvent(mentions, desired)
  }

  val t2j = "However, when the thermal balance between the two media is disturbed, as by advection, the heat subsequently passing from one to the other over any not-too-short time is governed by and proportional to the conductive capacity of the lower ranking medium."
  failingTest should s"find functions from t2j: ${t2j}" taggedAs(Somebody) in {
    val desired = Seq(
      "heat subsequently passing from one to the other over any not-too-short time" -> Seq("conductive capacity of the lower ranking medium"), //todo: tuning expansion handler needed?
      "heat subsequently passing from one to the other over any not-too-short time" -> Seq("conductive capacity of the lower ranking medium")
    )
    val mentions = extractMentions(t2j)
    testFunctionEvent(mentions, desired)
    val functionMentions = mentions.filter(_.label == "Function")
    functionMentions.head.text shouldEqual functionMentions.last.text
  }

  val t3j = "T0 is itself strongly governed by R and ground dryness."
  passingTest should s"find functions from t3j: ${t3j}" taggedAs(Somebody) in {
    val desired = Seq(
      "T0" -> Seq("R", "ground dryness")
    )
    val mentions = extractMentions(t3j)
    testFunctionEvent(mentions, desired)
  }

  val t4j = "C and C* are heat transfer coefficients that depend on the reference height selected for T and u, and, if this height is not low enough, on the stability."
  passingTest should s"find functions from t4j: ${t4j}" taggedAs(Somebody) in {
    val desired = Seq(
      "heat transfer coefficients" -> Seq("reference height selected for T and u", "stability") //todo: context is required as a key here. test needs to be revised?
    )
    val mentions = extractMentions(t4j)
    testFunctionEvent(mentions, desired)
  }
  // Tests from 2017-IMPLEMENTING STANDARDIZED REFERENCE EVAPOTRANSPIRATION AND DUAL CROP COEFFICIENT APPROACH IN THE DSSAT CROPPING SYSTEM MODEL
  val t1k = "While it is true that the DSSAT-CSM crop coefficient Kcs is multiplied by a reference ET, the resulting value (E0) denotes ET potential, therefore demand, and not necessarily actual ET."
  failingTest should s"find functions from t1k: ${t1k}" taggedAs(Somebody) in {
    val desired = Seq(
      "E0" -> Seq("Kcs", "reference ET") // fixme: why is "DSSAT-CSM crop coefficient Kcs" captured as identifier?
    )
    val mentions = extractMentions(t1k)
    testFunctionEvent(mentions, desired)
  }

  // Tests from APSIM_Cropping Systems
  val t1l = "empirical soil parameters are influenced by the number and thickness of specified layers"
  failingTest should s"find functions from t1l: ${t1l}" taggedAs(Somebody) in {
    val desired = Seq(
      "empirical soil parameters" -> Seq("number of specified layers", "thickness of specified layers")
    )
    val mentions = extractMentions(t1l)
    testFunctionEvent(mentions, desired)
  }

}

  // note: below are the example sentences that contain functional relations (I think), but I'm not sure what to do about with them for now.
  // todo: where KEP (typically ranging from 0.5 to 0.8) is defined as an energy extinction coefficient of the canopy for total solar irradiance, used for partitioning E0 to EPo and ESo (Ritchie, 1998).
  // Tests from paper: ASCE-2005-The ASCE Standardized Reference-TechReport-petasce
  // todo: "The values for Cn consider the time step and aerodynamic roughness of the surface (i.e., reference type)."
  // todo: "The constant in the denominator, Cd, considers the time step, bulk surface resistance, and aerodynamic roughness of the surface (the latter two terms vary with reference type, time step and daytime/nighttime)."
  // todo: "The density of water (ρw) is taken as 1.0 Mg m-3 so that the inverse ratio of λ ρw times energy flux in MJ m-2 d-1 equals 1.0 mm d-1."
  // todo: "For daily calculation time steps, average dew point temperature can be computed by averaging over hourly periods"

  // Tests from CHIME-online-manual
  // todo: "β can be interpreted as the effective contact rate: β=τ×c which is the transmissibility τ multiplied by the average number of people exposed c."
  
  // Tests from 2003-A-double-epidemic-model for the SARS_propagation
  // todo: "The rate of removal of the people in class E to the infective class I is proportional to the number of people in class E, that is bE(t), where b is a positive number."
  // todo: "The incubation period (the time from first infection to the appearances of symptoms) plus the onset to admission interval is equal to the sum of the latent period and the infectious period and is therefore equal to 1/b + 1/a."

  // Tests from PT-2012-ET Measurement and Estimation Using Modified PT in Maise with Mulching-petpt_2012
  // todo: "De Bruin (1983) developed the PT coefficient model as a function of surface resistance."
  // todo: "The different growing stages were divided by our local visual observations of maize development characteristics and phenology, combined with changes of maize height and leaf area (Allen et al., 1998; Xu et al., 2002)."

  // Tests from Global estimation of evapotranspiration using a leaf area index-based surface energy and water balance model
  // todo: "introducing a simple biophysical model for canopy conductance (Gc), defined as a constant maximum stomatal conductance gs max of 12.2mm s−1 multiplied by air relative humidity (Rh) and Lai (Gc=gs max×Rh×Lai)"
  // todo: "The surface energy balance partitions the available energy (Rn−G) between turbulent heat fluxes (λE and H):"
  // todo: "The ARTS E model requires inputs of Lai, net radiation, Rh, air temperature, wind speed, canopy height, precipitation, and maximum soil available water content (Mawc) as model parameters."
  // todo: "The SWB model requires as inputs precipitation, E0, air temperature, and Mawc. Its outputs are Ea, soil water content, and runoff."

  // Tests from 2003-DSSAT
  // todo: potential root water uptake is computed by calculating a maximum water flow to roots in each layer and summing these values (hierarchical function)

  // todo: It also computes the root water uptake of each soil layer. The daily weather values as well as all soil properties and current soil water content, by layer, are required as input. In addition, leaf area index (LAI) and root length density for each layer are needed.
  // todo: The potential ET is partitioned into potential soil evaporation based on the fraction of solar energy reaching the soil surface, based on a negative exponential function of LAI, and potential plant transpiration.
  // todo: This ratio is typically used in the Plant modules to reduce photosynthesis in proportion to relative decreases in transpiration.
  // todo: a ratio of potential root water uptake and potential transpiration is used to reduce plant turgor and expansive growth of crops
  // todo: The daily canopy photosynthesis option, modified from the method used in SOYGRO V5.4 (Jones et al., 1989), predicts daily gross photosynthesis as a function of daily irradiance for a full canopy, which is then multiplied by factors 0/1 for light interception, temperature, leaf nitrogen status, and water deficit.
  // todo: Daylength may affect the total number of leaves formed by altering the duration of the floral induction phase, and thus, floral initiation. //note: does this counts as a function example?
  // todo: The amount of new dry matter available for growth each day may also be modified by the most limiting of water or nitrogen stress, and temperature, and is sensitive to atmospheric CO2 concentration.
  // todo: An important aspect of many of these studies is a consideration that weather influences the performance of crops, interacting in complex ways with soil and management. # note: influence - function?

// Tests from model for predicting evaporation from a row crop with incomplete cover
// todo: As the plant cover increases, the evaporation rate becomes more dependent on the leaf area [Penman et al., 1967] and the potential evaporation so long as the soil water available to the plant roots is not limited
// todo: In the falling rate stage (stage 2), the surface soil water content has decreased below a threshold value, so that Es depends on the flux of water through the upper layer of soil to the evaporating site near the surface.
// todo: These data demonstrate that the initial fast rate of drying is followed by a decreasing rate.
// todo: In the Adelanto soil, the evaporation rate began to decline below the approximate Eo of 8 mm/day when the cumulative evaporation reached about 12 mm.
// todo: A plot of (9) expressing Ep as a fraction of E0 versus Lai is given in Figure 5.

// Tests from 1985-description and performance of CERES-Wheat_A_user-oriented wheat yield model