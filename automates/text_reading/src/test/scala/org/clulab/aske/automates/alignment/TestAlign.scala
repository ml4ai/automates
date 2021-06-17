package org.clulab.aske.automates.alignment

import java.io.File
import ai.lum.common.ConfigUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.aske.automates.apps.ExtractAndAlign
import org.clulab.embeddings.word2vec.Word2Vec
import org.clulab.utils.{AlignmentJsonUtils, Sourcer}
import ai.lum.common.FileUtils._
import org.clulab.aske.automates.TestUtils.TestAlignment
import org.clulab.aske.automates.apps.ExtractAndAlign.allLinkTypes


class TestAlign extends TestAlignment {

  // utils (todo: move to TestUtils)
  // todo: cleanup imports
// todo: get thresholds
  // separate file for eval of links

  // load files/configs

  val config: Config = ConfigFactory.load("/test.conf")
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
      "gvar_to_interval_param_setting_via_idfr" -> ("", "failingNegative")
    )

    val indirectDesired = Map(
      "source_to_comment" -> ("E","failing")
    )

    val (directLinksForE, indirE) = getLinksForGvar("E", links)
    runAllTests(idfE, directLinksForE, indirE, directDesired, indirectDesired)

  }


}
