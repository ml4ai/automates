package org.clulab.aske.automates.text

import org.clulab.aske.automates.TestUtils._

class TestParameterSetting  extends ExtractionTest {

  val text1 = "where Kcdmin is the minimum crop coefficient or Kcd at LAI = 0, Kcdmax is the maximum crop " +
    "coefficient at high LAI, and SKc is a shaping parameter that determines the shape of the Kcd versus LAI curve."
  passingTest should s"extract the parameter setting(s) from text 1: ${text1}" in {
    val desired = Seq(
      "LAI" -> Seq("0")
    )
    val mentions = extractMentions(text1)
    testParameterSettingEvent(mentions, desired)
  }


  // Tests from paper: 2017-IMPLEMENTING STANDARDIZED REFERENCE EVAPOTRANSPIRATION AND DUAL CROP COEFFICIENT APPROACH IN THE DSSAT CROPPING SYSTEM MODEL

  val t1a = "EORATIO for maize simulations was hard-coded to 1.0 within DSSAT-CSM."
  passingTest should s"extract the parameter setting(s) from t1a: ${t1a}" taggedAs(Somebody) in {
    val desired = Seq(
      "EORATIO" -> Seq("1.0")
    )
    val mentions = extractMentions(t1a)
    testParameterSettingEvent(mentions, desired)
  }
//
//  val t2a = "The value of Kcbmax was varied between 0.9 and 1.4 with a base level of Kcbmax = 1.15, which is the " +
//    "tabular value from FAO-56 (Allen et al., 1998) for both crops."
//  failingTest should s"extract descriptions from t1a: ${t2a}" taggedAs(Somebody) in {
//    val desired = Seq(
//      "Kcbmax" -> Seq("0.9", "1.4"), // todo: depends on how we decide to return intervals
//      "Kcbmax" -> Seq("1.15") //todo is this going to break if there are two kcbmax values -- Yes, see comment in t8
//    )
//    val mentions = extractMentions(t2a)
//    testParameterSettingEvent(mentions, desired)
//  }

  val t3a = "The value of SKc was varied between 0.4 and 0.9 with a base level of 0.5 for maize and 0.6 for cotton from " +
    "prior calibration efforts."
  failingTest should s"extract the parameter setting(s) from t3a: ${t3a}" taggedAs(Somebody) in {
    val desired = Seq(
      "SKc" -> Seq("0.5"),
      "Skc" -> Seq("0.6") // todo: need a more fine-grained test with modifiers, e.g., SKc -> 0.5, maize; potential trigger - "level"
    )

    //fixme: need a better rule to capture 0.5 and 0.6
    val mentions = extractMentions(t3a)
    testParameterSettingEvent(mentions, desired)
  }

  val t4a = "With an assumption of Kcbmin = 0 as described before, the values of Kcbmax and SKc were varied to " +
    "understand the influence of these variables on simulated yield and ETc for maize and cotton."
  passingTest should s"extract the parameter setting(s) from t4a: ${t4a}" taggedAs(Somebody) in {
    val desired = Seq(
      "Kcbmin" -> Seq("0")
    )
    val mentions = extractMentions(t4a)
    testParameterSettingEvent(mentions, desired)
  }

  val t5a = "With an RMSE of 22.8%, drastic discrepancies were found in the comparison of Ref-ET ETo and ETpm from " +
    "DSSAT-CSM version 4.5 for Arizona conditions (fig. 1a)."
  passingTest should s"NOT extract model version, but should extract the parameter setting(s) from t5a: ${t5a}" taggedAs(Somebody) in {
    val desired = Seq(
      "RMSE" -> Seq("22.8") //todo: see t8 for an example where model version is relevant; need a rule for % as a unit
    )
    val mentions = extractMentions(t5a)
    testParameterSettingEvent(mentions, desired)
  }

  val t6a = "In 2014, the authors linked the problem to a misspecification of the equation used to adjust wind speed " +
    "measurements to a standard height of 2.0 m"
  passingTest should s"extract the parameter setting(s) from t6a: ${t6a}" taggedAs(Somebody) in {
    val desired = Seq(
      "wind speed measurements" -> Seq("2.0") //todo: attaching value and unit? - finding variables when they are spelled out? - yes.
      //todo: rule with trigger "adjust"
    )
    val mentions = extractMentions(t6a)
    testParameterSettingEvent(mentions, desired)
  }

//  val t7a = "where u2 is the calculated wind speed at a standard height of 2.0 m, uz is the measured wind speed at a " +
//    "height of zw, and α is an empirically derived coefficient that is hard-coded but varies based on the stability of " +
//    "the atmosphere."
//  failingTest should s"extract the parameter setting(s) from t7: ${t7}" taggedAs(Somebody) in {
//    val desired = Seq(
//      "height" -> Seq("2.0 m") //todo: attaching value and unit? spelt out term?
//    )
//    val mentions = extractMentions(t7)
//    testParameterSettingEvent(mentions, desired)
//  }


  val t8a = "In DSSATCSM v4.5, the model erroneously used α = 2.0, which was corrected to α = 0.2." //todo: breaks if followed by  'in DSSAT-CSM v4.6' because 'in' is found as unit (inch)
  passingTest should s"extract the parameter setting(s) from t8a: ${t8a}" taggedAs(Somebody) in {
    val desired = Seq(
      "α" -> Seq("2.0"),
      "α" -> Seq("0.2")
      // (TestUtils.scala:70)), where the first two is the number of mentions found (I think)
    )
    val mentions = extractMentions(t8a)
    testParameterSettingEvent(mentions, desired)
  }

  val t9a = "This coding error in DSSAT-CSM version 4.5 (and likely prior versions) greatly affects ETpm calculations " +
    "for weather networks with anemometers at heights other than 2.0 m, such as AZMET in Arizona, but has no effect on " +
    "networks with anemometers at 2.0 m, such as CoAgMet in Colorado."
  toDiscuss should s"extract the parameter setting(s) from t9a: ${t9a}" taggedAs(Somebody, DiscussWithModelers) in {
    val desired = Seq(
      "anemometers" -> Seq("2.0 m"), //todo what will be the variable?
      "???" -> Seq("2.0 m")
    )
    val mentions = extractMentions(t9a)
    testParameterSettingEvent(mentions, desired)
    //todo: rule for 'other than'? need to store "not equal" constraint
  }

  val t10a = "Thus, differences between ETpm (figs. 1b and 1e) and ETo (figs. 1c and 1f) calculations in DSSAT-CSM " +
    "version 4.6 are partially attributed to different wind speed adjustment equations for each method " +
    "(eqs. 9 versus 10, respectively)."
  passingTest should s"extract NO parameter setting(s) from t10a: ${t10a}" taggedAs(Somebody) in {
    val desired = Seq.empty[(String, Seq[String])] //todo: unless we decide to extract model version
    val mentions = extractMentions(t10a)
    testParameterSettingEvent(mentions, desired)
  }

  val t11a = "As canopy cover increased with vegetative growth, the transpiration portion exceeded the evaporation " +
    "portion of ET, beginning around DOY 165 for maize and DOY 175 for cotton."
  passingTest should s"extract the parameter setting(s) from t11a: ${t11a}" taggedAs(Somebody) in {
    val desired = Seq(
      "DOY" -> Seq("165"),
      "DOY" -> Seq("175") // todo: see t8
    )
    val mentions = extractMentions(t11a)
    testParameterSettingEvent(mentions, desired)
  }


  val t13a = "If E and T data are unavailable, values of SKc from 0.5 to 0.7 are recommended."
    passingTest should s"NOT extract the figure number: ${t13a}" taggedAs(Somebody) in {
    val desired = Seq.empty
    val mentions = extractMentions(t13a)
    testParameterSettingEvent(mentions, desired)
  }

  val t14a = "For the mid-season transpiration portion, the ETo-Kcs method for maize had the limitation of Kcs = 1.0 " +
    "(fig. 2a) and for cotton was defined very close to 1.0 (fig. 3a)."
  toDiscuss should s"extract the parameter setting(s) from t14a and NOT extract the figure numbers: ${t14a}" taggedAs(Somebody, DiscussWithModelers) in {
    val desired = Seq(
      "Kcs" -> Seq("0.1"),
      "Kcs" -> Seq("1.0") //todo: do we want to account for "close" in "close to 1.0"?
      //fixme: need to extract more info e.g., for maize', 'for cotton'
    )
    val mentions = extractMentions(t14a)
    testParameterSettingEvent(mentions, desired)
  }


  //Tests from paper 2005-THE ASCE STANDARDIZED REFERENCE EVAPOTRANSPIRATION EQUATION

  val t1b = "For ETsz, a constant value of λ = 2.45 MJ kg-1 is recommended."
  passingTest should s"extract the parameter setting(s) from t1b: ${t1b}" taggedAs(Somebody) in {
    val desired = Seq(
      "λ" -> Seq("2.45")
    )
    val mentions = extractMentions(t1b)
    testParameterSettingEvent(mentions, desired)
  }

//  val t2b = "For ETsz, a constant value of λ = 2.45 MJ kg-1 is recommended."
//  passingTest should s"extract the parameter setting(s) from t2b: ${t2b}" taggedAs(Somebody) in {
//    val desired = Seq(
//      "ETsz" -> Seq("2.45")
//    )
//    val mentions = extractMentions(t2b)
//    testParameterSettingEvent(mentions, desired)
//  }


  val t3b = "The density of water (ρw) is taken as 1.0 Mg m-3."
  passingTest should s"extract the parameter setting(s) from t3b: ${t3b}" taggedAs(Somebody) in {
    val desired = Seq(
      "ρw" -> Seq("1.0")
    )
    val mentions = extractMentions(t3b)
    testParameterSettingEvent(mentions, desired)
  }

  val t4b = " The inverse ratio of λ ρw times energy flux in MJ m-2 d-1 equals 1.0 mm d-1."
  passingTest should s"extract the parameter setting(s) from t4b: ${t4b}" taggedAs(Somebody) in {
    val desired = Seq(
      "inverse ratio of λ ρw times energy flux" -> Seq("1.0")
    )
    val mentions = extractMentions(t4b)
    testParameterSettingEvent(mentions, desired)
  }

  val t1c = "We therefore assume that S(0) = 6.8 – 0.5 = 6.3 million."
  failingTest should s"extract the parameter setting(s) from t1c: ${t1c}" taggedAs(Somebody) in {
    val desired = Seq(
      "S(0)" -> Seq("6.3 million")
    )
    val mentions = extractMentions(t1c)
    testParameterSettingEvent(mentions, desired)
  }

  // SuperMaaS tests

  val u1a = "Default nitrogen removal is 15 % for sheep & beef, and 25 % for dairy grazed pastures but it remains the user's choice to set a sensible value for their system ."
  failingTest should s"extract the parameter setting(s) from u1a: ${u1a}" taggedAs(Somebody) in {
    val desired = Seq(
      "nitrogen removal" -> Seq("15"), //fixme: handle percentages
      "nitrogen removal" -> Seq("25")
    )
    val mentions = extractMentions(u1a)
    testParameterSettingEvent(mentions, desired)
  }

  val u2a = "It shows that the pasture is not harvested before 1/07/1995 , the harvest frequency is once every 21 days and the harvest residual is 1250 kg / ha ."
  failingTest should s"extract the parameter setting(s) from u2a: ${u2a}" taggedAs(Somebody) in {
    val desired = Seq(
      "harvest residual" -> Seq("1250")
    )
    val mentions = extractMentions(u2a)
    testParameterSettingEvent(mentions, desired)
  }

  val u3a = "85 % of grazed / harvested nitrogen returns to soil , of which 60 % is in urine and returned to soil profile to a depth of 300 mm ."
  failingTest should s"extract the parameter setting(s) from u3a: ${u3a}" taggedAs(Somebody) in {
    val desired = Seq(
      "soil profile to a depth" -> Seq("300") //fixme: should actually be soil profile depth but this is good enough
    )
    val mentions = extractMentions(u3a)
    testParameterSettingEvent(mentions, desired)
  }

  val u4a = "where sowing depth was known and it is set to 1.5 o Cd per mm ."
  passingTest should s"extract the parameter setting(s) from u4a: ${u4a}" taggedAs(Somebody) in {
    val desired = Seq(
      "sowing depth" -> Seq("1.5")
    )
    val mentions = extractMentions(u4a)
    testParameterSettingEvent(mentions, desired)
  }

  val u4atoy = " where St is sowing depth  and it is set to 1.5 o Cd per mm ."
  passingTest should s"extract the parameter setting(s) from u4atoy: ${u4atoy}" taggedAs(Somebody) in {
    val desired = Seq(
      "St" -> Seq("1.5")
    )
    val mentions = extractMentions(u4atoy)
    testParameterSettingEvent(mentions, desired)
  }

  val u5a = "For the purposes of model parameterisation the value of shoot_lag has been assumed to be around 40 o Cd."
  passingTest should s"extract the parameter setting(s) from u5a: ${u5a}" taggedAs(Somebody) in {
    val desired = Seq(
      "value of shoot_lag" -> Seq("40")
    )
    val mentions = extractMentions(u5a)
    testParameterSettingEvent(mentions, desired)
  }

  val u6a = "This means that at a sowing depth of 4 cm emergence occurs..."
  failingTest should s"extract the parameter setting(s) from u6a: ${u6a}" taggedAs(Somebody) in {
    val desired = Seq(
      "sowing depth" -> Seq("4")
    )
    val mentions = extractMentions(u6a)
    testParameterSettingEvent(mentions, desired)
  }

  val u7a = "Phenology APSIM-Barley uses 11 crop stages and ten phases ( time between stages ) ."
  failingTest should s"extract the parameter setting(s) from u7a: ${u7a}" taggedAs(Somebody) in {
    val desired = Seq(
      "crop stages" -> Seq("11"),
      "phases" -> Seq("ten") // when have started handling word param settings, switch to `10`
    )
    val mentions = extractMentions(u7a)
    testParameterSettingEvent(mentions, desired)
  }

  val u9a = "Photoperiod is calculated from day of year and latitude using standard astronomical equations accounting for civil twilight using the parameter twilight, which is assumed to be -6 o."
  failingTest should s"extract the parameter setting(s) from u9a: ${u9a}" taggedAs(Somebody, Interval) in {
    val desired = Seq(
      "parameter twilight" -> Seq("-6")
    )
    val mentions = extractMentions(u9a)
    testParameterSettingEvent(mentions, desired)
  }

  val u10a = "The barley module allows a total retranslocation of no more than 20 % of stem biomass present at the start of grainfilling. Grain yield on a commercial moisture basis is calculated using the parameter grn_water_cont = 0.125 ."
  failingTest should s"extract the parameter setting(s) from u10a: ${u10a}" taggedAs(Somebody, Interval) in {
    val desired = Seq(
      "grn_water_cont" -> Seq("0.125")
    )
    val mentions = extractMentions(u10a)
    testParameterSettingEvent(mentions, desired)
  }

  val u11a = "Leaf initiation / appearance and tillering leaves appear at a fixed phyllochron of thermal time, currently set to 95 o Cd in the barley."
  failingTest should s"extract the parameter setting(s) from u11a: ${u11a}" taggedAs(Somebody, Interval) in {
    val desired = Seq(
      "phyllochron of thermal time" -> Seq("95") // this is likely not solveable
    )
    val mentions = extractMentions(u11a)
    testParameterSettingEvent(mentions, desired)
  }

  val u12a = "On the day of emergence, leaf area per plant is initialised to a value of 200 mm 2 per plant ."
  failingTest should s"extract the parameter setting(s) from u12a: ${u12a}" taggedAs(Somebody, Interval) in {
    val desired = Seq(
      "leaf area per plant" -> Seq("200")
    )
    val mentions = extractMentions(u12a)
    testParameterSettingEvent(mentions, desired)
  }

  val u13a = "Root biomass is converted to root length using the parameter specific_root_length ( currently assumed as 60000 mm / g for all species ) ."
  failingTest should s"extract the parameter setting(s) from u13a: ${u13a}" taggedAs(Somebody, Interval) in {
    val desired = Seq(
      "specific_root_length" -> Seq("60000")
    )
    val mentions = extractMentions(u13a)
    testParameterSettingEvent(mentions, desired)
  }

  val u14a = "The parameter root_depth_rate varies with growth stage and is typically zero after the start of grain filling ."
  failingTest should s"extract the parameter setting(s) from u14a: ${u14a}" taggedAs(Somebody, Interval) in {
    val desired = Seq(
      "root_depth_rate" -> Seq("zero")
    )
    val mentions = extractMentions(u14a)
    testParameterSettingEvent(mentions, desired)
  }

  val u15a = "It is assumed that leaf expansion growth is reduced when the supply / demand ratio for water is below 1.1 and stops when supply / demand ratio reaches 0.1 ."
  passingTest should s"extract the parameter setting(s) from u15a: ${u15a}" taggedAs(Somebody) in {
    val desired = Seq(
      "supply / demand ratio" -> Seq("0.1")
    )
    val mentions = extractMentions(u15a)
    testParameterSettingEvent(mentions, desired)
  }

  // source unknown
  val t1d = "If the parameters above are used to simulate the future spread of epidemic we obtain the value of R∞ to be 350."
  passingTest should s"extract the parameter setting(s) from t1d: ${t1d}" taggedAs(Somebody) in {
    val desired = Seq(
      "R∞" -> Seq("350")
    )
    val mentions = extractMentions(t1d)
    testParameterSettingEvent(mentions, desired)
  }


//  val t4b = "The value of RHmax generally exceeds 90% and approaches 100%."
//  passingTest should s"extract the parameter setting(s) from t1b: ${t4b}" taggedAs(Somebody) in {
//    val desired = Seq(
//      "The inverse ratio of λ ρw times energy flux" -> Seq("1.0")
//    )
//    val mentions = extractMentions(t4b)
//    testParameterSettingEvent(mentions, desired)
//  }

}
