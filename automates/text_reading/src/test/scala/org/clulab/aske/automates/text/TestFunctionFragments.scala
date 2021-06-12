package org.clulab.aske.automates.text

import edu.stanford.nlp.ie.machinereading.structure.EventMention
import org.clulab.aske.automates.TestUtils._

class TestFunctionFragments extends ExtractionTest {

  val t1 = "In subsection 4a, the remaining large-scale parameter is the depth of the mixed layer."
  failingTest should s"find function fragments from t1: ${t1}" taggedAs(Somebody) in {
    val desired = Seq(
      "input" -> Seq("depth of the mixed layer")
    )
    val mentions = extractMentions(t1)
    testFragmentEvent(mentions, eventType = "Function", desired)
  }

  val t2 = "The only additional parameter appearing in the suggested formula is the extraterrestrial radiation, RA."
  failingTest should s"find function fragments from t2: ${t2}" taggedAs(Somebody) in {
    val desired = Seq(
      "input" -> Seq("extraterrestrial radiation")
    )
    val mentions = extractMentions(t2)
    testFragmentEvent(mentions, eventType = "Function", desired)
  }

}