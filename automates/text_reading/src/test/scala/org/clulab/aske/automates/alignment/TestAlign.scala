package org.clulab.aske.automates.alignment

import java.io.File

import ai.lum.common.ConfigUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.aske.automates.{OdinEngine, TestUtils}
import org.clulab.aske.automates.TestUtils.jsonStringToDocument
import org.clulab.aske.automates.apps.ExtractAndAlign
import org.clulab.embeddings.word2vec.Word2Vec
import org.clulab.grounding.sparqlResult
import org.clulab.odin.{Mention, RelationMention, TextBoundMention}
import org.clulab.struct.Interval
import org.clulab.utils.{AlignmentJsonUtils, Sourcer}
import org.scalatest.{FlatSpec, Matchers}
import ujson.Value
import ai.lum.common.FileUtils._
import org.clulab.aske.automates.apps.ExtractAndAlign.{getCommentDescriptionMentions, hasRequiredArgs}
import org.clulab.aske.automates.grfn.GrFNParser

import scala.collection.mutable.ArrayBuffer

class TestAlign extends FlatSpec with Matchers {


//  def getListOfFiles(dir: File, extensions: List[String]): List[File] = {
//    dir.listFiles.filter(_.isFile).toList.filter { file =>
//      extensions.exists(file.getName.endsWith(_))
//    }
//  }
  println("HERE")
  val config = ConfigFactory.load("/test.conf")
  val numAlignments = 3//config[String]("apps.numAlignments")
  val numAlignmentsSrcToComment = 1//config[String]("apps.numAlignmentsSrcToComment")
  val scoreThreshold = 0.0 //config[String]("apps.scoreThreshold")

  val w2v = new Word2Vec(Sourcer.sourceFromResource("/vectors.txt"), None) //todo: read this from test conf (after adding this to test conf)
  lazy val proc = TestUtils.newOdinSystem(config).proc
//  val srcDir: File = new File(getClass.getResource("/").getFile)
//  println("-->" + srcDir)
  val inputDir = new File(getClass.getResource("/").getFile)
  val files = inputDir.listFiles()
  for (f <- files) println(">>>", f)

  println("++>>", inputDir)



  // read in all related docs or maybe read in just a sample payload - that should make sense
  // make it as close as possivle to the actual endpoint while still mainly testing the ExtractAndAlign.groundMentions method (to get texts of links, need to run in debug mode)
  // the rest will be tested on paul's end
  // for now just use sample json

  //lazy val commentReader = OdinEngine.fromConfigSection("CommentEngine")
  val alignmentHandler = new AlignmentHandler(ConfigFactory.load()[Config]("alignment"))

  println(alignmentHandler + "<+")
  val serializerName = "AutomatesJSONSerializer"


  val jsonFile = new File("/home/alexeeva/Repos/automates/automates/text_reading/src/test/resources/temporaryAlignmentOutputSample.json") //todo: this should be read in from inputDir
  val json = ujson.read(jsonFile.readString()).obj("grounding")

//  val grfnFile = new File("/home/alexeeva/Repos/automates/automates/text_reading/src/test/resources/2003-double-epidemic-grfn.json")
//  val grfn = ujson.read(grfnFile.readString())

  val payloadPath = "/home/alexeeva/Repos/automates/automates/text_reading/src/test/resources/double-epidemic-chime-align_payload.json"
  val payloadFile = new File(payloadPath)

  val payloadJson = ujson.read(payloadFile.readString())

  val jsonObj = payloadJson.obj
//
//  val source = if (grfn.obj.get("source").isDefined) {
//    Some(grfn.obj("source").arr.mkString(";"))
//  } else None
//  // Get source identifiers
//  val identifierNames = Some(GrFNParser.getVariables(grfn))
//  val variableShortNames = Some(GrFNParser.getVariableShortNames(identifierNames.get))
//  // Get comment descriptions
//  val commentDescriptionMentions = getCommentDescriptionMentions(localCommentReader, grfn, variableShortNames, source)
//    .filter(m => hasRequiredArgs(m, "description"))

  val argsForGrounding = AlignmentJsonUtils.getArgsForAlignment(payloadPath, jsonObj, false, serializerName)

//  println(argsForGrounding + "<<<<===")

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
    Some(numAlignments),
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

  it should "have text variable to parameter setting (via identifier) links" in {
    linkTypes.contains("gvar_to_param_setting_via_idfr") shouldBe true
  }

  it should "have text variable to parameter setting (via concept) links" in {
    linkTypes.contains("gvar_to_param_setting_via_cpcpt") shouldBe true
  }

  it should "have text variable to interval parameter setting (via identifier) links" in {
    linkTypes.contains("gvar_to_interval_param_setting_via_idfr") shouldBe true
  }

  println(linkTypes + "<<")

  val (withGvarLinkTypes, otherLinksTypes) = linkTypes.partition(_.contains("gvar"))


//    // todo: find indirect link for a given gvar

  // todo: double-check returning the right number of indirect alignments per intermediate node
  // return indirect links of a given type as a list of
  def findIndirectLinks(allDirectVarLinks: Seq[Value], allLinks: Seq[Value], linkTypeToBuildOffOf: String, indirectLinkType: String, nIndirectLinks: Int): Map[String, Seq[String]] = {//Map[String, Map[String, ArrayBuffer[Value]]] = {

    val indirectLinkEndNodes = new ArrayBuffer[String]()
    val allIndirectLinks = new ArrayBuffer[Value]()
    // we have links for some var, e.g., I(t)
    // through one of the existing links, we can get to another type of node
    // probably already sorted - double-check
    val topNDirectLinkOfTargetTypeSorted = allDirectVarLinks.filter(_.obj("link_type").str==linkTypeToBuildOffOf).sortBy(_.obj("score").num).reverse.slice(0, nIndirectLinks)
    val sortedIntermNodeNames = new ArrayBuffer[String]()

    //
    for (dl <- topNDirectLinkOfTargetTypeSorted) {
      // get intermediate node of indirect link - for comment_to_gvar link, it's element_1
      val intermNodeJustName = linkTypeToBuildOffOf match {
        case "comment_to_gvar" => dl("element_1").str
        case _ => ???
      }
      sortedIntermNodeNames.append(intermNodeJustName)

      //
      val indirectLinksForIntermNode = getLinksWithIdentifierStr(intermNodeJustName, allLinks, true)//.sortBy(_.obj("score")).reverse
      for (il <- indirectLinksForIntermNode) {
        allIndirectLinks.append(il)
      }

    }


    // return only the ones of the given type
    val groupedByElement2 = allIndirectLinks.filter(_.obj("link_type").str == indirectLinkType).groupBy(_.obj("element_2").str)
    val maxLinksPerIntermNode = groupedByElement2.maxBy(_._2.length)._2.length

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


//  // todo: double-check returning the right number of indirect alignments per intermediate node
  // this version is just for a seq of links
//  def findIndirectLinks(allDirectVarLinks: Seq[Value], allLinks: Seq[Value], linkTypeToBuildOffOf: String, indirectLinkType: String, nIndirectLinks: Int): Seq[Value] = {
//
//    val allIndirectLinks = new ArrayBuffer[Value]()
//    // we have links for some var, e.g., I(t)
//    // through one of the existing links, we can get to another type of node
//    // probably already sorted - double-check
//    val topNDirectLinkOfTargetTypeSorted = allDirectVarLinks.filter(_.obj("link_type").str==linkTypeToBuildOffOf).sortBy(_.obj("score").num).reverse.slice(0, nIndirectLinks)
//    for (dl <- topNDirectLinkOfTargetTypeSorted) {
//      // get intermediate node of indirect link - for comment_to_gvar link, it's element_1
//      val intermNodeJustName = linkTypeToBuildOffOf match {
//        case "comment_to_gvar" => dl("element_1").str
//        case _ => ???
//      }
//
//      val indirectLinksForIntermNode = getLinksWithIdentifierStr(intermNodeJustName, allLinks, true)
//      for (il <- indirectLinksForIntermNode) {
//        allIndirectLinks.append(il)
//      }
//
//    }
//    // return only the ones of the given type
//    allIndirectLinks.filter(_.obj("link_type").str == indirectLinkType)
//
//  }
//  //

  def getLinksWithIdentifierStr(identifierName: String, allLinks: Seq[Value], inclId: Boolean): Seq[Value] = {
    val toReturn = if (inclId) {
      allLinks.filter(l => l.obj("element_1").str == identifierName || l.obj("element_2").str == identifierName)
    } else {
      allLinks.filter(l => l.obj("element_1").str.split("::").last == identifierName || l.obj("element_2").str.split("::").last == identifierName)

    }
    toReturn
  }

  val it_links_not_grouped = getLinksWithIdentifierStr("I(t)", links, false)
//  val e_links_not_grouped = getLinksWithIdentifierStr("E", links, false)


  // link test type 1: for every var, check if the gold test is top
  // get all the links where one of the elements is the E identifier
  // todo: define a method to do this for a given Identifier string
  val E_links = links.filter(l => l.obj("element_1").str.split("::").last =="E" || l.obj("element_2").str.split("::").last =="E").groupBy(_.obj("link_type").str)



  val it_links = links.filter(l => l.obj("element_1").str.split("::").last =="I(t)" || l.obj("element_2").str.split("::").last =="I(t)").groupBy(_.obj("link_type").str)

  for (gr <- it_links) {
    for (i <- gr._2.sortBy(_.obj("score").num).reverse) {
      println(i)
    }
    println("----------")
  }

  val allIndirectLinksForITLinks = findIndirectLinks(it_links_not_grouped, links, "comment_to_gvar", "source_to_comment", 2)
  for (aiIT <- allIndirectLinksForITLinks) println("it indirect: " + aiIT)

  println("INDIRECT: " + allIndirectLinksForITLinks)


//  ignore should "have a correct comment to src var link for I(t) idenfier" in {
//    allIndirectLinksForITLinks.head("element_1").str.split("::").last == "i_t" shouldBe true// I made this src code variable - i dont think it's in code base
//  }
//  val allIndirectLinksForELinks = findIndirectLinks(e_links_not_grouped, links, "comment_to_gvar", "source_to_comment", 2)
//  for (aiIT <- allIndirectLinksForELinks) println("E indirect: " + aiIT)

  it should "have a correct equation to global variable link for global var E" in {
    val topScoredLink = E_links("equation_to_gvar").sortBy(_.obj("score").num).reverse.head
    //
    val desired = "E"
    val threshold = 0.8 // the threshold will be set globally (from config?) as an allowed link
    // element 1 of this link (eq gl var) should be E
    topScoredLink("element_1").str.split("::").last shouldEqual desired
    topScoredLink("score").num > threshold shouldBe true
  }

  // this is for non-existent links (including those we end up filtering out because of threshold)
  it should "have NO gvar_to_unit_via_cpcpt link for global var E" in {
    E_links.keys.toList.contains("gvar_to_unit_via_cpcpt") shouldBe false
  }

  // if we decide not to filter out links because of threshold (could be beneficial to keep them for debugging purposes, but filter them out somewhere downstream; ask Paul), do this type of test:

  it should "have top gvar_to_unit_via_idfr link be below threshold for global var E" in {
    val topScoredLink = E_links("gvar_to_unit_via_idfr").sortBy(_.obj("score").num).reverse.head
    //
    val threshold = 0.8 // the threshold will be set globally (from config?) as an allowed link
    // element 1 of this link (eq gl var) should be E
    topScoredLink("score").num < threshold shouldBe true
  }




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


  var score = 0

  for (key <- toyGoldIt.keys) {
    println("key: " + key)

    if (allIndirectLinksForITLinks.contains(key)) {
      // if in indirect links, then it's this complicated check
      val linksOfGivenType = allIndirectLinksForITLinks(key).map(_.split("::").last)
      println("links of a given type comment: " + linksOfGivenType.mkString("||"))
      val rank = linksOfGivenType.indexOf(toyGoldIt(key)) + 1
      val scoreUpdate = if (rank > 0) 1/rank  else 0
      score += scoreUpdate

    } else if (it_links.contains(key)) {
//      var rank = 0
      // which element in this link type we want to check
      val whichLink = key match {
        case "equation_to_gvar" |  "comment_to_gvar"  => "element_1"
        case "gvar_to_interval_param_setting_via_idfr" | "gvar_to_unit_via_idfr"  => "element_2"
        case _ => ???
      }
      val linksOfGivenType = it_links(key).sortBy(_.obj("score").num).reverse.map(_(whichLink).str.split("::").last)
      println("links of a given type: " + linksOfGivenType)
      val rank = linksOfGivenType.indexOf(toyGoldIt(key)) + 1
      println("key/rank: " + key +  rank)
      val scoreUpdate = if (rank > 0) 1/rank  else 0
      score += scoreUpdate


    } else {
      println("missing link")
    }

  }



  val finalScore = score.toDouble/toyGoldIt.keys.toList.length

  println("final score: " + finalScore)



}
