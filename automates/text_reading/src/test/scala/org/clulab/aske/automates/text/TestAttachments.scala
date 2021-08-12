package org.clulab.aske.automates.text

import org.clulab.aske.automates.OdinEngine.{CONJ_DESCRIPTION_LABEL, CONJ_DESCRIPTION_TYPE2_LABEL, DESCRIPTION_LABEL}
import org.clulab.aske.automates.TestUtils._

class TestAttachments extends ExtractionTest{


  val t1 = "C and C* are heat transfer coefficient that depend on the reference height selected for T and u, and on the stability if this height is not low enough."
  passingTest should s"extract mentions with context attachments from t1: ${t1}" taggedAs (Somebody) in {

    val mentions = extractMentions(t1)
    val found = mentions.filter(_ matches CONJ_DESCRIPTION_LABEL)
    found.foreach(f => testIfHasAttachment(f))
    testIfHasAttachmentType(found, "ContextAtt")
  }

  val t2 = "C and C* are heat transfer coefficient and cat coefficient that depend on the reference height selected for T and u, and on the stability if this height is not low enough."
  passingTest should s"extract mentions with context attachments from t2: ${t2}" taggedAs (Somebody) in {

    val mentions = extractMentions(t2)
    val found = mentions.filter(_ matches CONJ_DESCRIPTION_TYPE2_LABEL)
    found.foreach(f => testIfHasAttachment(f))
    testIfHasAttachmentType(found, "ContextAtt")
  }
}
