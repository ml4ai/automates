package org.clulab.aske.automates.text

import org.clulab.aske.automates.TestUtils._
import org.clulab.aske.automates.OdinEngine.{FUNCTION_INPUT_ARG, MODEL_LABEL}

class TestFunctionFragments extends ExtractionTest {

  val t1 = "In subsection 4a, the remaining large-scale parameter is the depth of the mixed layer."
  passingTest should s"find function fragments from t1: ${t1}" taggedAs(Somebody) in {
    val desired = Map("input" -> Seq("depth of the mixed layer"))
    println("HERE")
    val mentions = extractMentions(t1)
    testUnaryEvent(mentions, "Function", FUNCTION_INPUT_ARG, desired)
  }

}