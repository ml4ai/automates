package org.clulab.aske.automates.alignment

import java.io.File
import ai.lum.common.ConfigUtils._
import com.typesafe.config.{Config, ConfigFactory, ConfigValueFactory}
import org.clulab.aske.automates.apps.{AlignmentArguments, ExtractAndAlign}
import org.clulab.utils.AlignmentJsonUtils
import ai.lum.common.FileUtils._
import com.fasterxml.jackson.databind.deser.impl.FailingDeserializer
import org.clulab.aske.automates.TestUtils.TestAlignment
import org.clulab.aske.automates.apps.ExtractAndAlign.{COMMENT_TO_GLOBAL_VAR, EQN_TO_GLOBAL_VAR, GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_CONCEPT, GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_IDENTIFIER, GLOBAL_VAR_TO_PARAM_SETTING_VIA_CONCEPT, GLOBAL_VAR_TO_PARAM_SETTING_VIA_IDENTIFIER, GLOBAL_VAR_TO_UNIT_VIA_CONCEPT, GLOBAL_VAR_TO_UNIT_VIA_IDENTIFIER, SRC_TO_COMMENT, allLinkTypes}


class TestAlign extends TestAlignment {

  //  todo:   complete mismatch should not result in 0.5 (like if there's b and a being compared) - it should be 0. How to capture that? maybe intersect?
  // todo: tests for what a global var contains?
  // todo: want tests for indirect links indep of global var - check if highest one for each src var is correct
  // todo: change paths to mention files in the payload (can't be local path)
  // todo: delete unused files in resources

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
  val extractedLinkTypes = links.map(_.obj("link_type").str).distinct

  it should "have all the link types" in {
    val allLinksTypesFlat = allLinkTypes.obj.filter(_._1 != "disabled").obj.flatMap(obj => obj._2.obj.keySet).toSeq//
    val overlap = extractedLinkTypes.intersect(allLinksTypesFlat)
    overlap.length == extractedLinkTypes.length  shouldBe true
    overlap.length == allLinksTypesFlat.length shouldBe true
  }


  {
    val idfr = "R0" // basic reproduction number
    behavior of idfr

    val directDesired = Map(
      GLOBAL_VAR_TO_UNIT_VIA_IDENTIFIER -> ("microbes per year", passingTest),
      GLOBAL_VAR_TO_UNIT_VIA_CONCEPT -> ("m2/year", passingTest),
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_IDENTIFIER -> ("2.71", passingTest),
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_CONCEPT -> ("100", passingTest),
      GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_IDENTIFIER ->("1", passingTest),
      GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_CONCEPT ->("0.5||1", passingTest),
      EQN_TO_GLOBAL_VAR -> ("R_0", passingTest),
      COMMENT_TO_GLOBAL_VAR -> ("Rb", passingTest)
    )
    //
    val indirectDesired = Map(
      SRC_TO_COMMENT -> ("Rb",passingTest)
    )
    //
    val (directLinks, indirLinks) = getLinksForGvar(idfr, links)
    runAllAlignTests(idfr, directLinks, indirLinks, directDesired, indirectDesired)
    //
  }

  {
    val idfr = "c" // number of people exposed
    behavior of idfr

    val directDesired = Map(
      GLOBAL_VAR_TO_UNIT_VIA_CONCEPT -> ("", failingNegative),
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_CONCEPT -> ("", failingNegative),
      GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_CONCEPT -> ("", failingNegative),
      EQN_TO_GLOBAL_VAR -> ("", failingNegative),
      COMMENT_TO_GLOBAL_VAR -> ("", failingNegative)
    )
    //
    val indirectDesired = Map(//Map.empty[String, (String, String)]
      SRC_TO_COMMENT -> ("", failingNegative)
    )
    val (directLinks, indirLinks) = getLinksForGvar(idfr, links)
    runAllAlignTests(idfr, directLinks, indirLinks, directDesired, indirectDesired)
    //
  }
  {
    val idfr = "β" //fixme: maybe if there is very little text for variable, make aligner depend more on the variable?
    behavior of idfr

    val directDesired = Map(
      EQN_TO_GLOBAL_VAR -> ("beta", passingTest),
      COMMENT_TO_GLOBAL_VAR -> ("beta", failingTest),
      GLOBAL_VAR_TO_UNIT_VIA_CONCEPT -> ("", failingNegative),
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_CONCEPT -> ("", failingNegative),
      GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_CONCEPT -> ("", failingNegative)
    )
    //
    val indirectDesired = Map(
      SRC_TO_COMMENT -> ("beta",failingTest)
    )
    //
    val (directLinks, indirLinks) = getLinksForGvar(idfr, links)

//    for (link <- directLinks) {
//      println(">>" + link._1 + " " + link._2.mkString("\n"))
//    }
    runAllAlignTests(idfr, directLinks, indirLinks, directDesired, indirectDesired)
  }


  {
    val idfr = "γ"
    behavior of idfr

    val directDesired = Map(
      EQN_TO_GLOBAL_VAR -> ("gamma", passingTest),
      COMMENT_TO_GLOBAL_VAR -> ("gamma", failingTest),
      GLOBAL_VAR_TO_UNIT_VIA_CONCEPT -> ("", failingNegative),
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_CONCEPT -> ("", failingNegative),
      GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_CONCEPT -> ("", failingNegative)
    )
    //
    val indirectDesired = Map(
      SRC_TO_COMMENT -> ("gamma", failingTest)
    )
    //
    val (directLinks, indirLinks) = getLinksForGvar(idfr, links)
    runAllAlignTests(idfr, directLinks, indirLinks, directDesired, indirectDesired)
  }

  {
    val idfr = "A" // virus
    behavior of idfr

    val directDesired = Map(//Map.empty[String, (String, String)]
      GLOBAL_VAR_TO_UNIT_VIA_CONCEPT -> ("", failingNegative),
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_IDENTIFIER -> ("", failingNegative),
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_CONCEPT -> ("", failingNegative),
      GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_CONCEPT -> ("", failingNegative),
      COMMENT_TO_GLOBAL_VAR -> ("", failingNegative)


    )
    //
    val indirectDesired = Map(//Map.empty[String, (String, String)]
      SRC_TO_COMMENT -> ("", failingNegative)
    )
    //
    val (directLinks, indirLinks) = getLinksForGvar(idfr, links)
    runAllAlignTests(idfr, directLinks, indirLinks, directDesired, indirectDesired)

  }

  {
    val idfr = "a" // removal rate of infectives
    behavior of idfr

    val directDesired = Map(
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_IDENTIFIER -> ("2/3", passingTest), // also this: a = 3
      EQN_TO_GLOBAL_VAR -> ("a", passingTest),
      COMMENT_TO_GLOBAL_VAR -> ("a", passingTest), //make this a same var in comments with modified definition - removal rate of infectives
      GLOBAL_VAR_TO_UNIT_VIA_CONCEPT -> ("", failingNegative),
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_CONCEPT -> ("", failingNegative),
      GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_CONCEPT -> ("", failingNegative),
    )
    //
    val indirectDesired = Map(
      SRC_TO_COMMENT -> ("a",passingTest)
    )
    //
    val (directLinks, indirLinks) = getLinksForGvar(idfr, links)
    runAllAlignTests(idfr, directLinks, indirLinks, directDesired, indirectDesired)
    //
  }

  {
    val idfr = "r" // infection rate
    behavior of idfr

    val directDesired = Map(
      GLOBAL_VAR_TO_UNIT_VIA_IDENTIFIER -> ("germs per second", passingTest),
      GLOBAL_VAR_TO_UNIT_VIA_CONCEPT -> ("germs per second", passingTest),
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_IDENTIFIER -> ("65", passingTest), // also this: r = 9.788 × 10-8
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_CONCEPT -> ("0.5", passingTest),
      GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_IDENTIFIER ->("negative", failingTest), // need processing for word param settings
      GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_CONCEPT ->("0.2||5.6", passingTest), // these may need to be ttwo values separated with ::
      EQN_TO_GLOBAL_VAR -> ("r", passingTest),
      COMMENT_TO_GLOBAL_VAR -> ("inc_inf", passingTest) //make this a diff var in comments - infection rate
    )
    //
    val indirectDesired = Map(
      SRC_TO_COMMENT -> ("inc_inf",passingTest)
    )
    //
    val (directLinks, indirLinks) = getLinksForGvar(idfr, links)
    runAllAlignTests(idfr, directLinks, indirLinks, directDesired, indirectDesired)
    //
  }

  {
    // todo: double-check these links
    val idfr = "I" // infected
    behavior of idfr

    val directDesired = Map(
      GLOBAL_VAR_TO_UNIT_VIA_IDENTIFIER -> ("individuals", failingTest),
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_IDENTIFIER -> ("10", passingTest),
      GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_IDENTIFIER ->("0", failingTest),// in text it's "positive", need something for word to param setting conversion + need to test intervals better, e.g., the first one in tuple is lower bound and second is upper OR it does not matter for align - quality of extractions is in param setting testing; here, the important part is being linked properly
      EQN_TO_GLOBAL_VAR -> ("I", failingTest), // I is not in eq but there's I(0), I(t), and I_P; what to align? Or nothing?
      COMMENT_TO_GLOBAL_VAR -> ("I", failingTest), // make this R is the basic reproduction number in the comments
      GLOBAL_VAR_TO_UNIT_VIA_CONCEPT ->("", failingNegative),
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_CONCEPT ->("", failingNegative),
      GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_CONCEPT ->("", failingNegative)
    )
    //
    val indirectDesired = Map(
      SRC_TO_COMMENT -> ("I",failingTest)
    )
    //
    val (directLinks, indirLinks) = getLinksForGvar(idfr, links)
    runAllAlignTests(idfr, directLinks, indirLinks, directDesired, indirectDesired)
    //
  }

  {
    val idfr = "R"
    behavior of idfr

    val directDesired = Map(
      EQN_TO_GLOBAL_VAR -> ("R", failingTest),
      COMMENT_TO_GLOBAL_VAR -> ("R", failingTest),
      GLOBAL_VAR_TO_UNIT_VIA_IDENTIFIER -> ("", failingNegative),
      GLOBAL_VAR_TO_UNIT_VIA_CONCEPT -> ("", failingNegative),
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_IDENTIFIER -> ("", failingNegative),
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_CONCEPT -> ("", failingNegative),
      GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_CONCEPT -> ("", failingNegative),
    )
    //
    val indirectDesired = Map(
      SRC_TO_COMMENT -> ("R", failingTest)
    )
    //
    val (directLinks, indirLinks) = getLinksForGvar(idfr, links)
    runAllAlignTests(idfr, directLinks, indirLinks, directDesired, indirectDesired)
    //
  }

  {
    val idfr = "τ"
    behavior of idfr

    val directDesired = Map(
      GLOBAL_VAR_TO_UNIT_VIA_IDENTIFIER -> ("mm", passingTest),
      GLOBAL_VAR_TO_UNIT_VIA_CONCEPT -> ("mm", passingTest), //millimeters is also correct; todo: have test accommodate several possible answers
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_IDENTIFIER -> ("450", passingTest),
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_CONCEPT -> ("32", passingTest),
      EQN_TO_GLOBAL_VAR -> ("tau", passingTest),
      COMMENT_TO_GLOBAL_VAR -> ("t_a", passingTest) //make this some other var in comment and source that would align well with the definition - make it same exact definition (transmissibility)
    )
    //
    val indirectDesired = Map(
      SRC_TO_COMMENT -> ("t_a",passingTest)
    )

    val (directLinks, indirLinks) = getLinksForGvar(idfr, links)
    runAllAlignTests(idfr, directLinks, indirLinks, directDesired, indirectDesired)

  }

    {
      val idfr = "S"
      behavior of idfr

      val directDesired = Map(
        GLOBAL_VAR_TO_UNIT_VIA_IDENTIFIER -> ("people", failingTest),
        GLOBAL_VAR_TO_PARAM_SETTING_VIA_IDENTIFIER -> ("6.8 millions", failingTest),
        GLOBAL_VAR_TO_PARAM_SETTING_VIA_CONCEPT -> ("4.5 million", failingTest), //fixme: how did 6.8 get attached to S?
        EQN_TO_GLOBAL_VAR -> ("S", passingTest),
        COMMENT_TO_GLOBAL_VAR -> ("S", failingTest), // make this R is the basic reproduction number in the comments
        GLOBAL_VAR_TO_UNIT_VIA_CONCEPT -> ("", failingNegative),
        GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_CONCEPT -> ("", failingNegative)
      )
      //
      val indirectDesired = Map(
        SRC_TO_COMMENT -> ("S", failingTest)
      )
      //
      val (directLinks, indirLinks) = getLinksForGvar(idfr, links)
      runAllAlignTests(idfr, directLinks, indirLinks, directDesired, indirectDesired)
      //
    }




  //  // template

  //  // template
  //  {
  //    val idfr = "E"
  //    behavior of idfr
  //
  //    val directDesired = Map(
  //      GLOBAL_VAR_TO_UNIT_VIA_IDENTIFIER -> ("E", passingTest),
  //      GLOBAL_VAR_TO_UNIT_VIA_CONCEPT -> ("E", passingTest),
  //      GLOBAL_VAR_TO_PARAM_SETTING_VIA_IDENTIFIER -> ("E", passingTest),
  //      GLOBAL_VAR_TO_PARAM_SETTING_VIA_CONCEPT -> ("E", passingTest),
  //      GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_IDENTIFIER ->("E", passingTest),
  //      GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_CONCEPT ->("E", passingTest),
  //      EQN_TO_GLOBAL_VAR -> ("E", passingTest),
  //      COMMENT_TO_GLOBAL_VAR -> ("E", passingTest)
  //    )
  //    //
  //    val indirectDesired = Map(
  //      SRC_TO_COMMENT -> ("E",passingTest)
  //    )
  //    //
  //val (directLinks, indirLinks) = getLinksForGvar(idfr, links)
  //  runAllTests(idfr, directLinks, indirLinks, directDesired, indirectDesired)
  //    //
  //  }

}
