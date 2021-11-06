package org.clulab.aske.automates.mentions

import org.clulab.odin
import org.clulab.odin.{Mention, _}
import org.clulab.processors.Document
import org.clulab.struct.Interval

// note: same as EventMention but has args from two different sentences - thus requires two sentence information.
// fixme: this is not properly deserialized yet.

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
}

object CrossSentenceEventMention



