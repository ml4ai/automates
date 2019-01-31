package org.clulab.aske.automates

import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.odin.Mention
import org.scalatest._
import org.clulab.aske.automates.OdinEngine._

object TestUtils {

  class TesterTag extends Tag("TesterTag")

  object Nobody   extends TesterTag
  object Somebody extends TesterTag
  object Andrew   extends TesterTag
  object Becky    extends TesterTag
  object Masha    extends TesterTag
  object Interval extends TesterTag

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

    //fixme -- when we move all Maps to Seqs: let's make the change here too
    def testDefinitionEvent(mentions: Seq[Mention], desired: Map[String, Seq[String]]): Unit = {
      testBinaryEvent(mentions, DEFINITION_LABEL, VARIABLE_ARG, DEFINITION_ARG, desired.toSeq)
    }

    //fixme -- when we move all Maps to Seqs: let's remove this overloaded version
    def testParameterSettingEvent(mentions: Seq[Mention], desired: Map[String, Seq[String]]): Unit = {
      testBinaryEvent(mentions, PARAMETER_SETTING_LABEL, VARIABLE_ARG, VALUE_ARG, desired.toSeq)
    }

    def testParameterSettingEvent(mentions: Seq[Mention], desired: Seq[(String, Seq[String])]): Unit = {
      testBinaryEvent(mentions, PARAMETER_SETTING_LABEL, VARIABLE_ARG, VALUE_ARG, desired)
    }

    // General Purpose

    def testTextBoundMention(mentions: Seq[Mention], eventType: String, desired: Seq[String]): Unit = {
      val found = mentions.filter(_ matches eventType).map(_.text)
      found.length should be(desired.size)

      desired.foreach(d => found should contain(d))
    }


    def testBinaryEvent(mentions: Seq[Mention], eventType: String, arg1Role: String, arg2Role: String, desired: Seq[(String, Seq[String])]): Unit = {
      val found = mentions.filter(_ matches eventType)
      found.length should be(desired.size)


      val grouped = found.groupBy(_.arguments(arg1Role).head.text) // we assume only one variable (arg1) arg!
      for {
        (desiredVar, desiredDefs) <- desired
        correspondingMentions = grouped.getOrElse(desiredVar, Seq())
      } testBinaryEventStrings(correspondingMentions, arg1Role, desiredVar, arg2Role, desiredDefs)
    }


    def testBinaryEventStrings(ms: Seq[Mention], arg1Role: String, arg1String: String, arg2Role: String, arg2Strings: Seq[String]) = {
      val variableDefinitionPairs = for {
        m <- ms
        a1 <- m.arguments.getOrElse(arg1Role, Seq()).map(_.text)
        a2 <- m.arguments.getOrElse(arg2Role, Seq()).map(_.text)
      } yield (a1, a2)

      arg2Strings.foreach(arg2String => variableDefinitionPairs should contain ((arg1String, arg2String)))
    }

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
