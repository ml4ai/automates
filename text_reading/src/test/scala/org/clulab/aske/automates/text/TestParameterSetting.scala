package org.clulab.aske.automates.text

import org.clulab.aske.automates.TestUtils.ExtractionTest

class TestParameterSetting  extends ExtractionTest {

  passingTest should "set parameters 1" in {
    val text = "where Kcdmin is the minimum crop coefficient or Kcd at LAI = 0, Kcdmax is the maximum crop " +
      "coefficient at high LAI, and SKc is a shaping parameter that determines the shape of the Kcd versus LAI curve."

    val desired = Map(
      "LAI" -> Seq("0")
    )
    val mentions = extractMentions(text)
    testParameterSettingEvent(mentions, desired)
  }
}
