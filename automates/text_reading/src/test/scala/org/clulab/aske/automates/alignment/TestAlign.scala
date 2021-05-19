package org.clulab.aske.automates.alignment

import java.io.File

import com.typesafe.config.ConfigFactory
import org.clulab.aske.automates.TestUtils
import org.clulab.aske.automates.TestUtils.jsonStringToDocument
import org.clulab.aske.automates.apps.ExtractAndAlign
import org.clulab.embeddings.word2vec.Word2Vec
import org.clulab.grounding.sparqlResult
import org.clulab.odin.{Mention, RelationMention, TextBoundMention}
import org.clulab.struct.Interval
import org.clulab.utils.Sourcer
import org.scalatest.{FlatSpec, Matchers}
import ujson.Value
import ai.lum.common.FileUtils._
import scala.collection.mutable.ArrayBuffer

class TestAlign extends FlatSpec with Matchers {


//  def getListOfFiles(dir: File, extensions: List[String]): List[File] = {
//    dir.listFiles.filter(_.isFile).toList.filter { file =>
//      extensions.exists(file.getName.endsWith(_))
//    }
//  }
  println("HERE")
  val config = ConfigFactory.load("/test.conf")
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


  val jsonFile = new File("/home/alexeeva/Repos/automates/automates/text_reading/src/test/resources/temporaryAlignmentOutputSample.json") //todo: this should be read in from inputDir
  val json = ujson.read(jsonFile.readString())
//  val distinctUids = json.obj("links").arr.map(_.obj.)
//  println("<<<>>>" + json.obj("links").arr.map())
  it should "contain links" in {
    json.obj.keys should contain("links")
  }

  val links = json.obj("links").arr


  println(links.map(_.obj("link_type").str).distinct + "<<")
  val src_comment_links = links.filter(_.obj("link_type").str == "source_to_comment")
//  for (scl <- src_comment_links) println(scl)

  println(src_comment_links.head.obj("element_1").str)

  // try str.split("::").last == "s_t"
  it should "have an s_t src to comment element" in {
    src_comment_links.exists(l => l.obj("element_1").str.contains("s_t") & l.obj("element_2").str.contains("S_t         Current count of individuals that are susceptible to either disease") && l.obj("score").num > 0.8) shouldBe true

    // hard to make negative links since we do make an attempt to get top 3 and there will be false positives there
    // need to check if the best one is the top out of three


  }


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
