package org.clulab.aske.automates.text

import edu.stanford.nlp.ie.machinereading.structure.EventMention
import org.clulab.aske.automates.TestUtils._

class TestFunctionFragments extends ExtractionTest {

  val t1 = "In subsection 4a, the remaining large-scale parameter is the depth of the mixed layer."
  failingTest should s"find function fragments from t1: ${t1}" taggedAs (Somebody) in {
    val desired = Seq("depth of the mixed layer")
    val mentions = extractMentions(t1)
    testUnaryEvent(mentions, "Function", "input", desired)
  }

  val t2 = "The only additional parameter appearing in the suggested formula is the extraterrestrial radiation, RA."
  passingTest should s"find function fragments from t2: ${t2}" taggedAs (Somebody) in {
    val desired = Seq("extraterrestrial radiation")
    val mentions = extractMentions(t2)
    testUnaryEvent(mentions, eventType = "Function", "input", desired)
  }

  val t3 = "Each day’s observations were averaged separately;"
  failingTest should s"find functions from t1m: ${t3}" taggedAs(Somebody) in {
    val desired = Seq("Each day's observations")
    val mentions = extractMentions(t3)
    testUnaryEvent(mentions, eventType = "Function", arg1Role = "input", desired)
  } // note: "Each" is not captured as a part of input as it is a determiner. Needs to fix this.

}
