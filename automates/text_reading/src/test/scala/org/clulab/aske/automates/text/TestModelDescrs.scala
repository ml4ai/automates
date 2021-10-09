package org.clulab.aske.automates.text

import org.clulab.aske.automates.TestUtils._

class TestModelDescrs extends ExtractionTest{

  val t1a = "SWAT incorporates a simple empirical model to predict the trophic status of water bodies."
  failingTest should s"extract descriptions from t1a: ${t1a}" taggedAs(Somebody) in {
    val desired = Seq(
      "SWAT" -> Seq("the trophic status of water bodies") // note: this test fails because "a simple empirical model" and the description is captured here too.
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

  val t3a = "we show first that the standard Susceptible-Infected-Removed (SIR) model cannot account for the patterns observed in various regions where the disease spread."
  failingTest should s"extract descriptions from t3a: ${t3a}" taggedAs(Somebody) in {
    val desired = Seq(
      "the standard Susceptible-Infected-Removed (SIR) model" -> Seq("account for the patterns observed in various regions where the disease spread")
    )
    val mentions = extractMentions(t3a)
    testModelLimitEvent(mentions, desired) // note: when the label for mention is "ModelLimitation", the test should be "testModelLimitEvent" instead of "testModelDescrsEvent"
    // TODO: it says that "List() did not contain element", even though the extraction is correct. need to discuss this with Masha.
  }
}
