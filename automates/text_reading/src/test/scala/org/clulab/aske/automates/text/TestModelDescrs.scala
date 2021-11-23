package org.clulab.aske.automates.text

import org.clulab.aske.automates.TestUtils._

class TestModelDescrs extends ExtractionTest{

  // note: this test became failing after disabling three_capital_letters model rule
  val t1a = "SWAT incorporates a simple empirical model to predict the trophic status of water bodies."
  failingTest should s"extract descriptions from t1a: ${t1a}" taggedAs(Somebody) in {
    val desired = Seq(
      "SWAT" -> Seq("trophic status of water bodies"), // TODO: need to resolve generic model names later
      "simple empirical model"  -> Seq("trophic status of water bodies")
    )
    val mentions = extractMentions(t1a)
    testModelDescrsEvent(mentions, desired)
  }

  val t2a = "Our model also offers an opportunity to further decompose the different contributions to annual price variability."
  passingTest should s"extract descriptions from t2a: ${t2a}" taggedAs(Somebody) in {
    val desired = Seq(
      "Our model" -> Seq("opportunity to further decompose the different contributions to annual price variability")
    )
    val mentions = extractMentions(t2a)
    testModelDescrsEvent(mentions, desired)
  }

  val t3a = "We show first that the standard Susceptible-Infected-Removed (SIR) model cannot account for the patterns observed in various regions where the disease spread."
  passingTest should s"extract descriptions from t3a: ${t3a}" taggedAs(Somebody) in {
    val desired = Seq(
      "the standard Susceptible-Infected-Removed (SIR) model" -> Seq("account for the patterns observed in various regions where the disease spread")
    )
    val mentions = extractMentions(t3a)
    testModelLimitEvent(mentions, desired) // note: when the label for mention is "ModelLimitation", the test should be "testModelLimitEvent" instead of "testModelDescrsEvent"
  }
}
