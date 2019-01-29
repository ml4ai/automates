package org.clulab.aske.automates.text

import org.clulab.aske.automates.TestUtils.ExtractionTest
import org.clulab.aske.automates.OdinEngine.VARIABLE_LABEL

class TestVariables extends ExtractionTest {

  passingTest should "find variables 1" in {
      val text = "where Kcdmin is the minimum crop coefficient or Kcd at LAI = 0, Kcdmax is the maximum crop " +
        "coefficient at high LAI, and SKc is a shaping parameter that determines the shape of the Kcd versus LAI curve."

      val desired = Seq("Kcdmin", "Kcd", "LAI", "Kcdmax", "LAI", "SKc", "Kcd", "LAI")
      val mentions = extractMentions(text)
      testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }


  passingTest should "find variables 2" in {
    val text = "Note that Kcdmax in equation 5 is different from Kcdmax in equation A6."

    val desired = Seq("Kcdmax", "Kcdmax")
    val mentions = extractMentions(text)
    testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }

}
