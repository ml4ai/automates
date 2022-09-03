package org.clulab.aske.automates.text

import org.clulab.aske.automates.TestUtils._

class TestPopulation extends ExtractionTest {


  // from: https://www.pnas.org/doi/pdf/10.1073/pnas.2111091119
  val t1a = "After data exclusions (Fig. 1), our final sample was 25,718 participants across 89 countries, representing all inhabited continents."
  passingTest should s"extract descriptions from t1a: ${t1a}" taggedAs(Somebody) in {
    val desired = Seq(
      "participants" -> Seq("25,718")
    )
    val mentions = extractMentions(t1a)
    testPopulationEvent(mentions, desired)
  }

  val t2a = "Of the total sample, 63.3% identified as female (n = 16,273), ..."
  passingTest should s"extract descriptions from t1a: ${t2a}" taggedAs(Somebody) in {
    val desired = Seq(
      "female" -> Seq("16,273"),
      "female" -> Seq("63.3%"),
    )
    val mentions = extractMentions(t2a)
    testPopulationEvent(mentions, desired)
  }

}
