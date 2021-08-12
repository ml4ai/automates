package org.clulab.aske.automates.text

import org.clulab.aske.automates.OdinEngine.CONTEXT_LABEL
import org.clulab.aske.automates.TestUtils._

class TestContext extends ExtractionTest{


  val t1 = "Simulations of crop development and growth for over 28 crops are possible, including the CERES family of models for maize and sorghum and the CROPGRO family of models for soybean and cotton."
  failingTest should s"extract model names from t1: ${t1}" taggedAs (Somebody) in {

    val desired = Seq("over 28 crops", "maize", "sorghum", "soybean", "cotton") //fixme: how to filter out "CROPGRO family of models"?
    val mentions = extractMentions(t1)
    testTextBoundMention(mentions, CONTEXT_LABEL, desired)
  }
}
