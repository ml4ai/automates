package org.clulab.aske.automates.alignment

import com.typesafe.config.ConfigFactory
import org.clulab.aske.automates.TestUtils
import org.clulab.embeddings.word2vec.Word2Vec
import org.clulab.odin.{RelationMention, TextBoundMention}
import org.clulab.odin.impl.{OdinCompileException, TokenPattern}
import org.clulab.processors.Document
import org.clulab.processors.fastnlp.FastNLPProcessor
import org.clulab.utils.{FileUtils, Sourcer}
import org.clulab.aske.automates.TestUtils.jsonStringToDocument
import org.clulab.struct.Interval
import org.scalatest.{FlatSpec, Matchers}

class TestPairwiseW2VAligner extends FlatSpec with Matchers {

  val w2v = new Word2Vec(Sourcer.sourceFromResource("/vectors.txt"), None)
  lazy val proc = TestUtils.newOdinSystem(ConfigFactory.load("/test.conf")).proc

  val srcTexts = Seq(
    "I have a cat",
    "I have a house"
  )

  val dstTexts = Seq(
    "my kitten is friendly",
    "I bought a condo"
  )

  val aligner = new PairwiseW2VAligner(w2v, Set("variable", "definition"))
  val mapping = aligner.alignTexts(srcTexts, dstTexts)
  println(mapping)

  it should "generate exhaustive alignemnts" in {
    mapping.length should be (4)
  }

  it should "compare the texts with w2v properly" in {
    val scores = mapping.map(a => ((a.src, a.dst), a.score)).toMap
    val catKitten = scores((0,0))
    val catcondo = scores((0,1))
    val houseKitten = scores((1,0))
    val houseCondo = scores((1,1))
    catKitten should be > catcondo
    houseCondo should be > houseKitten
  }

  it should "extract relevant portions of mentions" in {
    //    "words" : [ "TEMPMIN", "is", "the", "minimum", "temperature", "if", "it", "'s", "a", "Friday", "." ],
    val doc1 = jsonStringToDocument("{\"sentences\":[{\"words\":[\"TEMPMIN\",\"is\",\"the\",\"minimum\",\"temperature\",\"if\",\"it\",\"'s\",\"a\",\"Friday\",\".\"],\"startOffsets\":[0,8,11,15,23,35,38,40,43,45,51],\"endOffsets\":[7,10,14,22,34,37,40,42,44,51,52],\"raw\":[\"TEMPMIN\",\"is\",\"the\",\"minimum\",\"temperature\",\"if\",\"it\",\"'s\",\"a\",\"Friday\",\".\"],\"tags\":[\"NNP\",\"VBZ\",\"DT\",\"NN\",\"NN\",\"IN\",\"PRP\",\"VBZ\",\"DT\",\"NNP\",\".\"],\"lemmas\":[\"TEMPMIN\",\"be\",\"the\",\"minimum\",\"temperature\",\"if\",\"it\",\"be\",\"a\",\"Friday\",\".\"],\"entities\":[\"O\",\"O\",\"O\",\"O\",\"O\",\"O\",\"O\",\"O\",\"O\",\"DATE\",\"O\"],\"norms\":[\"O\",\"O\",\"O\",\"O\",\"O\",\"O\",\"O\",\"O\",\"O\",\"XXXX-WXX-5\",\"O\"],\"chunks\":[\"B-NP\",\"B-VP\",\"B-NP\",\"I-NP\",\"I-NP\",\"B-SBAR\",\"B-NP\",\"B-VP\",\"O\",\"O\",\"O\"],\"graphs\":{\"universal-enhanced\":{\"edges\":[{\"source\":4,\"destination\":0,\"relation\":\"nsubj\"},{\"source\":4,\"destination\":1,\"relation\":\"cop\"},{\"source\":4,\"destination\":2,\"relation\":\"det\"},{\"source\":4,\"destination\":3,\"relation\":\"compound\"},{\"source\":4,\"destination\":9,\"relation\":\"advcl_if\"},{\"source\":4,\"destination\":10,\"relation\":\"punct\"},{\"source\":9,\"destination\":5,\"relation\":\"mark\"},{\"source\":9,\"destination\":6,\"relation\":\"nsubj\"},{\"source\":9,\"destination\":7,\"relation\":\"cop\"},{\"source\":9,\"destination\":8,\"relation\":\"det\"}],\"roots\":[4]},\"universal-basic\":{\"edges\":[{\"source\":4,\"destination\":0,\"relation\":\"nsubj\"},{\"source\":4,\"destination\":1,\"relation\":\"cop\"},{\"source\":4,\"destination\":2,\"relation\":\"det\"},{\"source\":4,\"destination\":3,\"relation\":\"compound\"},{\"source\":4,\"destination\":9,\"relation\":\"advcl\"},{\"source\":4,\"destination\":10,\"relation\":\"punct\"},{\"source\":9,\"destination\":5,\"relation\":\"mark\"},{\"source\":9,\"destination\":6,\"relation\":\"nsubj\"},{\"source\":9,\"destination\":7,\"relation\":\"cop\"},{\"source\":9,\"destination\":8,\"relation\":\"det\"}],\"roots\":[4]}}}]}")
    val variable = new TextBoundMention("Variable", Interval(0,1), 0, doc1, true, "<MANUAL>")
    val definition = new TextBoundMention("Definition", Interval(3,5), 0, doc1, true, "<MANUAL>")
    val condition = new TextBoundMention("Condition", Interval(5,10), 0, doc1, true, "<MANUAL>")

    val rm = new RelationMention("Definition", Map("variable" -> Seq(variable), "definition" -> Seq(definition), "conditional" -> Seq(condition)),
      0, doc1, true, "<MANUAL>")

    Aligner.getRelevantText(rm, aligner.relevantArgs) should be ("TEMPMIN minimum temperature")
  }


}
