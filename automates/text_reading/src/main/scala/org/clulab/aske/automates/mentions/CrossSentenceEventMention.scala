package org.clulab.aske.automates.mentions

import org.clulab.odin
import org.clulab.odin.{Mention, _}
import org.clulab.processors.Document
import org.clulab.struct.Interval

// note: same as EventMention but has args from two different sentences - thus requires two sentence information.

class CrossSentenceEventMention(
                                 val labels: Seq[String],
                                 val tokenInterval: Interval,
                                 val trigger: TextBoundMention,
                                 val arguments: Map[String, Seq[Mention]],
                                 val paths: Map[String, Map[Mention, SynPath]],
                                 val sentence: Int,
                                 val sentences: Seq[Int],
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
            sentences: Seq[Int],
            document: Document,
            keep: Boolean,
            foundBy: String
          ) = this(Seq(label), mkTokenInterval(trigger, arguments), trigger, arguments, paths, sentence, sentences, document, keep, foundBy, Set.empty)

  // note: the method below is for copying a mention with some modification to its components.
  def copy(
            labels: Seq[String] = this.labels,
            tokenInterval: Interval = this.tokenInterval,
            trigger: TextBoundMention = this.trigger,
            arguments: Map[String, Seq[Mention]] = this.arguments,
            paths: Map[String, Map[Mention, SynPath]] = this.paths,
            sentence: Int = this.sentence,
            sentences: Seq[Int] = this.sentences,
            document: Document = this.document,
            keep: Boolean = this.keep,
            foundBy: String = this.foundBy,
            attachments: Set[Attachment] = this.attachments
          ): CrossSentenceEventMention = new CrossSentenceEventMention(labels, tokenInterval, trigger, arguments, paths, sentence, sentences, document, keep, foundBy, attachments)

  def newWithAttachment(mod: Attachment): CrossSentenceEventMention = {
    copy(attachments = this.attachments + mod)
  }

  def newWithoutAttachment(mod: Attachment): CrossSentenceEventMention = {
    copy(attachments = this.attachments - mod)
  }

  override def withAttachment(mod: Attachment): Mention = this match {
    case m: CrossSentenceEventMention => m.newWithAttachment(mod)
  }

  override def withoutAttachment(mod: Attachment): Mention = this match {
    case m: CrossSentenceEventMention => m.newWithoutAttachment(mod)
  }

  override def text: String = {
    val sentenceAndMentionsSeq = (arguments
      .values
      .flatten ++ Seq(trigger))
      .groupBy(_.sentence)
      .toSeq
      .sortBy(_._1) // sort by the sentence
    // Since this is CrossSentence, there are at least two different sentences.
    val firstSentence = sentenceAndMentionsSeq.head._1
    val lastSentence = sentenceAndMentionsSeq.last._1
    val perSentenceWords = sentenceAndMentionsSeq.map { case (sentence, mentions) =>
      val sentenceWordArr = mentions.head.sentenceObj.raw //sentence as an array of tokens
      //compile text of the CrossSentenceEventMention from parts of the sentences that the CrossSentenceEventMention spans
      val words = sentence match { //sentence index (ordered)
        case sentence if sentence == firstSentence =>
          // in the first sentence the CrossSentenceEventMention spans, the part to return is the span from the start of the first argument or trigger of the event to the end of the sentence
          // Although it doesn't matter much with a small collection, sorting one in its entirety just to extract
          // an extreme value is inefficient.  So, a simple minBy is used.  Is there no minByBy?
          val start = mentions.minBy(_.start).start
          sentenceWordArr.drop(start)
        case sentence if sentence == lastSentence =>
          // in the last sentence the CrossSentenceEventMention spans, the part to return is the span from the beginning of the sentence to the end of the last argument or the trigger, whichever comes latest
          // Although it may not be a problem in this context, the maximum end does not necessarily come from the
          // mention with the maximum start.  Sometimes mentions overlap and they might conceivably be nested.
          val end = mentions.maxBy(_.end).end
          sentenceWordArr.take(end)
        case _ =>
          // if it's a middle sentence, the part to return is the whole sentence
          sentenceWordArr
      }

      words
    }
    val text = perSentenceWords.flatten.mkString(" ")

    text
  }
}

object CrossSentenceEventMention

