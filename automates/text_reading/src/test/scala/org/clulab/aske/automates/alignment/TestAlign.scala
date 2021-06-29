package org.clulab.aske.automates.alignment

import java.io.File
import ai.lum.common.ConfigUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.aske.automates.apps.{AlignmentArguments, ExtractAndAlign}
import org.clulab.utils.AlignmentJsonUtils
import ai.lum.common.FileUtils._
import org.clulab.aske.automates.TestUtils.TestAlignment
import org.clulab.aske.automates.apps.ExtractAndAlign.{COMMENT_TO_GLOBAL_VAR, EQN_TO_GLOBAL_VAR, GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_CONCEPT, GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_IDENTIFIER, GLOBAL_VAR_TO_PARAM_SETTING_VIA_CONCEPT, GLOBAL_VAR_TO_PARAM_SETTING_VIA_IDENTIFIER, GLOBAL_VAR_TO_UNIT_VIA_CONCEPT, GLOBAL_VAR_TO_UNIT_VIA_IDENTIFIER, SRC_TO_COMMENT, allLinkTypes}


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


  // template
  {
    val idfr = "R0" // basic reproduction number
    behavior of idfr

    val directDesired = Map(
      GLOBAL_VAR_TO_UNIT_VIA_IDENTIFIER -> ("microbes per year", "passing"),
      GLOBAL_VAR_TO_UNIT_VIA_CONCEPT -> ("m2/year", "passing"),
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_IDENTIFIER -> ("2.71", "passing"),
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_CONCEPT -> ("100", "passing"),
      GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_IDENTIFIER ->("1", "passing"),
      GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_CONCEPT ->("0.5 and 1", "passing"), // these may need to be ttwo values separated with ::
      EQN_TO_GLOBAL_VAR -> ("R_0", "passing"), // think about this
      COMMENT_TO_GLOBAL_VAR -> ("R_0", "passing") // make this R is the basic reproduction number in the comments
    )
    //
    val indirectDesired = Map(
      SRC_TO_COMMENT -> ("R_0","passing")
    )
    //
    val (directLinks, indirLinks) = getLinksForGvar(idfr, links)
    runAllTests(idfr, directLinks, indirLinks, directDesired, indirectDesired)
    //
  }

  {
    // todo: make fake comment for this and src code var
    val idfr = "c" // number of people exposed
    behavior of idfr

    val directDesired = Map.empty[String, (String, String)]
    //
    val indirectDesired = Map.empty[String, (String, String)]
    //
    val (directLinks, indirLinks) = getLinksForGvar(idfr, links)
    runAllTests(idfr, directLinks, indirLinks, directDesired, indirectDesired)
    //
  }
  {
    val idfr = "β"
    behavior of idfr

    val directDesired = Map(
      EQN_TO_GLOBAL_VAR -> ("beta", "passing"), // think about this
      COMMENT_TO_GLOBAL_VAR -> ("beta", "passing") // make this R is the basic reproduction number in the comments
    )
    //
    val indirectDesired = Map(
      SRC_TO_COMMENT -> ("beta","passing")
    )
    //
    val (directLinks, indirLinks) = getLinksForGvar(idfr, links)
    runAllTests(idfr, directLinks, indirLinks, directDesired, indirectDesired)
  }

  {
    val idfr = "γ"
    behavior of idfr

    val directDesired = Map(
      EQN_TO_GLOBAL_VAR -> ("gamma", "passing"), // think about this
      COMMENT_TO_GLOBAL_VAR -> ("gamma", "passing") // make this R is the basic reproduction number in the comments
    )
    //
    val indirectDesired = Map(
      SRC_TO_COMMENT -> ("gamma","passing")
    )
    //
    val (directLinks, indirLinks) = getLinksForGvar(idfr, links)
    runAllTests(idfr, directLinks, indirLinks, directDesired, indirectDesired)
  }

  {
    val idfr = "A" // virus
    behavior of idfr

    val directDesired = Map.empty[String, (String, String)]
    //
    val indirectDesired = Map.empty[String, (String, String)]
    //
    val (directLinks, indirLinks) = getLinksForGvar(idfr, links)
    runAllTests(idfr, directLinks, indirLinks, directDesired, indirectDesired)

  }

  {
    val idfr = "a" // removal rate of infectives
    behavior of idfr

    val directDesired = Map(
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_IDENTIFIER -> ("2/3", "passing"), // also this: a = 3
      EQN_TO_GLOBAL_VAR -> ("a", "passing"),
      COMMENT_TO_GLOBAL_VAR -> ("a", "passing") //make this a same var in comments with modified definition - removal rate of infectives
    )
    //
    val indirectDesired = Map(
      SRC_TO_COMMENT -> ("a","passing")
    )
    //
    val (directLinks, indirLinks) = getLinksForGvar(idfr, links)
    runAllTests(idfr, directLinks, indirLinks, directDesired, indirectDesired)
    //
  }

  {
    val idfr = "r" // infection rate
    behavior of idfr

    val directDesired = Map(
      GLOBAL_VAR_TO_UNIT_VIA_IDENTIFIER -> ("germs per second", "passing"),
      GLOBAL_VAR_TO_UNIT_VIA_CONCEPT -> ("germs per second", "passing"),
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_IDENTIFIER -> ("0.5", "passing"), // also this: r = 9.788 × 10-8
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_CONCEPT -> ("65", "passing"),
      GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_IDENTIFIER ->("negative", "passing"),
      GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_CONCEPT ->("0.2 and 5.6", "passing"), // these may need to be ttwo values separated with ::
      EQN_TO_GLOBAL_VAR -> ("r", "passing"),
      COMMENT_TO_GLOBAL_VAR -> ("inc_inf", "passing") //make this a diff var in comments - infection rate
    )
    //
    val indirectDesired = Map(
      SRC_TO_COMMENT -> ("inc_inf","passing")
    )
    //
    val (directLinks, indirLinks) = getLinksForGvar(idfr, links)
    runAllTests(idfr, directLinks, indirLinks, directDesired, indirectDesired)
    //
  }

  {
    //todo: need a test with missing indir and comment links
    val idfr = "I"
    behavior of idfr

    val directDesired = Map(
      GLOBAL_VAR_TO_UNIT_VIA_IDENTIFIER -> ("individuals", "passing"),
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_IDENTIFIER -> ("10", "passing"),
      GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_IDENTIFIER ->("0", "passing"),// in text it's "positive", need something for word to param setting conversion + need to test intervals better, e.g., the first one in tuple is lower bound and second is upper OR it does not matter for align - quality of extractions is in param setting testing; here, the important part is being linked properly
      EQN_TO_GLOBAL_VAR -> ("I", "passing"), // think about this
      COMMENT_TO_GLOBAL_VAR -> ("I", "passing") // make this R is the basic reproduction number in the comments
    )
    //
    val indirectDesired = Map(
      SRC_TO_COMMENT -> ("I","passing")
    )
    //
    val (directLinks, indirLinks) = getLinksForGvar(idfr, links)
    runAllTests(idfr, directLinks, indirLinks, directDesired, indirectDesired)
    //
  }

  {
    val idfr = "R"
    behavior of idfr

    val directDesired = Map(
      EQN_TO_GLOBAL_VAR -> ("R", "passing"),
      COMMENT_TO_GLOBAL_VAR -> ("R", "passing")
    )
    //
    val indirectDesired = Map(
      SRC_TO_COMMENT -> ("R","passing")
    )
    //
    val (directLinks, indirLinks) = getLinksForGvar(idfr, links)
    runAllTests(idfr, directLinks, indirLinks, directDesired, indirectDesired)
    //
  }

  {
    val idfr = "τ"
    behavior of idfr

    val directDesired = Map(
      GLOBAL_VAR_TO_UNIT_VIA_IDENTIFIER -> ("mm", "passing"),
      GLOBAL_VAR_TO_UNIT_VIA_CONCEPT -> ("millimeters", "passing"),
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_IDENTIFIER -> ("450", "passing"),
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_CONCEPT -> ("32", "passing"),
      EQN_TO_GLOBAL_VAR -> ("tau", "passing"),
      COMMENT_TO_GLOBAL_VAR -> ("t_a", "passing") //make this some other var in comment and source that would align well with the definition - make it same exact definition (transmissibility)
    )
    //
    val indirectDesired = Map(
      SRC_TO_COMMENT -> ("t_a","passing")
    )
    //
    val (directLinks, indirLinks) = getLinksForGvar(idfr, links)
    runAllTests(idfr, directLinks, indirLinks, directDesired, indirectDesired)
    //
  }

  // template
  {
    val idfr = "S"
    behavior of idfr

    val directDesired = Map(
      GLOBAL_VAR_TO_UNIT_VIA_IDENTIFIER -> ("people", "passing"),
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_IDENTIFIER -> ("6.8 millions", "passing"),
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_CONCEPT -> ("4.5 million", "passing"),
      EQN_TO_GLOBAL_VAR -> ("S", "passing"), // think about this
      COMMENT_TO_GLOBAL_VAR -> ("S", "passing") // make this R is the basic reproduction number in the comments
    )
    //
    val indirectDesired = Map(
      SRC_TO_COMMENT -> ("S","passing")
    )
    //
    val (directLinks, indirLinks) = getLinksForGvar(idfr, links)
    runAllTests(idfr, directLinks, indirLinks, directDesired, indirectDesired)
    //
  }



//  // template
//  {
//    val idfr = "E"
//    behavior of idfr
//
//    val directDesired = Map(
//      GLOBAL_VAR_TO_UNIT_VIA_IDENTIFIER -> ("E", "passing"),
//      GLOBAL_VAR_TO_UNIT_VIA_CONCEPT -> ("E", "passing"),
//      GLOBAL_VAR_TO_PARAM_SETTING_VIA_IDENTIFIER -> ("E", "passing"),
//      GLOBAL_VAR_TO_PARAM_SETTING_VIA_CONCEPT -> ("E", "passing"),
//      GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_IDENTIFIER ->("E", "passing"),
//      GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_CONCEPT ->("E", "passing"),
//      EQN_TO_GLOBAL_VAR -> ("E", "passing"),
//      COMMENT_TO_GLOBAL_VAR -> ("E", "passing")
//    )
//    //
//    val indirectDesired = Map(
//      SRC_TO_COMMENT -> ("E","passing")
//    )
//    //
//val (directLinks, indirLinks) = getLinksForGvar(idfr, links)
//  runAllTests(idfr, directLinks, indirLinks, directDesired, indirectDesired)
//    //
//  }

    // todo: do we want a few def span tests here? like what a global var should contain? - yes

//  {
//    val idfr = "E"
//    behavior of idfr
//
//    val directDesired = Map(
//      "equation_to_gvar" -> ("E", "passing"),
//      "gvar_to_param_setting_via_idfr" -> ("E = 30", "failing"),
//      "comment_to_gvar" -> ("E", "passing"),
//      "gvar_to_unit_via_cpcpt" -> ("", "failingNegative"),
//      "gvar_to_param_setting_via_cpcpt" -> ("", "failingNegative"),
//      "gvar_to_interval_param_setting_via_cpcpt" -> ("", "failingNegative")
//    )
//
//    val indirectDesired = Map(
//      "source_to_comment" -> ("E","failing")
//    )
//
//    val (directLinksForE, indirE) = getLinksForGvar(idfr, links)
//    runAllTests(idfr, directLinksForE, indirE, directDesired, indirectDesired)
//
//  }

//  {
//    val idfr = "r"
//    behavior of idfr
//
//    val directDesired = Map(
//      "equation_to_gvar" -> ("r", "passing"),
//      "gvar_to_param_setting_via_cpcpt" -> ("Infection rate of 0.5", "passing"),
//      "gvar_to_param_setting_via_idfr" -> ("r = 1.62 × 10-8", "passing"),
//      "gvar_to_interval_param_setting_via_cpcpt" -> ("infection rate is measured at germs per second and ranges between 0.2 and 5.6", "passing"),
//      "gvar_to_unit_via_cpcpt" -> ("Infection rate of 0.5 germs per second", "passing"),
//      "comment_to_gvar" -> ("r_b", "passing"),
//      "gvar_to_interval_param_setting_via_idfr" -> ("", "failingNegative")
//    )
////
//    val indirectDesired = Map(
//      "source_to_comment" -> ("r_b","passing")
//    )
////
//    val (directLinksForE, indirE) = getLinksForGvar(idfr, links)
//    runAllTests(idfr, directLinksForE, indirE, directDesired, indirectDesired)
////
//  }


//  {
//    val idfr = "S"
//    behavior of idfr
//
//    val directDesired = Map(
//      "equation_to_gvar" -> ("S", "passing"),
////      "gvar_to_param_setting_via_cpcpt" -> ("Infection rate of 0.5", "passing"),
////      "gvar_to_param_setting_via_idfr" -> ("r = 1.62 × 10-8", "passing"),
////      "gvar_to_interval_param_setting_via_cpcpt" -> ("infection rate is measured at germs per second and ranges between 0.2 and 5.6", "passing"),
////      "gvar_to_unit_via_cpcpt" -> ("Infection rate of 0.5 germs per second", "passing"),
//      "comment_to_gvar" -> ("S_t", "passing"),
////      "gvar_to_interval_param_setting_via_idfr" -> ("", "failingNegative")
//    )
//    //
//    val indirectDesired = Map(
//      "source_to_comment" -> ("S_t","passing")
//    )
//    //
//    val (directLinksForE, indirE) = getLinksForGvar(idfr, links)
//    runAllTests(idfr, directLinksForE, indirE, directDesired, indirectDesired)
//    //
//  }
}
