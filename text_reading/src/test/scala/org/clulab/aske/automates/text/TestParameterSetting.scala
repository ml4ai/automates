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


  val t1 = "EORATIO for maize simulations was hard-coded to 1.0 within DSSAT-CSM."
  passingTest should s"extract definitions from t1: ${t1}" taggedAs(Somebody) in {
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
//      "Kcbmax" -> Seq("1.15") //todo is this going to break if there are two kcbmax values
//    )
//    val mentions = extractMentions(t2)
//    testParameterSettingEvent(mentions, desired)
//  }

}
