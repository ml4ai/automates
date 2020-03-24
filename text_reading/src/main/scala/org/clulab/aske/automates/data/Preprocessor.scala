package org.clulab.aske.automates.data

trait Preprocessor {
  def cleanUp(text: String): String
}

class EdgeCaseParagraphPreprocessor() extends Preprocessor {
  //processes the text based on whether it is composed of sentences or phrases (i.e., prose vs. table of contents/figures, etc):
  //if a paragraph has too many numbers per token (#numbers/tokens in text > threshold), assume it's not prose and the numbers are page numbers; in that case, replace numbers with periods to create "sentences" instead of one long block of text to make it processable by the text engine; only do this for texts over 10 tokens long (heuristic).
    def cleanUp(text: String): String = {
    //follow up on combining the heading and the body of each section in the paper with "\n" in the DataLoader:
    //the heading and the body should be connected with a period if the body starts with a capital letter and space otherwise:
    val loseVerticalText = text.split("\n").filter(t => t.length > 6).mkString("\n")
    val cleanerText = loseVerticalText.replaceAll("\n(?=[A-Z])", ". ").replaceAll("\n", " ")
    val cleanerTextTokenized = cleanerText.split(" ")
    val numberOfNumbers = cleanerTextTokenized.filter(t => t.forall(_.isDigit)).length
    val numberProportion = numberOfNumbers.toFloat / cleanerTextTokenized.length
    val numberThreshold = 0.12
    cleanerText match {
      case cleanerText if (numberProportion > numberThreshold && cleanerTextTokenized.length > 10) => {
        val cleanedUpText = replaceSuspectedPageNumbers(cleanerText)
        cleanedUpText
      }
      case _ => {
        //todo: add other clean up, e.g., in-paragraph tables
        replaceEndOfTextPageNumber(cleanerText)}
    }
  }
  //replace on numbers in suspected non-prose sections
  def replaceSuspectedPageNumbers(text: String): String = text.replaceAll("\\d+\\.?", ". ")

  //if the text ends in a number and not period, that tends to be a page number
  def replaceEndOfTextPageNumber(text: String): String = text.replaceAll("\\d+$", ".")
}

object EdgeCaseParagraphPreprocessor {
  def apply(): EdgeCaseParagraphPreprocessor = new EdgeCaseParagraphPreprocessor()

}


class PassThroughPreprocessor() extends Preprocessor {
  def cleanUp(text: String): String = {
    val loseVerticalText = text.split("\n").filter(t => t.length > 6).mkString("\n")
    val cleanerText = loseVerticalText.replaceAll("\n", " ")
    cleanerText
  }
}

object PassThroughPreprocessor {
  def apply(): PassThroughPreprocessor = new PassThroughPreprocessor

}