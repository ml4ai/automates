package org.clulab.aske.automates

import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.odin.Mention
import org.scalatest.{FlatSpec, Matchers}

object TestUtils {

  val successful = Seq()

  protected var mostRecentOdinEngine: Option[OdinEngine] = None

  // This is the standard way to extract mentions for testing
  def extractMentions(ieSystem: OdinEngine, text: String): Seq[Mention] = ieSystem.extractFromText(text, true, None)

  def newEidosSystem(config: Config): OdinEngine = this.synchronized {
    val eidosSystem =
      if (mostRecentOdinEngine.isEmpty) new OdinEngine(config)
      else if (mostRecentOdinEngine.get.config == config) mostRecentOdinEngine.get
      else new OdinEngine(config)

    mostRecentOdinEngine = Some(eidosSystem)
    eidosSystem
  }
  class Test extends FlatSpec with Matchers {
    val passingTest = it
    val failingTest = ignore
    val brokenSyntaxTest = ignore

  }

  class ExtractionTest(val ieSystem: OdinEngine) extends Test {
    def this(config: Config = ConfigFactory.load("test")) = this(newEidosSystem(config))

    def extractMentions(text: String): Seq[Mention] = TestUtils.extractMentions(ieSystem, text)

    // Event Specific

    def testDefinitionEvent(m: Mention, variable: String, definitions: Seq[String]) = {
      mentionHasArguments(m, "variable", Seq(variable))
      mentionHasArguments(m, "definition", definitions)
    }

    // General Purpose

    def mentionHasArguments(m: Mention, argName: String, argValues: Seq[String]): Unit = {
      // Check that the desired number of that argument were found
      val selectedArgs = m.arguments.getOrElse(argName, Seq())
      selectedArgs should have length(argValues.length)

      // Check that each of the arg values is found
      val argStrings = selectedArgs.map(_.text)
      argValues.foreach(argStrings should contain (_))
    }

  }

}
