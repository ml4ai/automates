package org.clulab.aske.automates

import ai.lum.common.ConfigUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.odin.Mention
import org.scalatest._
import org.clulab.aske.automates.OdinEngine._
import org.clulab.aske.automates.apps.{AlignmentBaseline, ExtractAndAlign}
import org.clulab.aske.automates.apps.ExtractAndAlign.{GLOBAL_VAR_TO_UNIT_VIA_CONCEPT, allLinkTypes, whereIsGlobalVar, whereIsNotGlobalVar}
import org.clulab.aske.automates.attachments.AutomatesAttachment
import org.clulab.processors.Document
import org.clulab.serialization.json.JSONSerializer
import org.clulab.utils.MentionUtils
import org.json4s.jackson.JsonMethods._
import play.libs.F.Tuple
import ujson.Value

import scala.collection.mutable.ArrayBuffer
import scala.util.Try

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
  val extractorAligner = ExtractAndAlign

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

    def testModelDescrsEvent(mentions: Seq[Mention], desired: Seq[(String, Seq[String])]): Unit = {
      testBinaryEvent(mentions, MODEL_DESCRIPTION_LABEL, MODEL_NAME_ARG, MODEL_DESCRIPTION_ARG, desired)
    }

    def testModelLimitEvent(mentions: Seq[Mention], desired: Seq[(String, Seq[String])]): Unit = {
      testBinaryEvent(mentions, MODEL_LIMITATION_LABEL, MODEL_NAME_ARG, MODEL_DESCRIPTION_ARG, desired)
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

    def withinOneSentenceTest(mentions: Seq[Mention]): Unit = {
      // makes sure all the args of a mentioned are contained within one sentence (note: not same for cross-sentence mentions)
      for (m <- mentions) {
        for (arg <- m.arguments) {
          arg._2.head.sentence shouldEqual m.sentence
        }
      }
    }

    def testTextBoundMention(mentions: Seq[Mention], eventType: String, desired: Seq[String]): Unit = {
      val found = mentions.filter(_ matches eventType).map(_.text)
      found.length should be(desired.size)

      desired.foreach(d => found should contain(d))
    }

    def testIfHasAttachmentType(mentions: Seq[Mention], attachmentType: String): Unit = {
      for (f <- mentions) {
        extractorAligner.returnAttachmentOfAGivenTypeOption(f.attachments, attachmentType).isDefined shouldBe true
      }
    }

    def testIfHasAttachments(mentions: Seq[Mention]): Unit = {
      mentions.foreach(f => testIfHasAttachment(f))
    }

    def testIfHasAttachment(mention: Mention): Unit = {
      mention.attachments.nonEmpty shouldBe true
    }

    //used for parameter setting tests where the setting is an interval
    def testThreeArgEvent(mentions: Seq[Mention], eventType: String, arg1Role: String, arg2Role: String, arg3Role: String, desired: Seq[(String, Seq[String])]): Unit = {

      val found = mentions.filter(_ matches eventType)
      found.length should be(desired.size)

      // note: assumes there's only one of each variable
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
        a1 <- m.arguments.getOrElse(arg1Role, Seq()).map(MentionUtils.getMentionText(_))
        a2 <- m.arguments.getOrElse(arg2Role, Seq()).map(MentionUtils.getMentionText(_))
      } yield (a1, a2)

      arg2Strings.foreach(arg2String => identifierDescriptionPairs should contain ((arg1String, arg2String)))
    }

    def testUnaryEvent(mentions: Seq[Mention], eventType: String, arg1Role: String, desired: Seq[String]): Unit = {
      val found = mentions.filter(_ matches eventType)
      found.length should be(desired.size)
      val grouped = found.groupBy(_.arguments(arg1Role).head.text) // we assume only one variable (arg1) arg!
      // when desired matches the text of the input arg, corresponding mentions are returned and the test passes
      // when the text does not match, there is no key in grouped for that so the returned seq is empty, and we get a failing test//
      for {
        desiredFragment <- desired
        correspondingMentions = grouped.getOrElse(desiredFragment, Seq())
      } testUnaryEventStrings(correspondingMentions, arg1Role, eventType, desired)
    }

    def testUnaryEventStrings(ms: Seq[Mention], arg1Role: String, eventType: String, arg1Strings: Seq[String]) = {
      val functionFragment = for {
        m <- ms
        a1 <- m.arguments.getOrElse(arg1Role, Seq()).map(MentionUtils.getMentionText(_))
      } yield a1
      arg1Strings.foreach(arg1String => functionFragment should contain (arg1String))
    }

    //used for parameter setting tests where the setting is an interval
    def testThreeArgEventString(ms: Seq[Mention], arg1Role: String, arg1String: String, arg2Role: String, arg2String: String, arg3Role: String, arg3String: String): Unit = {

      // assumes there is one of each arg
      val varMinMaxSettings =  for {
        m <- ms
        a1 = if (m.arguments.contains(arg1Role)) m.arguments.get(arg1Role).head.map(_.text).head else ""
        a2 = if (m.arguments.contains(arg2Role)) m.arguments.get(arg2Role).head.map(_.text).head else ""
        a3 = if (m.arguments.contains(arg3Role)) m.arguments.get(arg3Role).head.map(_.text).head else ""
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


    def getAttachmentJsonsFromArgs(mentions: Seq[Mention]): Seq[ujson.Value] = {
      val allAttachmentsInEvent = for {
        m <- mentions
        arg <- m.arguments
        a <- arg._2
        if a.attachments.nonEmpty
        att <- a.attachments
      } yield att.asInstanceOf[AutomatesAttachment].toUJson
      allAttachmentsInEvent
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

  class TestAlignment extends FlatSpec with Matchers {

    val passingTest = "passing"
    val failingTest = "failing"
    val failingNegative = "failingNegative"
    /*** TEST TYPES*/
    // DIRECT LINK TEST

    def runFailingTest(whichTest: String): Unit = {
      ignore should whichTest in {
        1 shouldEqual 1
      }
    }
    def topDirectLinkTest(idf: String, desired: String, directLinks: Map[String, Seq[Value]],
                          linkType: String, status: String): Unit = {

      val threshold = allLinkTypes("direct").obj(linkType).num
      if (status == "passing") {
        it should f"have a correct $linkType link for global var ${idf}" in {
          val topScoredLink = directLinks(linkType).sortBy(_.obj("score").num).reverse.head
          // which element in this link type we want to check
          val whichLink = whereIsNotGlobalVar(linkType)

          // element 1 of this link (eq gl var) should be E
          desired.split("::") should contain (topScoredLink(whichLink).str.split("::").last)
          topScoredLink("score").num >= threshold shouldBe true
        }
      } else {
        val failingMessage = if (status=="failingNegative") {
          f"have NO $linkType link for global var ${idf}"
        } else {
          f"have a correct $linkType link for global var ${idf}"
        }
        runFailingTest(failingMessage)
      }

    }

    def negativeDirectLinkTest(idf: String, directLinks: Map[String, Seq[Value]],
                               linkType: String): Unit = {
      it should s"have NO ${linkType} link for global var $idf" in {
        val threshold = allLinkTypes("direct").obj(linkType).num
        val condition1 = Try(directLinks.keys.toList.contains(linkType) should be(false)).isSuccess
        val condition2 = Try(directLinks
        (linkType).sortBy(_.obj("score").num).reverse.head("score").num > threshold shouldBe false).isSuccess
        assert(condition1 || condition2)
      }
    }


    // INDIRECT LINK TESTS

    def topIndirectLinkTest(idf: String, desired: String, inDirectLinks: Map[String,
      Seq[Tuple[String, Double]]],
                            linkType: String, status: String): Unit = {
      // todo: use threshold here now that we are saving it
      val threshold = allLinkTypes("indirect").obj(linkType).num
      if (status == "passing") {
        it should f"have a correct $linkType link for global var ${idf}" in {
          // these are already sorted
          val topScoredLink = inDirectLinks(linkType)
//          for (l <- topScoredLink) println(">>>" + l)
          topScoredLink.head._1.split("::").last shouldEqual desired
          topScoredLink.head._2 > threshold shouldBe true
        }
      } else {
        runFailingTest(f"have a correct $linkType link for global var ${idf}")
      }
    }


    def negativeIndirectLinkTest(idf: String, indirectLinks: Map[String, Seq[Tuple[String, Double]]],
                                 linkType: String): Unit = {
      it should s"have NO ${linkType} link for global var $idf" in {

        val threshold = allLinkTypes("indirect").obj(linkType).num
        val condition1 = Try(indirectLinks.keys.toList.contains(linkType) should be(false)).isSuccess
        val condition2 = Try(indirectLinks
        (linkType).head._2 > threshold shouldBe false).isSuccess
        assert(condition1 || condition2)
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

    // return indirect links of a given type as a list of strings per each intermediate node
    def findIndirectLinks(allDirectVarLinks: Seq[Value], allLinks: Seq[Value], linkTypeToBuildOffOf: String,
                          indirectLinkType: String, nIndirectLinks: Int): Map[String, Seq[Tuple[String, Double]]] =
    {
      val indirectLinkEndNodes = new ArrayBuffer[Tuple[String,Double]]()
      val allIndirectLinks = new ArrayBuffer[Value]()
      // we have links for some var, e.g., I(t)
      // through one of the existing links, we can get to another type of node
      val topNDirectLinkOfTargetTypeSorted = allDirectVarLinks.filter(_.obj("link_type").str==linkTypeToBuildOffOf).sortBy(_.obj("score").num).reverse.slice(0, nIndirectLinks)
      // keep for debugging
//      for (tdl <- topNDirectLinkOfTargetTypeSorted) {
//        println("dir link: " + tdl)
//      }
      val sortedIntermNodeNames = new ArrayBuffer[String]()


      for (dl <- topNDirectLinkOfTargetTypeSorted) {
        // get intermediate node of indirect link - for comment_to_gvar link, it's element_1
        val intermNodeJustName = linkTypeToBuildOffOf match {
          case "comment_to_gvar" => dl("element_1").str
          case _ => ???
        }
        sortedIntermNodeNames.append(intermNodeJustName)


        val indirectLinksForIntermNode = getLinksWithIdentifierStr(intermNodeJustName, allLinks, true).filter(_.obj
        ("link_type").str == indirectLinkType).sortBy(_.obj("score").num).reverse
        for (il <- indirectLinksForIntermNode) {

          allIndirectLinks.append(il)
//          println("indir links per interm node: " + il)
        }

      }


      // return only the ones of the given type
      val groupedByElement2 = allIndirectLinks.groupBy(_.obj("element_2").str)//.map(gr => (gr._1,gr._2.sortBy(_.obj("score").num)))
//      for (g <- groupedByElement2) {
//        println("G: " + g._1)
//        for (i <- g._2) {
//          println("=>" + i)
//        }
//      }

      val maxLinksPerIntermNode = groupedByElement2.maxBy(_._2.length)._2.length

      for (i <- 0 until maxLinksPerIntermNode) {
        for (j <- 0 until sortedIntermNodeNames.length) {
          val intermNodeName = sortedIntermNodeNames(j)

          val endNode = groupedByElement2(intermNodeName).map(l => Tuple(l.obj("element_1").str, l.obj("score").num))
          if (endNode.length > i) {
            indirectLinkEndNodes.append(endNode(i))
          }

        }
      }

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

    def getLinksForGvar(idfr: String, allLinks: Seq[Value]): (Map[String, Seq[Value]], Map[String, Seq[Tuple[String,
      Double]]])
    = {

      val maybeGreek = AlignmentBaseline.replaceGreekWithWord(idfr, AlignmentBaseline.greek2wordDict.toMap).replace("\\\\", "")
      // links are returned as maps from link types to a) full links for direct links and b) sequences of elements linked indirectly to the global var
      // sorted by score based on the two edges in the indirect link
      // all links that contain the target text global var string
      // and only the links that contain global vars
      val allDirectLinksForIdfr = if (idfr == maybeGreek) {
        // this means this is not a greek letter, so proceed as ususal
        getLinksWithIdentifierStr(idfr, allLinks, false).filter(link => whereIsGlobalVar.contains(link.obj("link_type").str))
      } else {
        getLinksWithIdentifierStr(idfr, allLinks, false).filter(link => whereIsGlobalVar.contains(link.obj("link_type").str)) ++    getLinksWithIdentifierStr(maybeGreek, allLinks, false).filter(link => whereIsGlobalVar.contains(link.obj("link_type").str))
      }

//      for (l <- allDirectLinksForIdfr) println("link: " + l)

      // filtering out the links with no idfr with the correct idf; can't have the link uid in the test itself bc those
      // are randomly generated on every run
      // this has to be one of the links with global variable

      val idfrWithIdFromMultipleLinks = new ArrayBuffer[String]()
      for (l <- allDirectLinksForIdfr) {
        val linkType = l("link_type").str
        val whichElement = whereIsGlobalVar(linkType)
        val fullIdfrUid = l(whichElement).str
        if (fullIdfrUid.split("::").last == idfr) {
          idfrWithIdFromMultipleLinks.append(fullIdfrUid)
        }

      }

      val fullIdfrUid = idfrWithIdFromMultipleLinks.head
//      println("full idfr uid: " + fullIdfrUid)
      val onlyWithCorrectIdfr = allDirectLinksForIdfr.filter(link => link(whereIsGlobalVar(link("link_type").str)).str ==
        fullIdfrUid)
      // group those by link type - in testing, will just be checking the rankings of links of each type
      val directLinksGroupedByLinkType = onlyWithCorrectIdfr.groupBy(_.obj("link_type").str)

      // keep for debug
//      for (l <- directLinksGroupedByLinkType) {
//        println(s"---${l._1}---")
//        for (i <- l._2.sortBy(el => el("score").num).reverse) println(">> " + i)
//      }

      // get indirect links; currently, it's only source to comment links aligned through comment (comment var is the intermediate node)
      val indirectLinks = if (directLinksGroupedByLinkType.contains("comment_to_gvar")) {
        findIndirectLinks(onlyWithCorrectIdfr, allLinks, "comment_to_gvar", "source_to_comment", 3)

      } else null


//      for (linkGr <- indirectLinks) {
//        println(s"===${linkGr._1}===")
//        for (link <- linkGr._2) {
//          println(link)
//        }
//      }

      (directLinksGroupedByLinkType, indirectLinks)
    }


    def runAllAlignTests(variable: String, directLinks: Map[String, Seq[Value]], indirectLinks: Map[String,
      Seq[Tuple[String,
      Double]]],
                         directDesired: Map[String, Tuple2[String, String]], indirectDesired: Map[String, Tuple2[String, String]])
    : Unit
    = {
      for (dl <- directDesired) {
        val desired = dl._2._1
        val linkType = dl._1
        val status = dl._2._2
        topDirectLinkTest(variable, desired, directLinks, linkType, status)
      }

//      for (dl <- indirectLinks) println("indir: " + dl._1 + " " + dl._2)
      for (dl <- indirectDesired) {
        val desired = dl._2._1
        val linkType = dl._1
        val status = dl._2._2
        topIndirectLinkTest(variable, desired, indirectLinks, linkType, status)
      }

      for (dlType <- allLinkTypes("direct").obj.keys) {
        if (!directDesired.contains(dlType)) {
          negativeDirectLinkTest(variable, directLinks, dlType)
        }
      }

      for (dlType <- allLinkTypes("indirect").obj.keys) {
        if (!indirectDesired.contains(dlType)) {
          negativeIndirectLinkTest(variable, indirectLinks, dlType)
        }
      }
    }
  }

}
