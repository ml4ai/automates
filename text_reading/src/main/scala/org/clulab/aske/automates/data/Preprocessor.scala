package org.clulab.aske.automates.data

trait Preprocessor {
  def cleanUp(text: String): String
}

class EdgeCaseParagraphPreprocessor() extends Preprocessor {
  def cleanUp(text: String): String = {
//    val digits = "0123456789"
    val cleanerText = text.replaceAll("\n(?=[A-Z])", ". ").replaceAll("\n", " ")
    val numberOfDigits = cleanerText.split(" ").filter(t => t.forall(_.isDigit)).length
    val numbers = cleanerText.split(" ").filter(t => t.forall(_.isDigit)).mkString(" ")
    //println("TOKENS: " + cleanerText.split(" ").mkString("-S-"))
    println("NUMBERS: " + numbers)
    val digitThreshold = 0.12
    cleanerText match {
      case cleanerText if numberOfDigits.toFloat / cleanerText.split(" ").length > digitThreshold => {
        println("Filtering bc the value is: " + numberOfDigits.toFloat / cleanerText.split(" ").length )
        val cleanedUpText = cleanerText.replaceAll("\\d+\\.?", ". ")
        cleanedUpText.replaceAll("\\d+$", ".")
      }
      case _ => {
        println("NOT filtering bc the value is: " + numberOfDigits.toFloat / cleanerText.split(" ").length )
        cleanerText.replaceAll("\\d+$", ".")} //todo: add other clean up, e.g., in-paragraph tables
    }
  }
}

object EdgeCaseParagraphPreprocessor {
  def apply(): EdgeCaseParagraphPreprocessor = new EdgeCaseParagraphPreprocessor()

}


class PassThroughPreprocessor() extends Preprocessor {
  def cleanUp(text: String): String = {
    text
  }
}

object PassThroughPreprocessor {
  def apply(): PassThroughPreprocessor = new PassThroughPreprocessor

}