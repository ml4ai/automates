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
class TextRouter(val engines: Seq[(String, OdinEngine)]) extends Router {
//  def route(text: String): OdinEngine = engines.head._2
  def route(text:String): OdinEngine = {
    val config: Config = ConfigFactory.load("automates")
    val period = "."
    val digits = "0123456789"
    val numberOfPeriods = text.filter(c => period.contains(c)).length
    val numberOfDigits = text.filter(c => digits.contains(c)).length
    val periodThreshold = 0.01 //for regular text, numberOfPeriods should be above the threshold
    val digitThreshold = 0.4
//    println("Text --> " + text)
    text match {
      case text if (numberOfPeriods.toDouble / text.split(" ").length > periodThreshold) => {
        println("\n")
        //println("USING TEXT ENGINE")
        //println(text + "\n")
        val engine = OdinEngine.fromConfig()
        engine
      }
      case text if text.matches("\\d+\\..*") => {
        println("\n")
        //println("USING TEXT ENGINE for weird numbered cases")
        //println(text + "\n")
        val engine = OdinEngine.fromConfig()
        engine
      }
      case text if (numberOfPeriods.toDouble / text.split(" ").length < periodThreshold && numberOfDigits.toDouble / text.split(" ").length < digitThreshold) => {
        println("\n")
        //println("USING COMMENT ENGINE")
        //println(text + "\n")
        val engine = OdinEngine.fromConfig(ConfigFactory.load("automates")[Config]("CommentEngine"))
        engine
      }
      case _ => {
        println("\n")
        //println("USING TEXT ENGINE for lack of better option")
        //println(text + "\n")
        val engine = OdinEngine.fromConfig()
        engine}
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