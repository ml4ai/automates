package org.clulab.aske.automates.alignment

import java.io.File
import ai.lum.common.ConfigUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.aske.automates.apps.{AlignmentArguments, ExtractAndAlign}
import org.clulab.utils.AlignmentJsonUtils
import ai.lum.common.FileUtils._
import org.clulab.aske.automates.TestUtils.TestAlignment
import org.clulab.aske.automates.apps.ExtractAndAlign.allLinkTypes


class TestAlign extends TestAlignment {

// todo: make sure use pairwise aligner for texts

  val config: Config = ConfigFactory.load("test.conf")
  val alignmentHandler = new AlignmentHandler(ConfigFactory.load()[Config]("alignment"))
  val serializerName: String = config[String]("apps.serializerName")
  val numAlignments: Int = config[Int]("apps.numAlignments")
  println("num of al" + numAlignments)
  val numAlignmentsSrcToComment: Int = config[Int]("apps.numAlignmentsSrcToComment")
  val scoreThreshold: Int = config[Int]("apps.scoreThreshold")
  val inputDir = new File(getClass.getResource("/").getFile)
  val payLoadFileName: String = config[String]("alignment.unitTestPayload")
  val debug: Boolean = config[Boolean]("alignment.debug")
  val payloadFile = new File(inputDir, payLoadFileName)
  val payloadPath: String = payloadFile.getAbsolutePath
  val payloadJson: ujson.Value = ujson.read(payloadFile.readString())
  val jsonObj: ujson.Value = payloadJson.obj

  val argsForGrounding: AlignmentArguments = AlignmentJsonUtils.getArgsForAlignment(payloadPath, jsonObj, groundToSVO = false,
    serializerName)


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
    groundToSVO = false,
    5,
    alignmentHandler,
    Some(numAlignments),
    Some(numAlignmentsSrcToComment),
    scoreThreshold,
    appendToGrFN=false,
    debug
  )

  val links = groundings.obj("links").arr
  val extractedLinkTypes = links.map(_.obj("link_type").str).distinct

  it should "have all the link types" in {
    val allLinksTypesFlat = allLinkTypes.obj.filter(_._1 != "disabled").obj.flatMap(obj => obj._2.obj.keySet).toSeq//
    val overlap = extractedLinkTypes.intersect(allLinksTypesFlat)
    overlap.length == extractedLinkTypes.length  shouldBe true
    overlap.length == allLinksTypesFlat.length shouldBe true
  }

  {
    val idfE = "E"
    behavior of idfE

    val directDesired = Map(
      "equation_to_gvar" -> ("E", "passing"),
      "gvar_to_param_setting_via_idfr" -> ("E = 30", "failing"),
      "comment_to_gvar" -> ("E", "passing"),
      "gvar_to_unit_via_cpcpt" -> ("", "failingNegative"),
      "gvar_to_param_setting_via_cpcpt" -> ("", "failingNegative"),
      "gvar_to_interval_param_setting_via_cpcpt" -> ("", "failingNegative")
    )

    val indirectDesired = Map(
      "source_to_comment" -> ("E","failing")
    )

    val (directLinksForE, indirE) = getLinksForGvar("E", links)
    runAllTests(idfE, directLinksForE, indirE, directDesired, indirectDesired)

  }


}
