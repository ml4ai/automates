package org.clulab.aske.automates.text

import org.clulab.aske.automates.TestUtils._

class TestParameterSettingEventInterval  extends ExtractionTest {

  // Tests from paper: 2017-IMPLEMENTING STANDARDIZED REFERENCE EVAPOTRANSPIRATION AND DUAL CROP COEFFICIENT APPROACH IN THE DSSAT CROPPING SYSTEM MODEL

  val t1a = "If E and T data are unavailable, values of SKc from 0.5 to 0.7 are recommended and values of Kc from 0.3 to 0.9."
  passingTest should s"extract the parameter setting(s) from t13a: ${t1a}" taggedAs(Somebody, Interval) in {

    val desired = Seq(
      "SKc" -> Seq("0.5", "0.7"),
      "Kc" -> Seq("0.3", "0.9") //this second arg is a toy example
    )

    val mentions = extractMentions(t1a)
    testParameterSettingEventInterval(mentions, desired)
  }

  val t2a = "The value of SKc was varied between 0.4 and 0.9 with a base level of 0.5 for maize and 0.6 for cotton from prior calibration efforts."
  passingTest should s"extract the parameter setting(s) from t2a: ${t2a}" taggedAs(Somebody, Interval) in {

    val desired = Seq(
      "SKc" -> Seq("0.4", "0.9")
    )

    val mentions = extractMentions(t2a)
    testParameterSettingEventInterval(mentions, desired)
  }

  val t3a = "where KEP (typically ranging from 0.5 to 0.8) is defined as an energy extinction coefficient of the canopy for total solar irradiance"
  passingTest should s"extract the parameter setting(s) from t3a: ${t3a}" taggedAs(Somebody, Interval) in {

    val desired = Seq(
      "KEP" -> Seq("0.5", "0.8")
    )

    val mentions = extractMentions(t3a)
    testParameterSettingEventInterval(mentions, desired)
  }

  val t4a = "Under full irrigation, Kcbmax with the ETo-Kcb method had little influence on maize and cotton yield " +
    "for 0.9 < Kcbmax < 1.15, but simulated yield decreased rapidly for Kcbmax > 1.15 (fig. 6a)."
  failingTest should s"extract the parameter setting(s) from t12a and NOT extract the figure number: ${t4a}" taggedAs(Somebody, Interval) in {
    val desired = Seq(
            "Kcbmax" -> Seq("0.9", "1.5"),
            "Kcbmax" -> Seq("1.15") //todo: need to have some mechanism to preserve ><=. some sort of attachment? similar to count in wm or use 'valueMin'/'valueMax' for the var
    )
    val mentions = extractMentions(t4a)
    testParameterSettingEvent(mentions, desired)
  }


  //
//  // Tests from paper: 2005-THE ASCE STANDARDIZED REFERENCE EVAPOTRANSPIRATION EQUATION
//  val t1b = "Rns and Rnl are generally positive or zero in value."
//  failingTest should s"extract the parameter setting(s) from t3a: ${t3a}" taggedAs(Somebody, Interval) in {
//
//    val desired = Seq(
//      "KEP" -> Seq("0", "0.8") //todo: need a rule for "range from"
//    )
//
//    val mentions = extractMentions(t3a)
//    testParameterSettingEventInterval(mentions, desired)
//  }


}
