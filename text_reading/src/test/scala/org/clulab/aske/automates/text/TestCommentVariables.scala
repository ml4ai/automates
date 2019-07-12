package org.clulab.aske.automates.text

import org.clulab.aske.automates.OdinEngine.VARIABLE_LABEL
import org.clulab.aske.automates.TestUtils._

class TestCommentVariables extends ExtractionFromCommentsTest {

  val t1 = "EEQ is equilibrium evaporation (mm/d)"
  passingTest should s"extract variables from t1: ${t1}" taggedAs(Somebody) in {


    val desired = Seq("EEQ")
    val mentions = extractMentions(t1)
    testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }


  val t2 = "11/04/1993 NBP Modified"
  passingTest should s" NOT extract variables from t2: ${t2}" taggedAs(Somebody) in {


    val desired = Seq()  // this is from revision history; do we eliminate these in preprocessing? Can probably make a neg lookbehind for date format? but can keep the test in case it gets in as a sentence
    val mentions = extractMentions(t2)
    testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }


  //From PET.for that I got from Paul---the sample in github repo does not have multiline var definitions
  val t3 = "S is the rate of change of saturated vapor pressure of air with           temperature (Pa/K)"
  passingTest should s"extract variables from t3: ${t3}" taggedAs(Somebody) in {


    val desired = Seq("S")  // this is from revision history; do we eliminate these in preprocessing? Can probably make a neg lookbehind for date format? but can keep the test in case it gets in as a sentence
    val mentions = extractMentions(t3)
    testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }

}
