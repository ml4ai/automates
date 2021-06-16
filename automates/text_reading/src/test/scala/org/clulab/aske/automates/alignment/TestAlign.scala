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
import org.clulab.aske.automates.TestUtils.{findIndirectLinks, getLinksForGvar, getLinksWithIdentifierStr}
import org.clulab.aske.automates.apps.ExtractAndAlign.{allLinkTypes, whereIsGlobalVar, whereIsNotGlobalVar}
import org.clulab.aske.automates.data.DataLoader

import scala.collection.mutable.ArrayBuffer
import scala.util.Try

class TestAlign extends FlatSpec with Matchers {

  // utils (todo: move to TestUtils)
  //todo: cleanup imports
  // todo: need a negative test of some kind, would be great if there were an either or like links dont contain this
  //  link should be true OR top link of that kind should be false
  // xor test in scala?

  println("HEREEE: " + org.apache.commons.text.StringEscapeUtils.unescapeJava("(2) Eeq = s s + \\u03b3 \\u03bb where " +
    "Rnday is daily surface net radiation (in J m\\u22122 day\\u22121) and \\u03bb is the latent heat of vaporization" +
    " (in J kg\\u22121)"))
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
  val linkTypes = links.map(_.obj("link_type").str).distinct

  it should "have all the link types" in {
    val allLinksTypesFlat = allLinkTypes.filter(_._1 != "disabled").flatMap(_._2).map(_._1).toSeq
    val overlap = linkTypes.intersect(allLinksTypesFlat)
    overlap.length == linkTypes.length  shouldBe true
    overlap.length == allLinksTypesFlat.length shouldBe true
  }





//
  {

    val idfE = "E"
    behavior of idfE

    val directDesired = Map(
      "equation_to_gvar" -> "E",
      "gvar_to_param_setting_via_idfr" -> "E = 30",
      "comment_to_gvar" -> "E"
    )

    val indirectDesired = Map(
      "source_to_comment" -> "E"
    )

    val thresholdE = 0.8 // same for all elements of link type probably
    val (directLinksForE, indirE) = getLinksForGvar("E", links)

    runAllTests(directLinksForE, indirE, directDesired, indirectDesired)


    def runAllTests(directLinks: Map[String, Seq[Value]], indirectLinks: Map[String, Seq[String]],
                    directDesired: Map[String, String], indirectDesired: Map[String, String]): Unit = {


      for (dl <- directDesired) {
        topDirectLinkTest(idfE, dl._2, thresholdE, directLinks, dl._1)
      }

      for (dl <- indirE) println("indir: " + dl._1 + " " + dl._2.mkString("||"))
      for (dl <- indirectDesired) {
        println(">>>" + dl._1 + " " + dl._2)
        topIndirectLinkTest(idfE, dl._2, thresholdE, indirE, dl._1)
      }
      for (dlType <- allLinkTypes("direct")) {
        if (!directDesired.contains(dlType._1)) {
          negativeDirectLinkTest(idfE, dlType._2, directLinks, dlType._1)
        }
      }

  }


    //    topLinkTest(idfE, desiredE, thresholdE, directLinksForE, "equation_to_gvar")

    // this is for non-existent links (including those we end up filtering out because of threshold)





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

  /*** TEST TYPES*/
    // DIRECT LINK TEST
  def topDirectLinkTest(idf: String, desired: String, threshold: Double, directLinks: Map[String, Seq[Value]],
                        linkType: String): Unit = {
    it should f"have a correct $linkType link for global var ${idf}" in {
      val topScoredLink = directLinks(linkType).sortBy(_.obj("score").num).reverse.head

      // which element in this link type we want to check
      val whichLink = whereIsNotGlobalVar(linkType)
      // element 1 of this link (eq gl var) should be E
      topScoredLink(whichLink).str.split("::").last shouldEqual desired
      topScoredLink("score").num > threshold shouldBe true
    }
  }

  def negativeDirectLinkTest(idf: String, threshold: Double, directLinks: Map[String, Seq[Value]],
                             linkType: String): Unit = {
    it should s"have NO ${linkType} link for global var $idf" in {

      val condition1 = Try(directLinks.keys.toList.contains(linkType) should be(false)).isSuccess
      val condition2 = Try(directLinks
      (linkType).sortBy(_.obj("score").num).reverse.head("score").num > threshold shouldBe false).isSuccess
      assert(condition1 || condition2)
    }
  }

  // INDIRECT LINK TESTS

  def topIndirectLinkTest(idf: String, desired: String, threshold: Double, inDirectLinks: Map[String, Seq[String]],
                          linkType: String): Unit = {
    it should f"have a correct $linkType link for global var ${idf}" in {
      // these are already sorted
      val topScoredLink = inDirectLinks(linkType)
      for (l <- topScoredLink) println(">>" + l)
      topScoredLink.head.split("::").last shouldEqual desired
      // can't get scores for these right now...
    }
  }

  def negativeIndirectLinkTest(idf: String, threshold: Double, indirectLinks: Map[String, Seq[String]],
                             linkType: String): Unit = {
    it should s"have NO ${linkType} link for global var $idf" in {

      // todo: when we get indirect links, need to save idf/score tuples instead of just idf
//      val condition1 = Try(indirectLinks.keys.toList.contains(linkType) should be(false)).isSuccess
//      val condition2 = Try(indirectLinks
//      (linkType).sortBy(_.obj("score").num).reverse.head("score").num > threshold shouldBe false).isSuccess
//      assert(condition1 || condition2)
    }
  }




}
