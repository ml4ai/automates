//package org.clulab.aske.automates.alignment
//
//import ai.lum.common.ConfigUtils._
//import ai.lum.common.FileUtils._
//import com.typesafe.config.{Config, ConfigFactory}
//import org.clulab.aske.automates.TestUtils.getLinksForGvar
//import org.clulab.aske.automates.apps.ExtractAndAlign
//import org.clulab.aske.automates.apps.ExtractAndAlign.{allLinkTypes, whereIsNotGlobalVar}
//import org.clulab.embeddings.word2vec.Word2Vec
//import org.clulab.utils.{AlignmentJsonUtils, Sourcer}
//import org.scalatest.{FlatSpec, Matchers}
//import play.libs.F.Tuple
//import ujson.Value
//
//import java.io.File
//import scala.util.Try
//
//class TestAlignFullLink extends FlatSpec with Matchers {
//
//
//
//  val config = ConfigFactory.load("/test.conf")
//  val numAlignments = 3//config[String]("apps.numAlignments")
//  val numAlignmentsSrcToComment = 1//config[String]("apps.numAlignmentsSrcToComment")
//  val scoreThreshold = 0.0 //config[String]("apps.scoreThreshold")
//
//  val w2v = new Word2Vec(Sourcer.sourceFromResource("/vectors.txt"), None) //todo: read this from test conf (after adding this to test conf)
////  lazy val proc = TestUtils.newOdinSystem(config).proc
//  val inputDir = new File(getClass.getResource("/").getFile)
//  val files = inputDir.listFiles()
//  for (f <- files) println(">>>", f)
//
//  println("++>>", inputDir)
//
//  // read in all related docs or maybe read in just a sample payload - that should make sense
//  // make it as close as possivle to the actual endpoint while still mainly testing the ExtractAndAlign.groundMentions method (to get texts of links, need to run in debug mode)
//  // the rest will be tested on paul's end
//
//  //lazy val commentReader = OdinEngine.fromConfigSection("CommentEngine")
//  val alignmentHandler = new AlignmentHandler(ConfigFactory.load()[Config]("alignment"))
//  val serializerName = "AutomatesJSONSerializer" //todo: read from config
//  val payloadFile = new File(inputDir, "double-epidemic-chime-align_payload-for-testing.json")
//  val payloadPath = payloadFile.getAbsolutePath
//  val payloadJson = ujson.read(payloadFile.readString())
//  val jsonObj = payloadJson.obj
//
//  val argsForGrounding = AlignmentJsonUtils.getArgsForAlignment(payloadPath, jsonObj, false, serializerName)
//
//
//  val groundings = ExtractAndAlign.groundMentions(
//    payloadJson,
//    argsForGrounding.identifierNames,
//    argsForGrounding.identifierShortNames,
//    argsForGrounding.descriptionMentions,
//    argsForGrounding.parameterSettingMentions,
//    argsForGrounding.intervalParameterSettingMentions,
//    argsForGrounding.unitMentions,
//    argsForGrounding.commentDescriptionMentions,
//    argsForGrounding.equationChunksAndSource,
//    argsForGrounding.svoGroundings,
//    false,
//    3,
//    alignmentHandler,
//    Some(5),
//    Some(2),//Some(numAlignmentsSrcToComment),
//    scoreThreshold,
//    appendToGrFN=false,
//    debug=true
//  )
//
//  val links = groundings.obj("links").arr
//  val linkTypes = links.map(_.obj("link_type").str).distinct
//
//  val toyGoldIt = Map(
////    "equation_to_gvar" -> "frac{dIp}{dt}",
////    "gvar_to_interval_param_setting_via_idfr" -> "R0>1",
////    "comment_to_gvar" -> "inc_exp_a",
////    "source_to_comment" -> "inc_exp_a",
////    "gvar_to_unit_via_idfr" -> "details of the dS dt rS t I t r S t I t dE dt rS t I t bE t bE t aI t dR dt aI t dt r S t I t"
//
//    "equation_to_gvar" -> "frac{dI}{dt}",
//    "gvar_to_interval_param_setting_via_idfr" -> "R0>1",
//    "comment_to_gvar" -> "inc_exp_a",
//    "source_to_comment" -> "inc_exp_a",
//    "gvar_to_unit_via_idfr" -> "details of the dS dt rS t I t r S t I t dE dt rS t I t bE t bE t aI t dR dt aI t dt r S t I t"
//  )
////  val allToyItLinks = (it_links ++ allIndirectLinksForITLinks).toSeq
//
//
////  var score = 0
////
////  for (key <- toyGoldIt.keys) {
//////    println("key: " + key)
////
////    if (allIndirectLinksForITLinks.contains(key)) {
////      // if in indirect links, then it's this complicated check
////      val linksOfGivenType = allIndirectLinksForITLinks(key).map(_.split("::").last)
//////      println("links of a given type comment: " + linksOfGivenType.mkString("||"))
////      val rank = linksOfGivenType.indexOf(toyGoldIt(key)) + 1
////      val scoreUpdate = if (rank > 0) 1/rank  else 0
////      score += scoreUpdate
////
////    } else if (itLinksGroupedByLinkType.contains(key)) {
//////      var rank = 0
////      // which element in this link type we want to check
////      val whichLink = key match {
////        case "equation_to_gvar" |  "comment_to_gvar"  => "element_1"
////        case "gvar_to_interval_param_setting_via_idfr" | "gvar_to_unit_via_idfr"  => "element_2"
////        case _ => ???
////      }
////      val linksOfGivenType = itLinksGroupedByLinkType(key).sortBy(_.obj("score").num).reverse.map(_(whichLink).str.split("::").last)
//////      println("links of a given type: " + linksOfGivenType)
////      val rank = linksOfGivenType.indexOf(toyGoldIt(key)) + 1
//////      println("key/rank: " + key +  rank)
////      val scoreUpdate = if (rank > 0) 1/rank  else 0
////      score += scoreUpdate
////
////
////    } else {
////      println("missing link")
////    }
////
////  }
////
////
////
////  val finalScore = score.toDouble/toyGoldIt.keys.toList.length
//
////  println("final score: " + finalScore)
//
//
//
//}
