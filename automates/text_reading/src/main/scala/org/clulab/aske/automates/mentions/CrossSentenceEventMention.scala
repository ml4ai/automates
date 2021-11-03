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
}

object CrossSentenceEventMention



