package org.clulab.aske.automates.text

import org.clulab.aske.automates.TestUtils._

class TestCommentUnits extends ExtractionFromCommentsTest {


  val t1a = "EEQ Equilibrium evaporation (mm/d)"
  passingTest should s"extract identifiers and units from t1a: ${t1a}" taggedAs(Somebody) in {
    val desired = Seq(
      "EEQ" -> Seq("mm/d")
    )
    val mentions = extractMentions(t1a)
    testUnitEvent(mentions, desired)
  }

  val t2a = "S Rate of change of saturated vapor pressure of air with temperature (Pa/K)"
  passingTest should s"extract identifiers and units from t2a: ${t2a}" taggedAs(Somebody) in {
    val desired = Seq(
      "S" -> Seq("Pa/K")
    )
    val mentions = extractMentions(t2a)
    testUnitEvent(mentions, desired)
  }

  val t3a = "RADB    Net outgoing thermal radiation (MJ/m2/d)"
  passingTest should s"extract identifiers and units from t3a: ${t3a}" taggedAs(Somebody) in {
    val desired = Seq(
      "RADB" -> Seq("MJ/m2/d")
    )
    val mentions = extractMentions(t3a)
    testUnitEvent(mentions, desired)
  }


}
