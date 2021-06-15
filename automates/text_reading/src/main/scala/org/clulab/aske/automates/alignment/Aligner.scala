package org.clulab.aske.automates.alignment


import com.typesafe.config.Config
import ai.lum.common.ConfigUtils._
import org.clulab.embeddings.word2vec.Word2Vec
import org.clulab.odin.{EventMention, Mention, RelationMention, TextBoundMention}
import org.apache.commons.text.similarity.LevenshteinDistance
import org.clulab.aske.automates.apps.AlignmentBaseline
import org.clulab.utils.AlignmentJsonUtils.GlobalVariable

case class AlignmentHandler(editDistance: VariableEditDistanceAligner, w2v: PairwiseW2VAligner) {
  def this(w2vPath: String, relevantArgs: Set[String]) =
    this(new VariableEditDistanceAligner(), new PairwiseW2VAligner(new Word2Vec(w2vPath), relevantArgs))
  def this(config: Config) = this(config[String]("w2vPath"), config[List[String]]("relevantArgs").toSet)
}

// todo: decide what to produce for reals
case class Alignment(src: Int, dst: Int, score: Double)

trait Aligner {
  def alignMentions(srcMentions: Seq[Mention], dstMentions: Seq[Mention]): Seq[Alignment]
  def alignTexts(srcTexts: Seq[String], dstTexts: Seq[String]): Seq[Alignment]
}


class VariableEditDistanceAligner(relevantArgs: Set[String] = Set("variable")) {
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

  def intersectMultipler(rendered: String, txtStr: String): Double = {
    // todo: should probably have a version of this for every 'via identifier' link
    // this is used for eq to gvar alignment from the same paper
    // equations come from the same source (scientific publication) as text identifiers, so the non-latex versions of them
    // should match exactly
    // we will hope the renderer did a good job and assign high weight for those that start with the same letter
    if (rendered.head == txtStr.head) return 3.0
    // if not, we will look at how much overlap there is between vars
    val intersect = rendered.toSeq.intersect(txtStr.toSeq)
    // if there's no overlap at all, the score for this alignment is probably 0, so just set multiplier to 0
    if (intersect.length <= 1) return 0

    // if intersect contains capital, return len intersect (even with intersect == 1, capital intersect should be informative
    if (intersect.exists(_.isUpper)) return intersect.length// println("true 75") else println("false 75") //return intersect.length// this is inadequate---has to normalized
    //println("passed 1")


    // shelving these for now till see more examples; fine for a first pass
    // if intersect == 1, return 1 -> not enough info to make us more confident of the edit distance score
    // if intersect > 1 and in same order in both, return len intersect
//    val onlyIntersectStr1 = rendered.filter(intersect.contains(_))
//    val onlyIntersectStr2 = txtStr.filter(intersect.contains(_))
//    var sameOrder = true
//    if (onlyIntersectStr1.length != onlyIntersectStr2.length) return 1.0 // what?!
//    else {
//      for ((char, index) <- onlyIntersectStr1.zipWithIndex) {
//        if (char != onlyIntersectStr2(index)) {
//          sameOrder = false
//        }
//      }
//    }
//    if (sameOrder) return 2.0

    1.0
  }

  // todo: maybe for equations it should not be judged on distance but just on overlap in some way? like b and E are in no way similar...
  // and intersect could be normalized in some way? like by length or something?..
  def alignEqAndTexts(srcTexts: Seq[String], dstTexts: Seq[String]): Seq[Alignment] = {
    val exhaustiveScores = for {
      (src, i) <- srcTexts.zipWithIndex
      rendered = AlignmentBaseline.renderForAlign(src)
      (dst, j) <- dstTexts.zipWithIndex
      multiplier = intersectMultipler(rendered, dst) // how did I make so many eq to gvar elements to go away? is there a threshold?
      score = 1.0 * multiplier / (editDistance(rendered, dst) + 1.0) // todo: is this good for long-term? next thing to try: only align if rendered starts with the same letter as actual---might need to make this output an option in case if there are no alignments; todo: try to find a way to use intersect multiplier
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
  * @param relevantArgs a Set of the string argument names that you want to include in the similarity (e.g., "variable" or "description")
  */
class PairwiseW2VAligner(val w2v: Word2Vec, val relevantArgs: Set[String]) extends Aligner {
  def this(w2vPath: String, relevantArgs: Set[String]) = this(new Word2Vec(w2vPath), relevantArgs)

  def alignMentions(srcMentions: Seq[Mention], dstMentions: Seq[Mention]): Seq[Alignment] = {
    alignTexts(srcMentions.map(Aligner.getRelevantText(_, relevantArgs).toLowerCase()), dstMentions.map(Aligner.getRelevantText(_, relevantArgs).toLowerCase()))
  }

  def getRelevantTextFromGlobalVar(glv: GlobalVariable): String = {
    // ["variable", "description"]
    val relText = relevantArgs match {
      case x if x.contains("variable") & x.contains("description")=> glv.identifier + " " + glv.textFromAllDescrs.mkString(" ")
      case x if x.contains("variable") => glv.identifier
      case x if x.contains("description") => glv.textFromAllDescrs.mkString(" ")
      case _ => ???
    }
//    println("relevant text: " + relText)
    relText
  }

  def alignMentionsAndGlobalVars(srcMentions: Seq[Mention], glVars: Seq[GlobalVariable]): Seq[Alignment] = {
    alignTexts(srcMentions.map(Aligner.getRelevantText(_, relevantArgs).toLowerCase()), glVars.map(getRelevantTextFromGlobalVar(_).toLowerCase()))
  }

  def alignGlobalCommentVarAndGlobalVars(commentGlVar: Seq[GlobalVariable], glVars: Seq[GlobalVariable]): Seq[Alignment] = {
    // todo: since we base this on text of multiple descriptions, we can try to add some sort of weight for words that occur multiple times
    // todo: text of conj descrs should be returned based on char offset attachement
//    for (g <- commentGlVar) println("_> " + g)
    alignTexts(commentGlVar.map(getRelevantTextFromGlobalVar(_).toLowerCase()), glVars.map(getRelevantTextFromGlobalVar(_).toLowerCase()))
  }

  def alignTexts(srcTexts: Seq[String], dstTexts: Seq[String]): Seq[Alignment] = {
    val exhaustiveScores = for {
      (src, i) <- srcTexts.zipWithIndex
      (dst, j) <- dstTexts.zipWithIndex
      score = compare(src, dst) + 2 * (1.0 / (editDistance(src, dst) + 1.0))
//      score =  (1.0 / (editDistance(src, dst) + 1.0)) // score without using word embeddings
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

  def topKByDst(alignments: Seq[Alignment], k: Int, scoreThreshold: Double = 0.0, debug: Boolean = false): Seq[Seq[Alignment]] = {
    def debugPrint(debug: Boolean, srcIdx: Int, alignments: Seq[Alignment]) {
      if (debug) println(s"srcIdx: ${srcIdx}, alignments: ${alignments}")
    }

//    val overallSum = alignments.map(_.score).sum
    val grouped = alignments.groupBy(_.dst).toSeq

    // score sum doesn't work bc alignment for eq to text bc here we group by source and src is eq and then when we choose top n for dst,
    // if we normalize by sum, we end up on a different scale
    //    for ((srcIdx, aa) <- grouped) {
    //      val scoreSum = aa.map(_.score).sum
    //      println("score sum: " + scoreSum)
    //    }
    for {
      (srcIdx, aa) <- grouped
      _ = debugPrint(debug, srcIdx, alignments)
      // since we added a bunch of multipliers, it might be good to normalize the scores, so we divide them by the sum of all the scores - doesn't work
      // bc scale ends up being different when we choose highest score for dst var
      scoreMax = aa.map(_.score).max
      topK = aa.sortBy(-_.score/scoreMax).slice(0,k).filter(_.score > scoreThreshold).map(a => Alignment(a.src, a.dst, a.score/scoreMax)) //filter out those with the score below the threshold; threshold is 0 by default
      if topK.nonEmpty
    } yield topK
  }

  def topKBySrc(alignments: Seq[Alignment], k: Int, scoreThreshold: Double = 0.0, debug: Boolean = false): Seq[Seq[Alignment]] = {
    def debugPrint(debug: Boolean, srcIdx: Int, alignments: Seq[Alignment]) {
      if (debug) println(s"srcIdx: ${srcIdx}, alignments: ${alignments}")
    }

//    val overallSum = alignments.map(_.score).sum
    val grouped = alignments.groupBy(_.src).toSeq

    // score sum doesn't work bc alignment for eq to text bc here we group by source and src is eq and then when we choose top n for dst,
    // if we normalize by sum, we end up on a different scale
//    for ((srcIdx, aa) <- grouped) {
//      val scoreSum = aa.map(_.score).sum
//      println("score sum: " + scoreSum)
//    }
    for {
      (srcIdx, aa) <- grouped
      _ = debugPrint(debug, srcIdx, alignments)
      // since we added a bunch of multipliers, it might be good to normalize the scores, so we divide them by the sum of all the scores - doesn't work
      // bc scale ends up being different when we choose highest score for dst var
      scoreMax = aa.map(_.score).max // if i do weights for some of the links, then when getting top k, divide sort by score by score max and remap alignments to updated scores
      topK = aa.sortBy(-_.score).slice(0,k).filter(_.score > scoreThreshold)//.map(a => Alignment(a.src, a.dst, a.score/scoreMax)) //filter out those with the score below the threshold; threshold is 0 by default
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