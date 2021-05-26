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

  val payloadPath = "/home/alexeeva/Repos/automates/automates/text_reading/src/test/resources/2003-double-epidemic-sample-payload.json"
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

  println(argsForGrounding + "<<<<===")

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
    Some(numAlignmentsSrcToComment),
    scoreThreshold,
    appendToGrFN=false,
    debug=true
  )

  println("groundings " + groundings)




  //  val distinctUids = json.obj("links").arr.map(_.obj.)
//  println("<<<>>>" + json.obj("links").arr.map())
  // this one only makes sense if we dump the results of alignment and then read them in,
  // which we might not need because there's no separate method for dumping the links to test
//  it should "contain links" in {
//    json.obj.keys should contain("links")
//  }
//
//  println("json keys: " + json.obj.keys.mkString("||"))

  val links = groundings.obj("links").arr
  println("===")

  println("->" + links)

  val gv = findGlobalVars(links)



  val linkTypes = links.map(_.obj("link_type").str).distinct

  println(linkTypes + "<<")

  val (withGvarLinkTypes, otherLinksTypes) = linkTypes.partition(_.contains("gvar"))


  println("links head: " + links.head)

  val i_t_links = links.filter(l => l.obj("element_1").str.contains("I(t)") || l.obj("element_2").str.contains("I(t)")).groupBy(_.obj("link_type").str)

  for (gr <- i_t_links) {
    for (i <- gr._2.sortBy(_.obj("score").num)) {
      println(i)
    }
  }


  val src_comment_links = links.filter(_.obj("link_type").str == "source_to_comment")

//  for (scl <- src_comment_links) println(scl)

  println("sample link" + links.head.obj.toString())

  println(src_comment_links.head.obj("element_1").str)

  // try str.split("::").last == "s_t"
  it should "have an s_t src to comment element" in {
    src_comment_links.exists(l => l.obj("element_1").str.contains("s_t") & l.obj("element_2").str.contains("S_t         Current count of individuals that are susceptible to either disease") && l.obj("score").num > 0.8) shouldBe true

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




//  val alignments = ExtractAndAlign.groundMentions(
//    grfn: Value,
//    variableNames: Option[Seq[String]],
//    variableShortNames: Option[Seq[String]],
//    descriptionMentions: Option[Seq[Mention]],
//    parameterSettingMention: Option[Seq[Mention]],
//    intervalParameterSettingMentions: Option[Seq[Mention]],
//    unitMentions: Option[Seq[Mention]],
//    commentDescriptionMentions: Option[Seq[Mention]],
//    equationChunksAndSource: Option[Seq[(String, String)]],
//    SVOgroundings: Option[ArrayBuffer[(String, Seq[sparqlResult])]],
//    groundToSVO: Boolean,
//    maxSVOgroundingsPerVar: Int,
//    alignmentHandler: AlignmentHandler,
//    numAlignments: Option[Int],
//    numAlignmentsSrcToComment: Option[Int],
//    scoreThreshold: Double = 0.0,
//  appendToGrFN: Boolean,
//  debug: Boolean
//  )
//
//  val srcTexts = Seq(
//    "I have a cat",
//    "I have a house"
//  )
//
//  val dstTexts = Seq(
//    "my kitten is friendly",
//    "I bought a condo"
//  )
//
//  val aligner = new PairwiseW2VAligner(w2v, Set("variable", "description"))
//  val mapping = aligner.alignTexts(srcTexts, dstTexts)
//  println(mapping)
//
//  it should "generate exhaustive alignemnts" in {
//    mapping.length should be (4)
//  }
//
//  ignore should "compare the texts with w2v properly" in {
//    val scores = mapping.map(a => ((a.src, a.dst), a.score)).toMap
//    val catKitten = scores((0,0))
//    val catcondo = scores((0,1))
//    val houseKitten = scores((1,0))
//    val houseCondo = scores((1,1))
//    catKitten should be > catcondo
//    houseCondo should be > houseKitten
//  }
//
//  it should "extract relevant portions of mentions" in {
//    //    "words" : [ "TEMPMIN", "is", "the", "minimum", "temperature", "if", "it", "'s", "a", "Friday", "." ],
//    val doc1 = jsonStringToDocument("{\"sentences\":[{\"words\":[\"TEMPMIN\",\"is\",\"the\",\"minimum\",\"temperature\",\"if\",\"it\",\"'s\",\"a\",\"Friday\",\".\"],\"startOffsets\":[0,8,11,15,23,35,38,40,43,45,51],\"endOffsets\":[7,10,14,22,34,37,40,42,44,51,52],\"raw\":[\"TEMPMIN\",\"is\",\"the\",\"minimum\",\"temperature\",\"if\",\"it\",\"'s\",\"a\",\"Friday\",\".\"],\"tags\":[\"NNP\",\"VBZ\",\"DT\",\"NN\",\"NN\",\"IN\",\"PRP\",\"VBZ\",\"DT\",\"NNP\",\".\"],\"lemmas\":[\"TEMPMIN\",\"be\",\"the\",\"minimum\",\"temperature\",\"if\",\"it\",\"be\",\"a\",\"Friday\",\".\"],\"entities\":[\"O\",\"O\",\"O\",\"O\",\"O\",\"O\",\"O\",\"O\",\"O\",\"DATE\",\"O\"],\"norms\":[\"O\",\"O\",\"O\",\"O\",\"O\",\"O\",\"O\",\"O\",\"O\",\"XXXX-WXX-5\",\"O\"],\"chunks\":[\"B-NP\",\"B-VP\",\"B-NP\",\"I-NP\",\"I-NP\",\"B-SBAR\",\"B-NP\",\"B-VP\",\"O\",\"O\",\"O\"],\"graphs\":{\"universal-enhanced\":{\"edges\":[{\"source\":4,\"destination\":0,\"relation\":\"nsubj\"},{\"source\":4,\"destination\":1,\"relation\":\"cop\"},{\"source\":4,\"destination\":2,\"relation\":\"det\"},{\"source\":4,\"destination\":3,\"relation\":\"compound\"},{\"source\":4,\"destination\":9,\"relation\":\"advcl_if\"},{\"source\":4,\"destination\":10,\"relation\":\"punct\"},{\"source\":9,\"destination\":5,\"relation\":\"mark\"},{\"source\":9,\"destination\":6,\"relation\":\"nsubj\"},{\"source\":9,\"destination\":7,\"relation\":\"cop\"},{\"source\":9,\"destination\":8,\"relation\":\"det\"}],\"roots\":[4]},\"universal-basic\":{\"edges\":[{\"source\":4,\"destination\":0,\"relation\":\"nsubj\"},{\"source\":4,\"destination\":1,\"relation\":\"cop\"},{\"source\":4,\"destination\":2,\"relation\":\"det\"},{\"source\":4,\"destination\":3,\"relation\":\"compound\"},{\"source\":4,\"destination\":9,\"relation\":\"advcl\"},{\"source\":4,\"destination\":10,\"relation\":\"punct\"},{\"source\":9,\"destination\":5,\"relation\":\"mark\"},{\"source\":9,\"destination\":6,\"relation\":\"nsubj\"},{\"source\":9,\"destination\":7,\"relation\":\"cop\"},{\"source\":9,\"destination\":8,\"relation\":\"det\"}],\"roots\":[4]}}}]}")
//    val identifier = new TextBoundMention("Identifier", Interval(0,1), 0, doc1, true, "<MANUAL>")
//    val description = new TextBoundMention("Description", Interval(3,5), 0, doc1, true, "<MANUAL>")
//    val condition = new TextBoundMention("Condition", Interval(5,10), 0, doc1, true, "<MANUAL>")
//
//    val rm = new RelationMention("Description", Map("variable" -> Seq(identifier), "description" -> Seq(description), "conditional" -> Seq(condition)),
//      0, doc1, true, "<MANUAL>")
//
//    Aligner.getRelevantText(rm, aligner.relevantArgs) should be ("TEMPMIN minimum temperature")
//  }


}
