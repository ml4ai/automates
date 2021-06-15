package org.clulab.aske.automates.alignment

import java.io.File

import ai.lum.common.ConfigUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.aske.automates.{OdinEngine, TestUtils}
import org.clulab.aske.automates.apps.ExtractAndAlign
import org.clulab.embeddings.word2vec.Word2Vec
import org.clulab.utils.{AlignmentJsonUtils, Sourcer}
import org.scalatest.{FlatSpec, Matchers}
import ujson.Value
import ai.lum.common.FileUtils._
import org.clulab.aske.automates.data.DataLoader

import scala.collection.mutable.ArrayBuffer

class TestAlign extends FlatSpec with Matchers {


  // utils (todo: move to TestUtils)


  println("HEREEE: " + org.apache.commons.text.StringEscapeUtils.unescapeJava("(2) Eeq = s s + \\u03b3 \\u03bb where " +
    "Rnday is daily surface net radiation (in J m\\u22122 day\\u22121) and \\u03bb is the latent heat of vaporization" +
    " (in J kg\\u22121)"))
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
    for (i <- 0 to maxLinksPerIntermNode - 1) {
      for (j <- 0 to sortedIntermNodeNames.length - 1) {
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




  // load files/configs

  val config = ConfigFactory.load("/test.conf")
  val numAlignments = 3//config[String]("apps.numAlignments")
  val numAlignmentsSrcToComment = 1//config[String]("apps.numAlignmentsSrcToComment")
  val scoreThreshold = 0.0 //config[String]("apps.scoreThreshold")

  val w2v = new Word2Vec(Sourcer.sourceFromResource("/vectors.txt"), None) //todo: read this from test conf (after adding this to test conf)
//  lazy val proc = TestUtils.newOdinSystem(config).proc
  val inputDir = new File(getClass.getResource("/").getFile)
  val files = inputDir.listFiles()
  for (f <- files) println(">>>", f)

  println("++>>", inputDir)



  // read in all related docs or maybe read in just a sample payload - that should make sense
  // make it as close as possivle to the actual endpoint while still mainly testing the ExtractAndAlign.groundMentions method (to get texts of links, need to run in debug mode)
  // the rest will be tested on paul's end

  //lazy val commentReader = OdinEngine.fromConfigSection("CommentEngine")
  val alignmentHandler = new AlignmentHandler(ConfigFactory.load()[Config]("alignment"))
  val serializerName = "AutomatesJSONSerializer" //todo: read from config


//  val payloadPath = "/home/alexeeva/Repos/automates/automates/text_reading/src/test/resources/double-epidemic-chime-align_payload-for-testing.json"
  val payloadFile = new File(inputDir, "double-epidemic-chime-align_payload-for-testing.json")
  val payloadPath = payloadFile.getAbsolutePath

  val payloadJson = ujson.read(payloadFile.readString())

  val jsonObj = payloadJson.obj


  val argsForGrounding = AlignmentJsonUtils.getArgsForAlignment(payloadPath, jsonObj, false, serializerName)


  val groundings = ExtractAndAlign.groundMentions(
    payloadJson,
    argsForGrounding.identifierNames,
    argsForGrounding.identifierShortNames,
    argsForGrounding.descriptionMentions,
    argsForGrounding.parameterSettingMentions,
    argsForGrounding.intervalParameterSettingMentions,
    argsForGrounding.unitMentions,
    argsForGrounding.commentDescriptionMentions,
    argsForGrounding.equationChunksAndSource,
    argsForGrounding.svoGroundings,
    false,
    3,
    alignmentHandler,
    Some(5),
    Some(2),//Some(numAlignmentsSrcToComment),
    scoreThreshold,
    appendToGrFN=false,
    debug=true
  )

  val links = groundings.obj("links").arr
  val gv = findGlobalVars(links)



  val linkTypes = links.map(_.obj("link_type").str).distinct

  // on the real test document, will have all link types
  it should "have source code variable to comment links" in {
    linkTypes.contains("source_to_comment") shouldBe true
  }

  it should "have comment to text variable links" in {
    linkTypes.contains("comment_to_gvar") shouldBe true
  }

  it should "have equation variable to text variable links" in {
    linkTypes.contains("equation_to_gvar") shouldBe true
  }

  it should "have text variable to unit (via identifier) links" in {
    linkTypes.contains("gvar_to_unit_via_idfr") shouldBe true
  }

  it should "have text variable to unit (via concept) links" in {
    linkTypes.contains("gvar_to_unit_via_cpcpt") shouldBe true
  }

  it should "have text variable to parameter setting (via identifier) links" in {
    linkTypes.contains("gvar_to_param_setting_via_idfr") shouldBe true
  }

  it should "have text variable to parameter setting (via concept) links" in {
    linkTypes.contains("gvar_to_param_setting_via_cpcpt") shouldBe true
  }

  it should "have text variable to interval parameter setting (via identifier) links" in {
    linkTypes.contains("gvar_to_interval_param_setting_via_idfr") shouldBe true
  }

  it should "have text variable to interval parameter setting (via concept) links" in {
    linkTypes.contains("gvar_to_interval_param_setting_via_cpcpt") shouldBe true
  }
  println(linkTypes + "<<")

  val (withGvarLinkTypes, otherLinksTypes) = linkTypes.partition(_.contains("gvar"))



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
    // all links that contain the target text global var
    val allDirectLinksForIdfr = getLinksWithIdentifierStr(idfr, allLinks, false)

    // group those by link type - in testing, will just be checking the rankings of links of each type
    val directLinksGroupedByLinkType = allDirectLinksForIdfr.groupBy(_.obj("link_type").str)
    for (l <- directLinksGroupedByLinkType) {
      println("---")
      for (i <- l._2.sortBy(el => el("score").num).reverse) println("-> " + i)
    }

    val indirectLinks = if (directLinksGroupedByLinkType.contains("comment_to_gvar")) {
      findIndirectLinks(allDirectLinksForIdfr, links, "comment_to_gvar", "source_to_comment", 3)

    } else null
    // get indirect links; currently, it's only source to comment links aligned through comment (comment var is the intermediate node)

    println("dir link len: " + directLinksGroupedByLinkType.keys.toList.length)
    (directLinksGroupedByLinkType, indirectLinks)
  }



//  val (directLinksForE, indir) = getLinksForGvar("r", links)

//  println("FROM METHOD")
//  printGroupedLinksSorted(directLinksForE)
//  printIndirectLinks(indir)


  def topLinkTest(idf: String, desired: String, threshold: Double, directLinks: Map[String, Seq[Value]], linkType: String): Unit = {
    it should f"have a correct $linkType link for global var ${idf}" in {
      val topScoredLink = directLinks(linkType).sortBy(_.obj("score").num).reverse.head

      // which element in this link type we want to check
      val whichLink = linkType match {
        case "equation_to_gvar" |  "comment_to_gvar"  => "element_1"
        case "gvar_to_interval_param_setting_via_idfr" | "gvar_to_unit_via_idfr"  => "element_2"
        case _ => ???
      }
      // element 1 of this link (eq gl var) should be E
      topScoredLink(whichLink).str.split("::").last shouldEqual desired
      topScoredLink("score").num > threshold shouldBe true
    }
  }

//  val idf = "r"
//  val desired = "r"
//  val threshold = 0.8
//  val (directLinksForR, indirR) = getLinksForGvar("r", links)
//  topLinkTest(idf, desired, threshold, directLinksForR,"equation_to_gvar")
//
  {
    val idfE = "E"
    behavior of idfE

    val desiredE = "E"
    val thresholdE = 0.8 // same for all elements of link type probably
    val (directLinksForE, indirE) = getLinksForGvar("E", links)

    topLinkTest(idfE, desiredE, thresholdE, directLinksForE, "equation_to_gvar")

    // this is for non-existent links (including those we end up filtering out because of threshold)
    it should s"have NO gvar_to_unit_via_cpcpt link for global var $idfE" in {
      directLinksForE.keys.toList.contains("gvar_to_unit_via_cpcpt") shouldBe false
    }
  }


//  println("len of dir links: " + directLinksForE.keys.toList.length)
//  for (l <- directLinksForE) {
//    println("link type: " + l._1)
//    for (link <- l._2) {
//      println(link)
//    }
//  }



  // if we decide not to filter out links because of threshold (could be beneficial to keep them for debugging purposes, but filter them out somewhere downstream; ask Paul), do this type of test:
//
//  it should "have top gvar_to_unit_via_idfr link be below threshold for global var E" in {
//    val topScoredLink = directLinksForE("gvar_to_unit_via_idfr").sortBy(_.obj("score").num).reverse.head
//    //
//    val threshold = 0.8 // the threshold will be set globally (from config?) as an allowed link
//    // element 1 of this link (eq gl var) should be E
//    topScoredLink("score").num < threshold shouldBe true
//  }




  // link test type 2: check if the links contains certain links with scores over threshold
  val src_comment_links = links.filter(_.obj("link_type").str == "source_to_comment")

  it should "have an s_t src to comment element" in {
    src_comment_links.exists(l => l.obj("element_1").str.contains("s_t") & l.obj("element_2").str.contains("S_t") && l.obj("score").num > 0.8) shouldBe true

    // hard to make negative links since we do make an attempt to get top 3 and there will be false positives there - ph already addressed it---need to have something like the score of this shouldn't be more than x (or maybe... it should be something like it shouldn't be higher than the score of the gold one because we may change weights on aligners (like what weighs more: w2v or edit distance) and the scores will change
    // need to check if the best one is the top out of three - this is basically the most important thing

    // another problem - there could be multiples of the same text but different ids... should we do global source and global equation as well? basically anything that can have exactly the same form?

    // for unit tests, does it need to be exhaustive?
    // for other eval, probably yes


  }

  def findGlobalVars(links: Seq[Value]): Seq[String] = {
    val glVarIds = new ArrayBuffer[String]()
    for (link <- links) {
      val linkType = link.obj("link_type").str
//      println("link type: " + linkType)
      linkType match {
        case "comment_to_gvar" | "equation_to_gvar" => glVarIds.append(link.obj("element_2").str)
        case "source_to_comment"  =>
        case _ => glVarIds.append(link.obj("element_1").str)
      }
    }
    for (gv <- glVarIds.distinct) println("gv: " + gv)
    glVarIds.distinct
  }



  val comment_gvar_links = links.filter(_.obj("link_type").str == "comment_to_gvar")

  val toyGoldIt = Map(
//    "equation_to_gvar" -> "frac{dIp}{dt}",
//    "gvar_to_interval_param_setting_via_idfr" -> "R0>1",
//    "comment_to_gvar" -> "inc_exp_a",
//    "source_to_comment" -> "inc_exp_a",
//    "gvar_to_unit_via_idfr" -> "details of the dS dt rS t I t r S t I t dE dt rS t I t bE t bE t aI t dR dt aI t dt r S t I t"

    "equation_to_gvar" -> "frac{dI}{dt}",
    "gvar_to_interval_param_setting_via_idfr" -> "R0>1",
    "comment_to_gvar" -> "inc_exp_a",
    "source_to_comment" -> "inc_exp_a",
    "gvar_to_unit_via_idfr" -> "details of the dS dt rS t I t r S t I t dE dt rS t I t bE t bE t aI t dR dt aI t dt r S t I t"
  )
//  val allToyItLinks = (it_links ++ allIndirectLinksForITLinks).toSeq


//  var score = 0
//
//  for (key <- toyGoldIt.keys) {
////    println("key: " + key)
//
//    if (allIndirectLinksForITLinks.contains(key)) {
//      // if in indirect links, then it's this complicated check
//      val linksOfGivenType = allIndirectLinksForITLinks(key).map(_.split("::").last)
////      println("links of a given type comment: " + linksOfGivenType.mkString("||"))
//      val rank = linksOfGivenType.indexOf(toyGoldIt(key)) + 1
//      val scoreUpdate = if (rank > 0) 1/rank  else 0
//      score += scoreUpdate
//
//    } else if (itLinksGroupedByLinkType.contains(key)) {
////      var rank = 0
//      // which element in this link type we want to check
//      val whichLink = key match {
//        case "equation_to_gvar" |  "comment_to_gvar"  => "element_1"
//        case "gvar_to_interval_param_setting_via_idfr" | "gvar_to_unit_via_idfr"  => "element_2"
//        case _ => ???
//      }
//      val linksOfGivenType = itLinksGroupedByLinkType(key).sortBy(_.obj("score").num).reverse.map(_(whichLink).str.split("::").last)
////      println("links of a given type: " + linksOfGivenType)
//      val rank = linksOfGivenType.indexOf(toyGoldIt(key)) + 1
////      println("key/rank: " + key +  rank)
//      val scoreUpdate = if (rank > 0) 1/rank  else 0
//      score += scoreUpdate
//
//
//    } else {
//      println("missing link")
//    }
//
//  }
//
//
//
//  val finalScore = score.toDouble/toyGoldIt.keys.toList.length

//  println("final score: " + finalScore)



}
