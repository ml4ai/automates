package org.clulab.aske.automates.alignment

import java.io.File
import ai.lum.common.ConfigUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.aske.automates.apps.{AlignmentArguments, ExtractAndAlign}
import org.clulab.utils.{AlignmentJsonUtils, Sourcer}
import ai.lum.common.FileUtils._
import org.clulab.aske.automates.TestUtils.TestAlignment
import org.clulab.aske.automates.apps.ExtractAndAlign.{COMMENT_TO_GLOBAL_VAR, EQN_TO_GLOBAL_VAR, GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_CONCEPT, GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_IDENTIFIER, GLOBAL_VAR_TO_PARAM_SETTING_VIA_CONCEPT, GLOBAL_VAR_TO_PARAM_SETTING_VIA_IDENTIFIER, GLOBAL_VAR_TO_UNIT_VIA_CONCEPT, GLOBAL_VAR_TO_UNIT_VIA_IDENTIFIER, SRC_TO_COMMENT, allLinkTypes}
import org.clulab.embeddings.word2vec.Word2Vec

/* Tests the alignment payload created based on the toy double-epidemic-and-chime files in /test/resources;
  should changes need to be made to the toy document, the latex template is stored under /test/resources/toy_document_tex;
  if changes are made, the new pdf will need to be processed with science parse (or cosmos) and the payload will need to be recreated
  (can use align_experiment.py for that); the sample grfn is only there so that align_experiment is runnable---copy the testing source variables from the testing payload and paste those into the newly created payload;
  Currently, there are three types of tests:
  1) the test that checks that all supported links are made (the toy document contains all of them); the toy document will need to be updated if new link types are added;
  2) a set of tests (one for every identifier that occurs in the toy doc) that check if the identifier got correct alignments for every link type (template at the bottom of the file; to ignore negative tests, add a line like this to direct or indirect desired maps: <link_type> -> ("", failingNegative)); if there are two possible values, can add them in desired as a "::"-separated string; interval values are "||"-separated;
  3) tests for comment_to_gvar tests (the only type of indirect link we have now); there are few because the alignment for them is very basic and whatever can go wrong will be obvious from these two tests.

 */
class TestAlign extends TestAlignment {

  val config: Config = ConfigFactory.load("test.conf")
  val vectors: String = config[String]("alignment.w2vPath")
  val w2v = new Word2Vec(Sourcer.sourceFromResource(vectors), None)
  val relevantArgs: List[String] = config[List[String]]("alignment.relevantArgs")
  val alignmentHandler = new AlignmentHandler(w2v, relevantArgs.toSet)
  // get general configs
  val serializerName: String = config[String]("apps.serializerName")
  val numAlignments: Int = config[Int]("apps.numAlignments")
  val numAlignmentsSrcToComment: Int = config[Int]("apps.numAlignmentsSrcToComment")
  val scoreThreshold: Int = config[Int]("apps.scoreThreshold")
  val groundToSVO: Boolean = config[Boolean]("apps.groundToSVO")
  val groundToWiki: Boolean = false //config[Boolean]("apps.groundToWiki")
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

  val argsForGrounding: AlignmentArguments = AlignmentJsonUtils.getArgsForAlignment(payloadPath, jsonObj, groundToSVO, groundToWiki, serializerName)

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
    argsForGrounding.wikigroundings,
    groundToSVO,
    groundToWiki,
    saveWikiGroundings = false,
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
    val allLinksTypesFlat = allLinkTypes.obj.filter(_._1 != "disabled").obj.flatMap(obj => obj._2.obj.keySet).toSeq
    val overlap = extractedLinkTypes.intersect(allLinksTypesFlat)
    overlap.length == extractedLinkTypes.length  shouldBe true
    overlap.length == allLinksTypesFlat.length shouldBe true
  }


  {
    val idfr = "R0" // basic reproduction number
    behavior of idfr

    val directDesired = Map(
      GLOBAL_VAR_TO_UNIT_VIA_IDENTIFIER -> ("microbes per year::mm", passingTest),
      GLOBAL_VAR_TO_UNIT_VIA_CONCEPT -> ("m2/year", passingTest),
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_IDENTIFIER -> ("2.71", passingTest),
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_CONCEPT -> ("100", passingTest),
      GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_IDENTIFIER ->("1", passingTest),
      GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_CONCEPT ->("0.5||1", passingTest),
      EQN_TO_GLOBAL_VAR -> ("R_0", passingTest),
      COMMENT_TO_GLOBAL_VAR -> ("Rb", passingTest)
    )

    val indirectDesired = Map(
      SRC_TO_COMMENT -> ("Rb",passingTest)
    )

    val (directLinks, indirLinks) = getLinksForGvar(idfr, links)
    runAllAlignTests(idfr, directLinks, indirLinks, directDesired, indirectDesired)

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

    val indirectDesired = Map(//Map.empty[String, (String, String)]
      SRC_TO_COMMENT -> ("", failingNegative)
    )
    val (directLinks, indirLinks) = getLinksForGvar(idfr, links)
    runAllAlignTests(idfr, directLinks, indirLinks, directDesired, indirectDesired)

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

    val indirectDesired = Map(
      SRC_TO_COMMENT -> ("beta",failingTest)
    )
    val (directLinks, indirLinks) = getLinksForGvar(idfr, links)
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

    val indirectDesired = Map(
      SRC_TO_COMMENT -> ("gamma", failingTest)
    )

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

    val indirectDesired = Map(//Map.empty[String, (String, String)]
      SRC_TO_COMMENT -> ("", failingNegative)
    )

    val (directLinks, indirLinks) = getLinksForGvar(idfr, links)
    runAllAlignTests(idfr, directLinks, indirLinks, directDesired, indirectDesired)

  }

  {
    val idfr = "a" // removal rate of infectives
    behavior of idfr

    val directDesired = Map(
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_IDENTIFIER -> ("2/3::3", passingTest),
      EQN_TO_GLOBAL_VAR -> ("a", passingTest),
      COMMENT_TO_GLOBAL_VAR -> ("a", passingTest),
      GLOBAL_VAR_TO_UNIT_VIA_CONCEPT -> ("", failingNegative),
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_CONCEPT -> ("", failingNegative),
      GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_CONCEPT -> ("", failingNegative),
    )

    val indirectDesired = Map(
      SRC_TO_COMMENT -> ("a",passingTest)
    )

    val (directLinks, indirLinks) = getLinksForGvar(idfr, links)
    runAllAlignTests(idfr, directLinks, indirLinks, directDesired, indirectDesired)

  }

  {
    val idfr = "r" // infection rate
    behavior of idfr

    val directDesired = Map(
      GLOBAL_VAR_TO_UNIT_VIA_IDENTIFIER -> ("germs per second", passingTest),
      GLOBAL_VAR_TO_UNIT_VIA_CONCEPT -> ("germs per second", passingTest),
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_IDENTIFIER -> ("65::9.788 × 10-8", passingTest),
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_CONCEPT -> ("0.5", passingTest),
      GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_IDENTIFIER ->("negative", failingTest), // need processing for word param settings
      GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_CONCEPT ->("0.2||5.6", passingTest),
      EQN_TO_GLOBAL_VAR -> ("r", passingTest),
      COMMENT_TO_GLOBAL_VAR -> ("inc_inf", failingTest) // got misaligned to 'removal rate of infectives'
    )

    val indirectDesired = Map(
      SRC_TO_COMMENT -> ("inc_inf",failingTest)
    )

    val (directLinks, indirLinks) = getLinksForGvar(idfr, links)
    runAllAlignTests(idfr, directLinks, indirLinks, directDesired, indirectDesired)

  }

  {

    val idfr = "I" // infected
    behavior of idfr

    val directDesired = Map(
      GLOBAL_VAR_TO_UNIT_VIA_IDENTIFIER -> ("individuals", failingTest),
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_IDENTIFIER -> ("10", passingTest),
      GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_IDENTIFIER ->("0", failingTest),// in text it's "positive", need something for word to param setting conversion + need to test intervals better, e.g., the first one in tuple is lower bound and second is upper OR it does not matter for align - quality of extractions is in param setting testing; here, the important part is being linked properly
      EQN_TO_GLOBAL_VAR -> ("I", failingTest), // I is not in eq but there's I(0), I(t), and I_P; what to align? Or nothing?
      COMMENT_TO_GLOBAL_VAR -> ("I", failingTest),
      GLOBAL_VAR_TO_UNIT_VIA_CONCEPT ->("", failingNegative),
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_CONCEPT ->("", failingNegative),
      GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_CONCEPT ->("", failingNegative)
    )

    val indirectDesired = Map(
      SRC_TO_COMMENT -> ("I",failingTest)
    )

    val (directLinks, indirLinks) = getLinksForGvar(idfr, links)
    runAllAlignTests(idfr, directLinks, indirLinks, directDesired, indirectDesired)

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

    val indirectDesired = Map(
      SRC_TO_COMMENT -> ("R", failingTest)
    )

    val (directLinks, indirLinks) = getLinksForGvar(idfr, links)
    runAllAlignTests(idfr, directLinks, indirLinks, directDesired, indirectDesired)

  }

  {
    val idfr = "τ"
    behavior of idfr

    val directDesired = Map(
      GLOBAL_VAR_TO_UNIT_VIA_IDENTIFIER -> ("mm", passingTest),
      GLOBAL_VAR_TO_UNIT_VIA_CONCEPT -> ("mm::millimeters", passingTest), // both values possible
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_IDENTIFIER -> ("450", passingTest),
      GLOBAL_VAR_TO_PARAM_SETTING_VIA_CONCEPT -> ("32", passingTest),
      EQN_TO_GLOBAL_VAR -> ("tau", passingTest),
      COMMENT_TO_GLOBAL_VAR -> ("t_a", passingTest)
    )

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
        COMMENT_TO_GLOBAL_VAR -> ("S", failingTest),
        GLOBAL_VAR_TO_UNIT_VIA_CONCEPT -> ("", failingNegative),
        GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_CONCEPT -> ("", failingNegative)
      )

      val indirectDesired = Map(
        SRC_TO_COMMENT -> ("S", failingTest)
      )

      val (directLinks, indirLinks) = getLinksForGvar(idfr, links)
      runAllAlignTests(idfr, directLinks, indirLinks, directDesired, indirectDesired)

    }

  /* INDIRECT LINK TESTS
  for now, the only indirect link is source to comment
   */
  val src_comment_links = links.filter(_.obj("link_type").str == SRC_TO_COMMENT)

  it should "have a src to comment element for source variable a" in {
    src_comment_links.exists(l => l.obj("element_1").str.split("::").last == "a" & l.obj("element_2").str.split("::").last == "a" && l.obj("score").num == 1) shouldBe true
  }

  it should "have a src to comment element for source variable gamma" in {
    src_comment_links.exists(l => l.obj("element_1").str.split("::").last == "gamma" & l.obj("element_2").str.split("::").last == "gamma" && l.obj("score").num == 1) shouldBe true
  }



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
  //  val (directLinks, indirLinks) = getLinksForGvar(idfr, links)
  //  runAllTests(idfr, directLinks, indirLinks, directDesired, indirectDesired)
  //    //
  //  }

}
