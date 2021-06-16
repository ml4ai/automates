package org.clulab.aske.automates

import ai.lum.common.ConfigUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.odin.Mention
import org.scalatest._
import org.clulab.aske.automates.OdinEngine._
import org.clulab.aske.automates.apps.ExtractAndAlign.whereIsGlobalVar
import org.clulab.processors.Document
import org.clulab.serialization.json.JSONSerializer
import org.clulab.utils.TextUtils
import org.json4s.jackson.JsonMethods._
import ujson.Value

import scala.collection.mutable.ArrayBuffer

object TestUtils {

  // From Processors -- I couldn't import it for some reason
  def jsonStringToDocument(jsonstr: String): Document = JSONSerializer.toDocument(parse(jsonstr))

  class TesterTag extends Tag("TesterTag")

  object Nobody   extends TesterTag
  object Somebody extends TesterTag
  object Andrew   extends TesterTag
  object Becky    extends TesterTag
  object Masha    extends TesterTag
  object Interval extends TesterTag
  object DiscussWithModelers extends TesterTag // i.e., Clay and Adarsh

  val successful = Seq()

  protected var mostRecentOdinEngine: Option[OdinEngine] = None
  protected var mostRecentConfig: Option[Config] = None

  // This is the standard way to extract mentions for testing
  def extractMentions(ieSystem: OdinEngine, text: String): Seq[Mention] = {
    ieSystem.extractFromText(text, true, None)
  }

  def newOdinSystem(config: Config): OdinEngine = this.synchronized {
    val readingSystem =
      if (mostRecentOdinEngine.isEmpty) OdinEngine.fromConfig(config)
      else if (mostRecentConfig.get == config) mostRecentOdinEngine.get
      else OdinEngine.fromConfig(config)

    mostRecentOdinEngine = Some(readingSystem)
    mostRecentConfig = Some(config)
    readingSystem
  }

  class Test extends FlatSpec with Matchers {
    val passingTest = it
    val failingTest = ignore
    val brokenSyntaxTest = ignore
    val toDiscuss = ignore

  }

  class ExtractionTest(val ieSystem: OdinEngine) extends Test {
    def this(config: Config = ConfigFactory.load("test")) = this(newOdinSystem(config[Config]("TextEngine")))

    def extractMentions(text: String): Seq[Mention] = TestUtils.extractMentions(ieSystem, text)

    // Event Specific

    def testDescriptionEvent(mentions: Seq[Mention], desired: Seq[(String, Seq[String])]): Unit = {
      testBinaryEvent(mentions, DESCRIPTION_LABEL, VARIABLE_ARG, DESCRIPTION_ARG, desired)
    }

    def testFunctionEvent(mentions: Seq[Mention], desired: Seq[(String, Seq[String])]): Unit = {
      testBinaryEvent(mentions, FUNCTION_LABEL, FUNCTION_OUTPUT_ARG, FUNCTION_INPUT_ARG, desired)
    }

    def testUnitEvent(mentions: Seq[Mention], desired: Seq[(String, Seq[String])]): Unit = {
      testBinaryEvent(mentions, UNIT_LABEL, VARIABLE_ARG, UNIT_ARG, desired)
    }

    def testParameterSettingEvent(mentions: Seq[Mention], desired: Seq[(String, Seq[String])]): Unit = {
      testBinaryEvent(mentions, PARAMETER_SETTING_LABEL, VARIABLE_ARG, VALUE_ARG, desired)
    }

    def testParameterSettingEventInterval(mentions: Seq[Mention], desired: Seq[(String, Seq[String])]): Unit = {
      testThreeArgEvent(mentions, INTERVAL_PARAMETER_SETTING_LABEL, VARIABLE_ARG, VALUE_LEAST_ARG, VALUE_MOST_ARG, desired)
    }

    // General Purpose

    def testTextBoundMention(mentions: Seq[Mention], eventType: String, desired: Seq[String]): Unit = {
      val found = mentions.filter(_ matches eventType).map(_.text)
      found.length should be(desired.size)

      desired.foreach(d => found should contain(d))
    }

    //used for parameter setting tests where the setting is an interval
    def testThreeArgEvent(mentions: Seq[Mention], eventType: String, arg1Role: String, arg2Role: String, arg3Role: String, desired: Seq[(String, Seq[String])]): Unit = {
      val found = mentions.filter(_ matches eventType)
      found.length should be(desired.size)
      //todo add func to check args and not only the size

      val grouped = found.groupBy(_.arguments(arg1Role).head.text)
      // we assume only one variable (arg1) arg!
      for {
        (desiredVar, desiredParameters) <- desired
        correspondingMentions = grouped.getOrElse(desiredVar, Seq())
      } testThreeArgEventString(correspondingMentions, arg1Role, desiredVar, arg2Role, desiredParameters.head, arg3Role, desiredParameters.last)

    }

    def testBinaryEvent(mentions: Seq[Mention], eventType: String, arg1Role: String, arg2Role: String, desired: Seq[(String, Seq[String])]): Unit = {
      val found = mentions.filter(_ matches eventType)
      found.length should be(desired.size)



      val grouped = found.groupBy(_.arguments(arg1Role).head.text) // we assume only one variable (arg1) arg!
      for {
        (desiredVar, desiredDescrs) <- desired
        correspondingMentions = grouped.getOrElse(desiredVar, Seq())
      } testBinaryEventStrings(correspondingMentions, arg1Role, desiredVar, arg2Role, desiredDescrs)
    }


    def testBinaryEventStrings(ms: Seq[Mention], arg1Role: String, arg1String: String, arg2Role: String, arg2Strings: Seq[String]) = {
      val identifierDescriptionPairs = for {
        m <- ms
        a1 <- m.arguments.getOrElse(arg1Role, Seq()).map(TextUtils.getMentionText(_))
        a2 <- m.arguments.getOrElse(arg2Role, Seq()).map(TextUtils.getMentionText(_))
      } yield (a1, a2)

      arg2Strings.foreach(arg2String => identifierDescriptionPairs should contain ((arg1String, arg2String)))
    }

    //used for parameter setting tests where the setting is an interval
    def testThreeArgEventString(ms: Seq[Mention], arg1Role: String, arg1String: String, arg2Role: String, arg2String: String, arg3Role: String, arg3String: String): Unit = {
      val varMinMaxSettings = for {
        m <- ms
        a1 <- m.arguments.getOrElse(arg1Role, Seq()).map(_.text)
        a2 <- m.arguments.getOrElse(arg2Role, Seq()).map(_.text)
        a3 <- m.arguments.getOrElse(arg3Role, Seq()).map(_.text)
      } yield (a1, a2, a3)

      varMinMaxSettings should contain ((arg1String, arg2String, arg3String))
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

  class ExtractionFromCommentsTest(val ieSystem: OdinEngine) extends Test {
    def this(config: Config = ConfigFactory.load("test")) = this(newOdinSystem(config[Config]("CommentEngine")))

    def extractMentions(text: String): Seq[Mention] = TestUtils.extractMentions(ieSystem, text)

    // Event Specific

    def testDescriptionEvent(mentions: Seq[Mention], desired: Seq[(String, Seq[String])]): Unit = {
      testBinaryEvent(mentions, DESCRIPTION_LABEL, VARIABLE_ARG, DESCRIPTION_ARG, desired)
    }

    def testFunctionEvent(mentions: Seq[Mention], desired: Seq[(String, Seq[String])]): Unit = {
      testBinaryEvent(mentions, FUNCTION_LABEL, FUNCTION_OUTPUT_ARG, FUNCTION_INPUT_ARG, desired)
    }

    def testUnitEvent(mentions: Seq[Mention], desired: Seq[(String, Seq[String])]): Unit = {
      testBinaryEvent(mentions, UNIT_LABEL, VARIABLE_ARG, UNIT_ARG, desired)
    }

    def testParameterSettingEvent(mentions: Seq[Mention], desired: Seq[(String, Seq[String])]): Unit = {
      testBinaryEvent(mentions, PARAMETER_SETTING_LABEL, VARIABLE_ARG, VALUE_ARG, desired)
    }

    def testParameterSettingEventInterval(mentions: Seq[Mention], desired: Seq[Seq[String]]): Unit = {
      testThreeArgEvent(mentions, INTERVAL_PARAMETER_SETTING_LABEL, VARIABLE_ARG, VALUE_LEAST_ARG, VALUE_MOST_ARG, desired)
    }

    // General Purpose

    def testTextBoundMention(mentions: Seq[Mention], eventType: String, desired: Seq[String]): Unit = {
      val found = mentions.filter(_ matches eventType).map(_.text)
      found.length should be(desired.size)

      desired.foreach(d => found should contain(d))
    }


    def testThreeArgEvent(mentions: Seq[Mention], eventType: String, arg1Role: String, arg2Role: String, arg3Role: String, desired: Seq[Seq[String]]): Unit = {
      val found = mentions.filter(_ matches eventType)
      found.length should be(desired.size)

    }

    def testBinaryEvent(mentions: Seq[Mention], eventType: String, arg1Role: String, arg2Role: String, desired: Seq[(String, Seq[String])]): Unit = {
      val found = mentions.filter(_ matches eventType)
      found.length should be(desired.size)


      val grouped = found.groupBy(_.arguments(arg1Role).head.text) // we assume only one variable (arg1) arg!
      for {
        (desiredVar, desiredDescrs) <- desired
        correspondingMentions = grouped.getOrElse(desiredVar, Seq())
      } testBinaryEventStrings(correspondingMentions, arg1Role, desiredVar, arg2Role, desiredDescrs)
    }


    def testBinaryEventStrings(ms: Seq[Mention], arg1Role: String, arg1String: String, arg2Role: String, arg2Strings: Seq[String]) = {
      val identifierDescriptionPairs = for {
        m <- ms
        a1 <- m.arguments.getOrElse(arg1Role, Seq()).map(_.text)
        a2 <- m.arguments.getOrElse(arg2Role, Seq()).map(_.text)
      } yield (a1, a2)

      arg2Strings.foreach(arg2String => identifierDescriptionPairs should contain ((arg1String, arg2String)))
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

  // Alignment testing utils
  def getLinksWithIdentifierStr(identifierName: String, allLinks: Seq[Value], inclId: Boolean): Seq[Value] = {

    // when searching all links, can't include element uid, but when we search off of intermediate node (e.g., comment identifier when searching for gvar to src code alignment for testing, have to use uid
    val toReturn = if (inclId) {
      allLinks.filter(l => l.obj("element_1").str == identifierName || l.obj("element_2").str == identifierName)
    } else {
      allLinks.filter(l => l.obj("element_1").str.split("::").last == identifierName || l.obj("element_2").str.split("::").last == identifierName)

    }
    toReturn
  }

  // todo: double-check returning the right number of indirect alignments per intermediate node
  // return indirect links of a given type as a list of strings per each intermediate node
  def findIndirectLinks(allDirectVarLinks: Seq[Value], allLinks: Seq[Value], linkTypeToBuildOffOf: String, indirectLinkType: String, nIndirectLinks: Int): Map[String, Seq[String]] = {//Map[String, Map[String, ArrayBuffer[Value]]] = {
    val indirectLinkEndNodes = new ArrayBuffer[String]()
    val allIndirectLinks = new ArrayBuffer[Value]()
    // we have links for some var, e.g., I(t)
    // through one of the existing links, we can get to another type of node
    // probably already sorted - double-check
    val topNDirectLinkOfTargetTypeSorted = allDirectVarLinks.filter(_.obj("link_type").str==linkTypeToBuildOffOf).sortBy(_.obj("score").num).reverse.slice(0, nIndirectLinks)
    for (tdl <- topNDirectLinkOfTargetTypeSorted) {
      println("dir link: " + tdl)
    }
    val sortedIntermNodeNames = new ArrayBuffer[String]()

    //
    for (dl <- topNDirectLinkOfTargetTypeSorted) {
      println("---")
      // get intermediate node of indirect link - for comment_to_gvar link, it's element_1
      val intermNodeJustName = linkTypeToBuildOffOf match {
        case "comment_to_gvar" => dl("element_1").str
        case _ => ???
      }
      sortedIntermNodeNames.append(intermNodeJustName)

      //
      val indirectLinksForIntermNode = getLinksWithIdentifierStr(intermNodeJustName, allLinks, true).filter(_.obj("link_type").str == indirectLinkType)//.sortBy(_.obj("score")).reverse
      for (il <- indirectLinksForIntermNode) {

        allIndirectLinks.append(il)
        println("indir links per interm node: " + il)
      }

    }


    // return only the ones of the given type
    val groupedByElement2 = allIndirectLinks.groupBy(_.obj("element_2").str)
    for (g <- groupedByElement2) {
      println("G: " + g._1)
      for (i <- g._2) {
        println("=>" + i)
      }
    }
    println("???")
    val maxLinksPerIntermNode = groupedByElement2.maxBy(_._2.length)._2.length

    println("???????")
    for (i <- 0 until maxLinksPerIntermNode) {
      for (j <- 0 until sortedIntermNodeNames.length) {
        val intermNodeName = sortedIntermNodeNames(j)

        val endNode = groupedByElement2(intermNodeName).map(_.obj("element_1").str)
        if (endNode.length > i) {
          indirectLinkEndNodes.append(endNode(i))
        }

      }
    }

    for (i <- indirectLinkEndNodes) println("END NODE: " + i)


    //    Map(indirectLinkType -> groupedByElement2)
    Map(indirectLinkType -> indirectLinkEndNodes)
  }

  def printGroupedLinksSorted(links: Map[String, Seq[Value]]): Unit = {
    for (gr <- links) {
      for (i <- gr._2.sortBy(_.obj("score").num).reverse) {
        println(i)
      }
      println("----------")
    }
  }

  def printIndirectLinks(indirectLinks: Map[String, Seq[String]]): Unit = {
    for (l <- indirectLinks) {
      println("link type: " + l._1)
      println("linked nodes: " + l._2.mkString(" :: "))
    }
  }

  def getLinksForGvar(idfr: String, allLinks: Seq[Value]): (Map[String, Seq[Value]], Map[String, Seq[String]]) = {

    println("IDFR: " + idfr)
    // links are returned as maps from link types to a) full links for direct links and b) sequences of elements linked indirectly to the global var
    // sorted by score based on the two edges in the indirect link
    // all links that contain the target text global var string
    // and only the links that contain global vars
    val allDirectLinksForIdfr = getLinksWithIdentifierStr(idfr, allLinks, false).filter(link => whereIsGlobalVar.contains(link.obj("link_type").str))

    // filtering out the links with no idfr with the correct idf; can't have the link uid in the test itself bc those
    // are randomly generated on every run
    // this has to be one of the links with global variable
    val oneLink = allDirectLinksForIdfr.head
    val linkType = oneLink("link_type").str
    val whichElement = whereIsGlobalVar(linkType)
    val fullIdfrUid = oneLink(whichElement).str
    println("full idfr uid: " + fullIdfrUid)
    val onlyWithCorrectIdfr = allDirectLinksForIdfr.filter(link => link(whereIsGlobalVar(link("link_type").str)).str ==
      fullIdfrUid)
    // group those by link type - in testing, will just be checking the rankings of links of each type
    val directLinksGroupedByLinkType = onlyWithCorrectIdfr.groupBy(_.obj("link_type").str)
    // take the first available link and, depending on the type, get the full name from the correct element
    // (element_1 or element_2)

    for (l <- directLinksGroupedByLinkType) {
      // todo: here need to filter out the links that do not have the exact identifier we are looking at,
      //eg for eq to gvar link, filter out the links where the idfr exact match is in element 1 instead of 2
      println("---")
      for (i <- l._2.sortBy(el => el("score").num).reverse) println("-+> " + i)
    }

    val indirectLinks = if (directLinksGroupedByLinkType.contains("comment_to_gvar")) {
      findIndirectLinks(onlyWithCorrectIdfr, allLinks, "comment_to_gvar", "source_to_comment", 3)

    } else null
    // get indirect links; currently, it's only source to comment links aligned through comment (comment var is the intermediate node)

    println("dir link len: " + directLinksGroupedByLinkType.keys.toList.length)
    (directLinksGroupedByLinkType, indirectLinks)
  }


}
