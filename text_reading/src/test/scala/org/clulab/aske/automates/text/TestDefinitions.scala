package org.clulab.aske.automates.text

import org.clulab.aske.automates.TestUtils.ExtractionTest

class TestDefinitions extends ExtractionTest {

  passingTest should "find definitions 1" in {

    val text = "where Kcdmin is the minimum crop coefficient or Kcd at LAI = 0, Kcdmax is the maximum crop " +
      "coefficient at high LAI, and SKc is a shaping parameter that determines the shape of the Kcd versus LAI curve."

    val desired = Map(
      "Kcdmin" -> Seq("minimum crop coefficient"),
      "Kcdmax" -> Seq("maximum crop coefficient"), // Seq("maximum crop coefficient at high LAI"), fixme?
      "SKc" -> Seq("shaping parameter")
    )
    val mentions = extractMentions(text)
    testDefinitionEvent(mentions, desired)

  }

}
