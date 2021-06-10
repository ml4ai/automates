package org.clulab.aske.automates.text

import org.clulab.aske.automates.TestUtils._
import org.clulab.aske.automates.OdinEngine.{FUNCTION_INPUT_ARG, MODEL_LABEL}

class TestFunctionFragments extends ExtractionTest {

  val t1 = "In subsection 4a, the remaining large-scale parameter is the depth of the mixed layer."
  failingTest should s"find function fragments from t1: ${t1}" taggedAs(Somebody) in {
    val desired = Seq("depth of the mixed layer")
    val mentions = extractMentions(t1)
    testUnaryEvent(mentions, "EventMention", FUNCTION_INPUT_ARG, desired)
  }

}