package org.clulab.aske.automates.alignment

import java.io.File
import ai.lum.common.ConfigUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.aske.automates.apps.{AlignmentArguments, ExtractAndAlign}
import org.clulab.utils.AlignmentJsonUtils
import ai.lum.common.FileUtils._
import org.clulab.aske.automates.TestUtils.TestAlignment
import org.clulab.aske.automates.apps.ExtractAndAlign.{allLinkTypes, whereIsNotGlobalVar}
import org.clulab.embeddings.word2vec.Word2Vec
import org.scalatest.{FlatSpec, Matchers}


class TestAlignFullLink extends TestAlignment {

  val config: Config = ConfigFactory.load("test.conf")
  val alignmentHandler = new AlignmentHandler(config[Config]("alignment"))
  // get general configs
  val serializerName: String = config[String]("apps.serializerName")
  val numAlignments: Int = config[Int]("apps.numAlignments")
  val numAlignmentsSrcToComment: Int = config[Int]("apps.numAlignmentsSrcToComment")
  val scoreThreshold: Int = config[Int]("apps.scoreThreshold")
  val groundToSVO: Boolean = config[Boolean]("apps.groundToSVO")
  val maxSVOgroundingsPerVar: Int = config[Int]("apps.maxSVOgroundingsPerVar")
  val appendToGrFN: Boolean = config[Boolean]("apps.appendToGrFN")

  // alignment-specific configs
  val debug: Boolean = config[Boolean]("alignment.debug")
  val inputDir = new File(getClass.getResource("/").getFile)
  val payLoadFileName: String = config[String]("alignment.unitTestPayload")
  val payloadFile = new File(inputDir, payLoadFileName)
  val payloadPath: String = payloadFile.getAbsolutePath
  val payloadJson: ujson.Value = ujson.read(payloadFile.readString())
  val jsonObj: ujson.Value = payloadJson.obj

  val argsForGrounding: AlignmentArguments = AlignmentJsonUtils.getArgsForAlignment(payloadPath, jsonObj, groundToSVO, serializerName)


  val groundings: ujson.Value = ExtractAndAlign.groundMentions(
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
    groundToSVO,
    maxSVOgroundingsPerVar,
    alignmentHandler,
    Some(numAlignments),
    Some(numAlignmentsSrcToComment),
    scoreThreshold,
    appendToGrFN,
    debug
  )

  val links = groundings.obj("links").arr
  val linkTypes = links.map(_.obj("link_type").str).distinct

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

  val toyGoldR = Map(
    "equation_to_gvar" -> "r",
    "gvar_to_param_setting_via_cpcpt" -> "Infection rate of 0.5",
    "gvar_to_param_setting_via_idfr" -> "r = 1.62 × 10-8",
    "gvar_to_interval_param_setting_via_cpcpt" -> "infection rate is measured at germs per second and ranges between 0.2 and 5.6",
    "gvar_to_unit_via_cpcpt" -> "Infection rate of 0.5 germs per second"
  )

  val toyGoldIndirR = Map(
    "source_to_comment" -> "r_b"
  )

  val idfr = "r"
  val (directLinksForR, indirR) = getLinksForGvar(idfr, links)
  val allToyRLinks = (toyGoldR ++ toyGoldIndirR).toSeq
//  val rLinksGroupedByLinkType =

  var score = 0

  for (key <- toyGoldR.keys) {
//    println("key: " + key)

    if (indirR.contains(key)) {
      // if in indirect links, then it's this complicated check
      val linksOfGivenType = indirR(key).map(_._1.split("::").last)
//      println("links of a given type comment: " + linksOfGivenType.mkString("||"))
      val rank = linksOfGivenType.indexOf(toyGoldR(key)) + 1
      val scoreUpdate = if (rank > 0) 1/rank  else 0
      score += scoreUpdate

    } else if (directLinksForR.contains(key)) {
//      var rank = 0
      // which element in this link type we want to check
      val whichLink = whereIsNotGlobalVar(key)
      val linksOfGivenType = directLinksForR(key).sortBy(_.obj("score").num).reverse.map(_(whichLink).str.split("::").last)
//      println("links of a given type: " + linksOfGivenType)
      val rank = linksOfGivenType.indexOf(toyGoldR(key)) + 1
//      println("key/rank: " + key +  rank)
      val scoreUpdate = if (rank > 0) 1/rank  else 0
      score += scoreUpdate


    } else {
      println("missing link")
    }

  }



  val finalScore = score.toDouble/directLinksForR.keys.toList.length

  println("final score: " + finalScore)

  it should f"have score over threshold" in {
    finalScore > 0.6 shouldBe true
  }

  // composite score for all links? (that is we should have extracted links for everything in the doc); should it be
  // macro or micro? (that is should it be avg of averages for all links or average of all ranked scores? The
  // decision should be about which gives us more information
  // score to account for extra links found (false positives)

}
