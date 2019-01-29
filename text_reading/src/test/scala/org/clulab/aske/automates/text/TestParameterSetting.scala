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

}
