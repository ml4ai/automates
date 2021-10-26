package org.clulab.aske.automates.mentions

import org.clulab.odin
import org.clulab.odin.{Mention, _}
import org.clulab.processors.Document
import org.clulab.struct.Interval

//same as EventMention but with a different foundBy, no paths, sentence == the sent of the trigger, and a different text method

//trait CrossSentenceTrait extends Equals with Ordered[Mention] with Serializable {
//  def sentences: Seq[Int]
//}

class CrossSentenceEventMention(
                                 val labels: Seq[String],
                                 val tokenInterval: Interval,
                                 val trigger: TextBoundMention,
                                 val arguments: Map[String, Seq[Mention]],
                                 val paths: Map[String, Map[Mention, SynPath]],
                                 val sentence: Int,
                                 val additionalSentence: Int,
                                 val document: Document,
                                 val keep: Boolean,
                                 val foundBy: String,
                                 val attachments: Set[Attachment]
                               ) extends Mention {

  def this(
            label: String,
            trigger: TextBoundMention,
            arguments: Map[String, Seq[Mention]],
            paths: Map[String, Map[Mention, SynPath]],
            sentence: Int,
            additionalSentence: Int,
            document: Document,
            keep: Boolean,
            foundBy: String
          ) = this(Seq(label), mkTokenInterval(trigger, arguments), trigger, arguments, paths, sentence, additionalSentence, document, keep, foundBy, Set.empty)
}

object CrossSentenceEventMention


//
//  //the text method is overridden bc the EventMention text method does not work with cross sentence mentions
//
//  override def text: String = {
//    val sentenceAndMentionsSeq = (arguments
//      .values
//      .flatten ++ Seq(trigger))
//      .groupBy(_.sentence)
//      .toSeq
//      .sortBy(_._1) // sort by the sentence
//    // Since this is CrossSentence, there are at least two different sentences.
//    val firstSentence = sentenceAndMentionsSeq.head._1
//    val lastSentence = sentenceAndMentionsSeq.last._1
//    val perSentenceWords = sentenceAndMentionsSeq.map { case (sentence, mentions) =>
//      val sentenceWordArr = mentions.head.sentenceObj.raw //sentence as an array of tokens
//      //compile text of the CrossSentenceEventMention from parts of the sentences that the CrossSentenceEventMention spans
//      val words = sentence match { //sentence index (ordered)
//        case sentence if sentence == firstSentence =>
//          // in the first sentence the CrossSentenceEventMention spans, the part to return is the span from the start of the first argument or trigger of the event to the end of the sentence
//          // Although it doesn't matter much with a small collection, sorting one in its entirety just to extract
//          // an extreme value is inefficient.  So, a simple minBy is used.  Is there no minByBy?
//          val start = mentions.minBy(_.start).start
//          sentenceWordArr.drop(start)
//        case sentence if sentence == lastSentence =>
//          // in the last sentence the CrossSentenceEventMention spans, the part to return is the span from the beginning of the sentence to the end of the last argument or the trigger, whichever comes latest
//          // Although it may not be a problem in this context, the maximum end does not necessarily come from the
//          // mention with the maximum start.  Sometimes mentions overlap and they might conceivably be nested.
//          val end = mentions.maxBy(_.end).end
//          sentenceWordArr.take(end)
//        case _ =>
//          // if it's a middle sentence, the part to return is the whole sentence
//          sentenceWordArr
//      }
//
//      words
//    }
//    val text = perSentenceWords.flatten.mkString(" ")
//
//    text
//  }
//}
//
//object CrossSentenceEventMention {
//
//  def calcTokenInterval(sentence: Int, trigger: TextBoundMention, arguments: Map[String, Seq[Mention]], tokenCount: Int): Interval = {
//    // Base the token interval only on arguments from the mention's sentence because the token interval is only
//    // valid for a single sentence.  They cannot extend to other sentences.
//    // TODO: Figure out a way around this limitation.
//    val hasPreceding = trigger.sentence < sentence || arguments.values.exists { mentions => mentions.exists(_.sentence < sentence) }
//    val hasFollowing = sentence < trigger.sentence || arguments.values.exists { mentions => mentions.exists(sentence < _.sentence) }
//    val localArguments = arguments.map { case (key, values) =>
//      key -> values.filter(_.sentence == sentence)
//    }
//    val localTokenInterval = if (trigger.sentence == sentence)
//      odin.mkTokenInterval(trigger, localArguments)
//    else
//      odin.mkTokenInterval(localArguments)
//    val tokenInterval = (hasPreceding, hasFollowing) match {
//      case (false, false) => localTokenInterval
//      case (false, true) => Interval(localTokenInterval.start, tokenCount)
//      case (true, false) => Interval(0, localTokenInterval.end)
//      case (true, true) => Interval(0, tokenCount)
//    }
//
//    tokenInterval
//  }
//}



