package org.clulab.aske.automates.apps

import com.typesafe.config.{Config, ConfigFactory}

import java.io.File
import jline.console.ConsoleReader
import jline.console.history.FileHistory
import org.clulab.aske.automates.OdinEngine
import ai.lum.common.ConfigUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.utils.DisplayUtils._

object AutomatesShell extends App {

  val config = ConfigFactory.load()
  val ieSystem = OdinEngine.fromConfig(config[Config]("TextEngine"))

  val history = new FileHistory(new File(System.getProperty("user.home"), ".shellhistory"))
  sys addShutdownHook {
    history.flush() // we must flush the file before exiting
  }

  val reader = new ConsoleReader
  reader.setPrompt(">>> ")
  reader.setHistory(history)

  val commands = Map(
    "%help" -> "show commands",
    "%exit" -> "exit system"
  )

  println(s"\nWelcome to ReachShell!\n")
  printCommands()

  var running = true

  while (running) {
    reader.readLine match {
      case "%help" =>
        printCommands()

      case "%exit" | null =>
        running = false

      case text =>
        val doc = ieSystem.annotate(text)
        val mentions = ieSystem.extractFrom(doc)
        displayMentions(mentions, doc, true)
    }
  }

  // manual terminal cleanup
  reader.getTerminal().restore()
  reader.shutdown()


  // functions

  def printCommands(): Unit = {
    println("COMMANDS:")
    commands.foreach {
      case (cmd, msg) => println(s"\t$cmd\t=>\t$msg")
    }
  }


}