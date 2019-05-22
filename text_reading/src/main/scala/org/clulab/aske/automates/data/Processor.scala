package org.clulab.aske.automates.data

trait Preprocessor {
  def cleanUp(text: String): String
}

class EdgeCaseParagraphPreprocessor(text: String) extends Preprocessor {
  def cleanUp(text: String): String = {
    val digits = "0123456789"
    val numberOfDigits = text.filter(c => digits.contains(c)).length
    val digitThreshold = 0.4
    text match {
      case text if numberOfDigits.toDouble / text.split(" ").length > digitThreshold => {
        val cleanedUpText = text.replaceAll("\\d+", ".")
        cleanedUpText
      }
      case _ => text //todo: add other clean up, e.g., in-paragraph tables
    }
  }
}

object EdgeCaseParagraphPreprocessor {
  val preProc = new EdgeCaseParagraphPreprocessor

}


class PassThroughPreprocessor() extends Preprocessor {
  def cleanUp(text: String): String = {
    text
  }
}

object PassThroughPreprocessor {
  def apply(): PassThroughPreprocessor = new PassThroughPreprocessor

}