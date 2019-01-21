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

//    class GraphTester(text: String) extends graph.GraphTester(ieSystem, text)
//
//    class RuleTester(text: String) extends rule.RuleTester(ieSystem, text)

    def extractMentions(text: String): Seq[Mention] = TestUtils.extractMentions(ieSystem, text)

  }

}
