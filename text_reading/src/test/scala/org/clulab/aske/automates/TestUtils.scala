package org.clulab.aske.automates

import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.odin.Mention
import org.scalatest.{FlatSpec, Matchers}

object TestUtils {

  val successful = Seq()

  protected var mostRecentOdinEngine: Option[OdinEngine] = None

  // This is the standard way to extract mentions for testing
  def extractMentions(ieSystem: OdinEngine, text: String): Seq[Mention] = ieSystem.extractFromText(text, true, None)

  def newOdinSystem(config: Config): OdinEngine = this.synchronized {
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
    def this(config: Config = ConfigFactory.load("test")) = this(newOdinSystem(config))

    def extractMentions(text: String): Seq[Mention] = TestUtils.extractMentions(ieSystem, text)

    // Event Specific

    def testDefinitionEvent(mentions: Seq[Mention], desired: Map[String, Seq[String]]): Unit = {
      val definedVariables = mentions.filter(_ matches "Definition")
      definedVariables.length should be(desired.size)

      val grouped = definedVariables.groupBy(_.arguments("variable").head.text) // we assume only one variable arg!
      for {
        (desiredVar, desiredDefs) <- desired
        correspondingMentions = grouped.getOrElse(desiredVar, Seq())
      } testDefinitionEvent(correspondingMentions, desiredVar, desiredDefs)
    }

    def testDefinitionEvent(ms: Seq[Mention], variable: String, definitions: Seq[String]) = {
      val variableDefinitionPairs = for {
        m <- ms
        v <- m.arguments.getOrElse("variable", Seq()).map(_.text)
        d <- m.arguments.getOrElse("definition", Seq()).map(_.text)
      } yield (v, d)

      definitions.foreach(d => variableDefinitionPairs should contain ((variable, d)))
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
