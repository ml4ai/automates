package org.clulab.aske.automates.text

import org.clulab.aske.automates.TestUtils._

class TestConjunctions extends ExtractionTest {

    val t2j = "(where S(0) and R(0) are the initial numbers of, respectively, susceptible and removed subjects)"
  failingTest should s"find definitions from t2j: ${t2j}" taggedAs(Somebody) in {
    val desired =  Seq(
      "S(0)" -> Seq("initial number of susceptible subjects"), // issue: This test should be moved to conjunction once the file is made.
      "R(0)" -> Seq("initial number of removed subjects")      // fixme: "S" only is captured as the variable here. Should be fixed to capture both S(0) and R(0) as variables. Definitions should be divided as well.
    )
    val mentions = extractMentions(t2j)
    testDefinitionEvent(mentions, desired)
  }

    val t2k = "where Rns and Rnc are net radiation obtained by soil surface and intercepted by crop canopy (W m−2), respectively; αs and αc are soil " +
      "evaporation coefficient and crop transpiration coefficient, respectively."
  failingTest should s"find definitions from t2k: ${t2k}" taggedAs(Somebody) in {
    val desired =  Seq(
      "Rns" -> Seq("net radiation obtained by soil surface"), // fixme: Only "Rns" is captured as variable here. The definition is also incomplete. ("net radiation")
      "Rnc" -> Seq("net radiation intercepted by crop canopy"),
      "αs" -> Seq("soil evaporation coefficient"), // fixme: Only "αs" is captured as variable here.
      "αc" -> Seq("crop transpiration coefficient") // fixme: The definition for "αc" was not captured.
    )
    val mentions = extractMentions(t2k)
    testDefinitionEvent(mentions, desired)
  }

}