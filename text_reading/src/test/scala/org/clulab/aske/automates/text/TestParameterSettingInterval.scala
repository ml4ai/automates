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

}
