package org.clulab.aske.automates.data

import org.clulab.aske.automates.OdinEngine
import com.typesafe.config.{Config, ConfigFactory}

trait Router {
  def route(text: String): OdinEngine
}


class TextRouter(val engines: Map[String, OdinEngine]) extends Router {
  //returns the appropriate OdinEngine (currently either TextEngine or CommentEngine) for the given text based on the amount of sentence punctuation (commas and end-of-sentence-like periods---with the assumption that those will be indicative of prose) and the amount of numbers in the text (the texts with a high # of numbers are likely non-prose, e.g., a table of contents, and are to be processed with a textEngine with additional preprocessing).
  def route(text:String): OdinEngine = {
    val config: Config = ConfigFactory.load("automates")
    val sentencePunct = "(\\.\\s|,\\s|\\.$)".r
    val amountOfPunct = sentencePunct.findAllIn(text).length
    val numberOfNumbers = text.split(" ").filter(t => t.forall(_.isDigit)).length //checking if the token is a number
    val digitThreshold = 0.12
    val periodThreshold = 0.02 //for regular text, amountOfPunct should be above the threshold
    val punctProportion = amountOfPunct.toFloat / text.split(" ").length
    val numberProportion = numberOfNumbers.toFloat / text.split(" ").length

    text match {
      case text if (punctProportion > periodThreshold) => {
        //sentence-like punctuation present --> TextEngine
        val engine = engines.get(TextRouter.TEXT_ENGINE)
        if (engine.isEmpty) throw new RuntimeException("You tried to use a text engine but the router doesn't have one")
        engine.get
      }
      case text if text.matches("\\d+\\..*") => {
        //use TextEngine for texts starting with \d\. --- the periods in numbered lists successfully break the text into "sentences". This case might be redundant.
        val engine = engines.get(TextRouter.TEXT_ENGINE)
        if (engine.isEmpty) throw new RuntimeException("You tried to use a text engine but the router doesn't have one")
        engine.get
      }
      case text if (punctProportion < periodThreshold && numberProportion < digitThreshold) => {
        //not much punctuation and not too many numbers --> CommentEngine
        val engine = engines.get(TextRouter.COMMENT_ENGINE)
        if (engine.isEmpty) throw new RuntimeException("You tried to use a text engine but the router doesn't have one")
        engine.get
      }
      case _ => {
        //use TextEngine for all other cases (more cases may come up)
        val engine = engines.get(TextRouter.TEXT_ENGINE)
        if (engine.isEmpty) throw new RuntimeException("You tried to use a text engine but the router doesn't have one")
        engine.get
      }
    }
  }
}

object TextRouter {
  val TEXT_ENGINE = "text"
  val COMMENT_ENGINE = "comment"
}