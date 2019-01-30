package org.clulab.aske.automates.text

import org.clulab.aske.automates.TestUtils._

class TestParameterSetting  extends ExtractionTest {

//  passingTest should "set parameters 1" in {
//    val text = "where Kcdmin is the minimum crop coefficient or Kcd at LAI = 0, Kcdmax is the maximum crop " +
//      "coefficient at high LAI, and SKc is a shaping parameter that determines the shape of the Kcd versus LAI curve."
//
//    val desired = Map(
//      "LAI" -> Seq("0")
//    )
//    val mentions = extractMentions(text)
//    testParameterSettingEvent(mentions, desired)
//  }


  // Tests from paper: 2017-IMPLEMENTING STANDARDIZED REFERENCE EVAPOTRANSPIRATION AND DUAL CROP COEFFICIENT APPROACH IN THE DSSAT CROPPING SYSTEM MODEL

  //todo: decide if we want to explicitly state in the name of the test what we are extracting
  //can be done after we have confirmed that the tests look correct

  val t1 = "EORATIO for maize simulations was hard-coded to 1.0 within DSSAT-CSM."
  passingTest should s"extract the parameter setting(s) from t1: ${t1}" taggedAs(Somebody) in {
    val desired = Map(
      "EORATIO" -> Seq("1.0")
    )
    val mentions = extractMentions(t1)
    testParameterSettingEvent(mentions, desired)
  }
//
//  val t2 = "The value of Kcbmax was varied between 0.9 and 1.4 with a base level of Kcbmax = 1.15, which is the " +
//    "tabular value from FAO-56 (Allen et al., 1998) for both crops."
//  passingTest should s"extract definitions from t1: ${t2}" taggedAs(Somebody) in {
//    val desired = Map(
//      "Kcbmax" -> Seq("0.9", "1.4"), // todo: depends on how we decide to return intervals
//      "Kcbmax" -> Seq("1.15") //todo is this going to break if there are two kcbmax values -- Yes, see comment in t8
//    )
//    val mentions = extractMentions(t2)
//    testParameterSettingEvent(mentions, desired)
//  }

  val t3 = "The value of SKc was varied between 0.4 and 0.9 with a base level of 0.5 for maize and 0.6 for cotton from " +
    "prior calibration efforts."
  passingTest should s"extract the parameter setting(s) from t3: ${t3}" taggedAs(Somebody) in {
    val desired = Map(
      "SKc" -> Seq("0.4", "0.9", "0.5", "0.6") // the last two need to come with modifiers (e.g., for maize)
    )
    val mentions = extractMentions(t3)
    testParameterSettingEvent(mentions, desired)
  }

  val t4 = "With an assumption of Kcbmin = 0 as described before, the values of Kcbmax and SKc were varied to " +
    "understand the influence of these variables on simulated yield and ETc for maize and cotton."
  passingTest should s"extract the parameter setting(s) from t4: ${t4}" taggedAs(Somebody) in {
    val desired = Map(
      "Kcbmin" -> Seq("0")
    )
    val mentions = extractMentions(t4)
    testParameterSettingEvent(mentions, desired)
  }

  val t5 = "With an RMSE of 22.8%, drastic discrepancies were found in the comparison of Ref-ET ETo and ETpm from " +
    "DSSAT-CSM version 4.5 for Arizona conditions (fig. 1a)."
  passingTest should s"NOT extract model version, but should extract the parameter setting(s) from t5: ${t5}" taggedAs(Somebody) in {
    val desired = Map(
      "RMSE" -> Seq("22.8") //todo: see t8 for an example where model version is relevant
    )
    val mentions = extractMentions(t5)
    testParameterSettingEvent(mentions, desired)
  }

  val t6 = "In 2014, the authors linked the problem to a misspecification of the equation used to adjust wind speed " +
    "measurements to a standard height of 2.0 m."
  passingTest should s"extract the parameter setting(s) from t6: ${t6}" taggedAs(Somebody) in {
    val desired = Map(
      "wind speed measurements" -> Seq("2.0 m") //todo: attaching value and unit? finding variables when they are spelled out?
    )
    val mentions = extractMentions(t6)
    testParameterSettingEvent(mentions, desired)
  }

  val t7 = "where u2 is the calculated wind speed at a standard height of 2.0 m, uz is the measured wind speed at a " +
    "height of zw, and α is an empirically derived coefficient that is hard-coded but varies based on the stability of " +
    "the atmosphere."
  passingTest should s"extract the parameter setting(s) from t7: ${t7}" taggedAs(Somebody) in {
    val desired = Map(
      "wind speed" -> Seq("2.0 m") //todo: attaching value and unit? spelt out term?
    )
    val mentions = extractMentions(t7)
    testParameterSettingEvent(mentions, desired)
  }


  val t8 = "In DSSATCSM v4.5, the model erroneously used α = 2.0, which was corrected to α = 0.2 in DSSAT-CSM v4.6."
  passingTest should s"extract the parameter setting(s) from t8: ${t8}" taggedAs(Somebody) in {
    val desired = Map(
      "α" -> Seq("2.0"),
      "α" -> Seq("0.2") //todo: this is a map but have the same key, so we get this error (2 was not equal to 1
      // (TestUtils.scala:70)), where the first two is the number of mentions found (I think)
    )
    val mentions = extractMentions(t8)
    testParameterSettingEvent(mentions, desired)
  }

//  val t9 = "This coding error in DSSAT-CSM version 4.5 (and likely prior versions) greatly affects ETpm calculations " +
//    "for weather networks with anemometers at heights other than 2.0 m, such as AZMET in Arizona, but has no effect on " +
//    "networks with anemometers at 2.0 m, such as CoAgMet in Colorado."
//  passingTest should s"extract the parameter setting(s) from t9: ${t9}" taggedAs(Somebody) in {
//    val desired = Map(
//      "???" -> Seq("2.0 m"), //todo what will be the variable?
//      "???" -> Seq("2.0 m")
//    )
//    val mentions = extractMentions(t9)
//    testParameterSettingEvent(mentions, desired)
//  }

  val t10 = "Thus, differences between ETpm (figs. 1b and 1e) and ETo (figs. 1c and 1f) calculations in DSSAT-CSM " +
    "version 4.6 are partially attributed to different wind speed adjustment equations for each method " +
    "(eqs. 9 versus 10, respectively)."
  passingTest should s"extract NO parameter setting(s) from t10: ${t10}" taggedAs(Somebody) in {
    val desired = Map.empty[String, Seq[String]] //todo: unless we decide to extract model version
    val mentions = extractMentions(t10)
    testParameterSettingEvent(mentions, desired)
  }

  val t11 = "As canopy cover increased with vegetative growth, the transpiration portion exceeded the evaporation " +
    "portion of ET, beginning around DOY 165 for maize and DOY 175 for cotton."
  passingTest should s"extract the parameter setting(s) from t11: ${t11}" taggedAs(Somebody) in {
    val desired = Map(
      "DOY" -> Seq("165"),
      "DOY" -> Seq("175") // todo: see t8
    )
    val mentions = extractMentions(t11)
    testParameterSettingEvent(mentions, desired)
  }

  val t12 = "Under full irrigation, Kcbmax with the ETo-Kcb method had little influence on maize and cotton yield " +
    "for 0.9 < Kcbmax < 1.15, but simulated yield decreased rapidly for Kcbmax > 1.15 (fig. 6a)."
  passingTest should s"extract the parameter setting(s) from t12 and NOT extract the figure number: ${t12}" taggedAs(Somebody) in {
    val desired = Map(
      "Kcbmax" -> Seq("0.9", "1.5"), //todo: how do we extract intervals like this?
      "Kcbmax" -> Seq("1.15") //todo: see t8
    )
    val mentions = extractMentions(t12)
    testParameterSettingEvent(mentions, desired)
  }

  val t13 = "If E and T data are unavailable, values of SKc from 0.5 to 0.7 are recommended."
  passingTest should s"extract the parameter setting(s) from t13 and NOT extract the figure number: ${t13}" taggedAs(Somebody) in {
    val desired = Map(
      "SKc" -> Seq("0.5", "0.7") //todo: how do we extract intervals like this?
    )
    val mentions = extractMentions(t13)
    testParameterSettingEvent(mentions, desired)
  }

  val t14 = "For the mid-season transpiration portion, the ETo-Kcs method for maize had the limitation of Kcs = 1.0 " +
    "(fig. 2a) and for cotton was defined very close to 1.0 (fig. 3a)."
  passingTest should s"extract the parameter setting(s) from t14 and NOT extract the figure numbers: ${t14}" taggedAs(Somebody) in {
    val desired = Map(
      "Kcs" -> Seq("0.1"),
      "Kcs" -> Seq("1.0") //todo: do we want to account for "close" in "close to 1.0"?
    )
    val mentions = extractMentions(t14)
    testParameterSettingEvent(mentions, desired)
  }

}
