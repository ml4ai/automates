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

  // todo: pass arg type somewhere to only get text of that arg in tests
  // todo: fix order of indir links
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

  println("grounding keys: " + groundings.obj.keySet.mkString("||"))

  val links = groundings.obj("links").arr
  val extractedLinkTypes = links.map(_.obj("link_type").str).distinct

  it should "have all the link types" in {
    val allLinksTypesFlat = allLinkTypes.obj.filter(_._1 != "disabled").obj.flatMap(obj => obj._2.obj.keySet).toSeq//
    val overlap = extractedLinkTypes.intersect(allLinksTypesFlat)
    overlap.length == extractedLinkTypes.length  shouldBe true
    overlap.length == allLinksTypesFlat.length shouldBe true
  }

  {
    val idfr = "E"
    behavior of idfr

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

    val (directLinksForE, indirE) = getLinksForGvar(idfr, links)
    runAllTests(idfr, directLinksForE, indirE, directDesired, indirectDesired)

  }

  {
    val idfr = "r"
    behavior of idfr

    val directDesired = Map(
      "equation_to_gvar" -> ("r", "passing"),
      "gvar_to_param_setting_via_cpcpt" -> ("Infection rate of 0.5", "passing"),
      "gvar_to_param_setting_via_idfr" -> ("r = 1.62 × 10-8", "passing"),
      "gvar_to_interval_param_setting_via_cpcpt" -> ("infection rate is measured at germs per second and ranges between 0.2 and 5.6", "passing"),
      "gvar_to_unit_via_cpcpt" -> ("Infection rate of 0.5 germs per second", "passing"),
      "comment_to_gvar" -> ("r_b", "passing"),
      "gvar_to_interval_param_setting_via_idfr" -> ("", "failingNegative")
    )
//
    val indirectDesired = Map(
      "source_to_comment" -> ("r_b","failing") // fails bc of wrong indir link ordering
    )
//
    val (directLinksForE, indirE) = getLinksForGvar(idfr, links)
    runAllTests(idfr, directLinksForE, indirE, directDesired, indirectDesired)
//
  }

}
