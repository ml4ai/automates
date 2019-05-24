package org.clulab.aske.automates.data

import java.io.{File, PrintWriter}

import ai.lum.common.ConfigUtils._
import org.clulab.aske.automates.OdinEngine
import com.typesafe.config.{Config, ConfigFactory}
import scala.util.matching.Regex

trait Router {
  def route(text: String): OdinEngine
}

// todo: Masha/Andrew make some Routers
class TextRouter(val engines: Map[String, OdinEngine]) extends Router {
//  def route(text: String): OdinEngine = engines.head._2
  def route(text:String): OdinEngine = {
    val config: Config = ConfigFactory.load("automates")
    val period = "(\\.\\s|,\\s|\\.$)".r
//    val digits = "0123456789"
    //val numberOfPeriods = text.filter(c => period.contains(c)).length
    val numberOfPeriods = period.findAllIn(text).length

    //println("\nNumber of Periods: " + numberOfPeriods)
    val numberOfDigits = text.split(" ").filter(t => t.forall(_.isDigit)).length //checking if the token is a number
    val digitThreshold = 0.12
    val periodThreshold = 0.02 //for regular text, numberOfPeriods should be above the threshold

    //println("PERIODS / LEN: " + numberOfPeriods.toFloat / text.split(" ").length)
//    println("Text --> " + text)
    text match {
      case text if (numberOfPeriods.toFloat / text.split(" ").length > periodThreshold) => {
        println("USING TEXT ENGINE")
        //println(text + "\n")
        val engine = engines.get(TextRouter.TEXT_ENGINE)
        if (engine.isEmpty) throw new RuntimeException("You tried to use a text engine but the router doesn't have one")
        engine.get
      }
      case text if text.matches("\\d+\\..*") => {
        println("USING TEXT ENGINE for weird numbered cases")
        println(text + "\n")
        val engine = engines.get(TextRouter.TEXT_ENGINE)
        engine.get
      }
      case text if (numberOfPeriods.toFloat / text.split(" ").length < periodThreshold && numberOfDigits.toFloat / text.split(" ").length < digitThreshold) => {
        println("USING COMMENT ENGINE")
        //println(text + "\n")
        val engine = engines.get(TextRouter.COMMENT_ENGINE)
        engine.get
      }
      case _ => {
        println("USING TEXT ENGINE for lack of better option")
        //println(text + "\n")
        val engine = engines.get(TextRouter.TEXT_ENGINE)
        engine.get
      }
    }



    ///////START OF VAGUELY WORKING VERSION///////
//    if (numberOfPeriods.toDouble / text.split(" ").length > threshold) {
//      println("USING TEXT ENGINE")
//      println(text + "\n")
//      //val config: Config = ConfigFactory.load("automates")
//
//      //val textconfig: Config = config[Config]("TextEngine")
//      val engine = OdinEngine.fromConfig()
//      engine
//    } else {
//      println("USING COMMENT ENGINE")
//      println(text + "\n")
////      def this(config: Config = ConfigFactory.load("test")) = this(newOdinSystem(config[Config]("CommentEngine")))
//
//      val engine = OdinEngine.fromConfig(ConfigFactory.load("automates")[Config]("CommentEngine"))
//      engine
//    }
    ///////END OF VAGUELY WORKING VERSION///////

  }
}

object TextRouter {
  val TEXT_ENGINE = "text"
  val COMMENT_ENGINE = "comment"
}