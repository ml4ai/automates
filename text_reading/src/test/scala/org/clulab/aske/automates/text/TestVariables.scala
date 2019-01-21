package org.clulab.aske.automates.text

import org.clulab.aske.automates.TestUtils._
import org.clulab.aske.automates.TestUtils.ExtractionTest
import org.clulab.odin.Mention

class TestVariables extends ExtractionTest {
  val text = "where Kcdmin is the minimum crop coefficient or Kcd at LAI = 0, Kcdmax is the maximum crop " +
    "coefficient at high LAI, and SKc is a shaping parameter that determines the shape of the Kcd versus LAI curve."
  val textShort = "where Kcdmin is the minimum crop coefficient or Kcd at LAI = 0"

  "Kcdmin" should "be defined" in {

    val mentions = extractMentions(textShort)

    val definedVariables = mentions.filter(_ matches "Definition")
    definedVariables.length should be(1)
    val kcdDef = definedVariables.head

    testDefinitionEvent(kcdDef, "Kcdmin", Seq("minimum crop coefficients"))

  }

}

object TestMethods {


}

