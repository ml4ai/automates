package org.clulab.aske.automates.data

import java.io.{File, PrintWriter}

import ai.lum.common.ConfigUtils._
import org.clulab.aske.automates.OdinEngine
import com.typesafe.config.{Config, ConfigFactory}

trait Router {
  def route(text: String): OdinEngine
}

// todo: Masha/Andrew make some Routers
class TextRouter(val engines: Seq[(String, OdinEngine)]) extends Router {
//  def route(text: String): OdinEngine = engines.head._2
  def route(text:String): OdinEngine = {
    val config: Config = ConfigFactory.load("automates")
    val period = "."
    val numberOfPeriods = text.filter(c => period.contains(c)).length
    val threshold = 0.01

    if (numberOfPeriods.toDouble / text.split(" ").length > threshold) {
      println("USING TEXT ENGINE")
      println(text + "\n")
      //val config: Config = ConfigFactory.load("automates")

      //val textconfig: Config = config[Config]("TextEngine")
      val engine = OdinEngine.fromConfig()
      engine
    } else {
      println("USING COMMENT ENGINE")
      println(text + "\n")
//      def this(config: Config = ConfigFactory.load("test")) = this(newOdinSystem(config[Config]("CommentEngine")))

      val engine = OdinEngine.fromConfig(ConfigFactory.load("automates")[Config]("CommentEngine"))
      engine
    }

  }
}