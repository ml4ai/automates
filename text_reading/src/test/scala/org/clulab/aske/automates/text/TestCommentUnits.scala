package org.clulab.aske.automates.text

import org.clulab.aske.automates.TestUtils._

class TestCommentDefinitions extends ExtractionFromCommentsTest {


  val t1a = "EEQ Equilibrium evaporation (mm/d)"
  passingTest should s"extract definitions from t1a: ${t1a}" taggedAs(Somebody) in {
    val desired = Seq(
      "EEQ" -> Seq("Equilibrium evaporation")
    )
    val mentions = extractMentions(t1a)
    testDefinitionEvent(mentions, desired)
  }

  val t2a = "S Rate of change of saturated vapor pressure of air with temperature (Pa/K)"
  passingTest should s"extract definitions from t1a: ${t2a}" taggedAs(Somebody) in {
    val desired = Seq(
      "S" -> Seq("Rate of change of saturated vapor pressure of air with temperature")
    )
    val mentions = extractMentions(t2a)
    testDefinitionEvent(mentions, desired)
  }



}
