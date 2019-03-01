package org.clulab.aske.automates.text

import org.clulab.aske.automates.TestUtils._

class testParameterSettingEventInterval  extends ExtractionTest {

  // Tests from paper: 2017-IMPLEMENTING STANDARDIZED REFERENCE EVAPOTRANSPIRATION AND DUAL CROP COEFFICIENT APPROACH IN THE DSSAT CROPPING SYSTEM MODEL

  val t1a = "If E and T data are unavailable, values of SKc from 0.5 to 0.7 are recommended."
  passingTest should s"extract the parameter setting(s) from t13a: ${t1a}" taggedAs(Somebody, Interval) in {
    val desired = Seq(
      Seq("SKc", "0.5", "0.7")
    )
    val mentions = extractMentions(t1a)
    mentions.foreach(m => println("---> " + m.text + " " + m.arguments.toString()))
    testParameterSettingEventInterval(mentions, desired)
  }

}