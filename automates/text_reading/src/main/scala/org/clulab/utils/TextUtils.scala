package org.clulab.utils

import java.io.IOException

import org.clulab.aske.automates.attachments.AutomatesAttachment
import org.clulab.odin.Mention
import org.clulab.aske.automates.apps._
import org.slf4j.{Logger, LoggerFactory}

import scala.collection.mutable.ArrayBuffer


object TextUtils {
  /**stores methods related to text mention extraction*/
  protected lazy val logger: Logger = LoggerFactory.getLogger(this.getClass)

def getMentionText(mention: Mention): String = {

  // get mention text taking into accout the presence of discontinuous character offset attachment
  if (mention.attachments.nonEmpty & mention.attachments.exists(att => att.asInstanceOf[AutomatesAttachment].toUJson("attType").str == "DiscontinuousCharOffset")) {
    val attAsJson = ExtractAndAlign.returnAttachmentOfAGivenType(mention.attachments, "DiscontinuousCharOffset").toUJson
    val charOffsets = attAsJson("charOffsets").arr.map(v => (v.arr.head.num.toInt, v.arr.last.num.toInt))
    val textPieces = new ArrayBuffer[String]()
    val fullDocText =  try {
      mention.document.text.get
    } catch {
      case e: IOException => throw new RuntimeException("Document text missing; try extracting mentions with keepText set to true")
    }

    for (offset <- charOffsets) {
      textPieces.append(fullDocText.slice(offset._1, offset._2).mkString(""))
    }

   textPieces.mkString(" ")

  } else {
    mention.text
  }
}


}


