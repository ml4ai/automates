package org.clulab.aske.automates.alignment

import ai.lum.common.ConfigUtils._
import com.typesafe.config.Config
import org.clulab.embeddings.word2vec.Word2Vec
import org.clulab.odin.{EventMention, Mention, RelationMention, TextBoundMention}
import org.apache.commons.text.similarity.LevenshteinDistance

// todo: decide what to produce for reals
case class Alignment(src: Int, dst: Int, score: Double)

trait Aligner {
  def alignMentions(srcMentions: Seq[Mention], dstMentions: Seq[Mention]): Seq[Alignment]
  def alignTexts(srcTexts: Seq[String], dstTexts: Seq[String]): Seq[Alignment]
}


class VariableEditDistanceAligner(relevantArgs: Set[String]) {
  def alignMentions(srcMentions: Seq[Mention], dstMentions: Seq[Mention]): Seq[Alignment] = {
    alignTexts(srcMentions.map(Aligner.getRelevantText(_, relevantArgs)), dstMentions.map(Aligner.getRelevantText(_, relevantArgs)))
  }
  def alignTexts(srcTexts: Seq[String], dstTexts: Seq[String]): Seq[Alignment] = {
    val exhaustiveScores = for {
      (src, i) <- srcTexts.zipWithIndex
      (dst, j) <- dstTexts.zipWithIndex
      score = 1.0 / (editDistance(src, dst) + 1.0) // todo: is this good for long-term?
    } yield Alignment(i, j, score)
    // redundant but good for debugging
    exhaustiveScores
  }

  def editDistance(s1: String, s2: String): Double = {
    LevenshteinDistance.getDefaultInstance().apply(s1, s2).toDouble
  }
}

/**
  * Performs an exhaustive pairwise alignment, comparing each src item with each dst item independently of the others.
  * @param w2v
  * @param relevantArgs a Set of the string argument names that you want to include in the similarity (e.g., "variable" or "definition")
  */
class PairwiseW2VAligner(val w2v: Word2Vec, val relevantArgs: Set[String]) extends Aligner {

  def alignMentions(srcMentions: Seq[Mention], dstMentions: Seq[Mention]): Seq[Alignment] = {
    alignTexts(srcMentions.map(Aligner.getRelevantText(_, relevantArgs)), dstMentions.map(Aligner.getRelevantText(_, relevantArgs)))
  }

  def alignTexts(srcTexts: Seq[String], dstTexts: Seq[String]): Seq[Alignment] = {
    val exhaustiveScores = for {
      (src, i) <- srcTexts.zipWithIndex
      (dst, j) <- dstTexts.zipWithIndex
      score = compare(src, dst) + 2 * (1.0 / (editDistance(src, dst) + 1.0))
    } yield Alignment(i, j, score)
    // redundant but good for debugging
    exhaustiveScores
  }

  def editDistance(s1: String, s2: String): Double = {
    LevenshteinDistance.getDefaultInstance().apply(s1, s2).toDouble
  }

  // fixme - pick something more intentional
  def compare(src: String, dst: String): Double = {
    val srcTokens = src.split(" ")
    val dstTokens = dst.split(" ")
    w2v.avgSimilarity(srcTokens, dstTokens) + w2v.maxSimilarity(srcTokens, dstTokens)
  }


}

object PairwiseW2VAligner {
  def fromConfig(config: Config): Aligner = {
    val w2vPath: String = config[String]("w2vPath")
    val w2v = new Word2Vec(w2vPath)
    val relevantArgs: List[String] = config[List[String]]("relevantArgs")

    new PairwiseW2VAligner(w2v, relevantArgs.toSet)
  }
}

object Aligner {

  def fromConfig(config: Config): Aligner = {
    val alignerType = config[String]("alignerType")
    alignerType match {
      case "pairwisew2v" => PairwiseW2VAligner.fromConfig(config)
      case _ => ???
    }
  }

  def topKBySrc(alignments: Seq[Alignment], k: Int, scoreThreshold: Double = 0.0): Seq[Seq[Alignment]] = {
    val grouped = alignments.groupBy(_.src).toSeq
    for {
      (srcIdx, aa) <- grouped
      topK = aa.sortBy(-_.score).slice(0,k).filter(_.score > scoreThreshold) //filter out those with the score below the threshold; threshold is 0 by default
      if topK.nonEmpty
    } yield topK
  }

  // Helper methods for handling mentions
  def mkTextFromArgs(argMap: Map[String, Seq[Mention]]): String = {
    val stopwords = Set("the", "in", "on", "from") // fixme: this is a hack, should be more robust
    argMap.values.flatten.map(_.text).filter(!stopwords.contains(_)).mkString(" ")
  }
  // Get the text from the arguments of the mention, but only the previously specified arguments
  def getRelevantText(m: Mention, relevantArgs: Set[String]): String = {
    m match {
      case tb: TextBoundMention => m.text
      case rm: RelationMention =>
        val relevantOnly = rm.arguments.filterKeys(arg => relevantArgs.contains(arg))
        mkTextFromArgs(relevantOnly)
      case em: EventMention =>
        val relevantOnly = em.arguments.filterKeys(arg => relevantArgs.contains(arg))
        mkTextFromArgs(relevantOnly)
      case _ => ???
    }
  }
}