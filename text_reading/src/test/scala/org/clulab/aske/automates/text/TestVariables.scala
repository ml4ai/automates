package org.clulab.aske.automates.text

import org.clulab.aske.automates.TestUtils._
import org.clulab.aske.automates.TestUtils.ExtractionTest

class TestVariables extends ExtractionTest {
  val text = "where Kcdmin is the minimum crop coefficient or Kcd at LAI = 0, Kcdmax is the maximum crop " +
    "coefficient at high LAI, and SKc is a shaping parameter that determines the shape of the Kcd versus LAI curve."

  "Kcdmin" should "be defined" in {

    val mentions = extractMentions(text)
    // Kcdmin should be a variable with 'the minimum crop coefficient or Kcd' as the definition
    val desiredVariable = "Kcdmin"
    val desiredDefinition = "minimum crop coefficient"

    val definedVariables = mentions.filter(_ matches "Definition")
    definedVariables.length should be 1
    val kcdDef = definedVariables.head

    val variables = kcdDef.arguments("variable")
    variables.length should be 1
    variables.head.text should be(desiredVariable)

    val definitions = kcdDef.arguments("definition")
    definitions.length should be 1
    definitions.head.text should be(desiredDefinition)

  }

}
