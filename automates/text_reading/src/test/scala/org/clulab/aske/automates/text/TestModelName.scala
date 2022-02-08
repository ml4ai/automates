package org.clulab.aske.automates.text

import org.clulab.aske.automates.TestUtils._
import org.clulab.aske.automates.OdinEngine.MODEL_LABEL

class TestModelName extends ExtractionTest {

  val t1 = "In the SEIRP model, there is no latency for the disease B."
  passingTest should s"extract model names from t1: ${t1}" taggedAs (Somebody) in {
    val desired = Seq("SEIRP model")
    val mentions = extractMentions(t1)
    testTextBoundMention(mentions, MODEL_LABEL, desired)
  }

  val t2 = "The CHIME (COVID-19 Hospital Impact Model for Epidemics) App is designed to assist hospitals and public " +
    "health officials"
  passingTest should s"extract model names from t2: ${t2}" taggedAs (Somebody) in {
    val desired = Seq("CHIME", "COVID-19 Hospital Impact Model") //fixme: maybe the second one should not be found
    val mentions = extractMentions(t2)
    testTextBoundMention(mentions, MODEL_LABEL, desired)
  }

  val t3 = "Since the rate of new infections in the SIR model is ..."
  passingTest should s"extract model names from t3: ${t2}" taggedAs (Somebody) in {
    val desired = Seq("SIR model")
    val mentions = extractMentions(t3)
    testTextBoundMention(mentions, MODEL_LABEL, desired)
  }
}