package org.clulab.aske.automates.mentions

import org.clulab.aske.automates.quantities.Interval
import org.clulab.odin._
import org.clulab.processors.Document

//class CrossSentenceFunctionMention(
//                                 labels: Seq[String],
//                                 tokenInterval: Interval,
////                                 tokenInterval2: Interval,
//                                 trigger: TextBoundMention,
////                                 trigger2: TextBoundMention,
//                                 arguments: Map[String, Seq[Mention]],
//                                 paths: Map[String, Map[Mention, SynPath]],
//                                 sentence: Int,
//                                 document: Document,
//                                 keep: Boolean,
//                                 foundBy: String,
////                                 foundBy2: String,
//                                 attachments: Set[Attachment] = Set.empty
//                               ) extends EventMention(labels, tokenInterval, trigger, arguments, Map.empty, trigger.sentence, document, keep, foundBy, attachments){
//  def this(
//            labels: Seq[String],
//            trigger: TextBoundMention,
//            arguments: Map[String, Seq[Mention]],
//            paths: Map[String, Map[Mention, SynPath]],
//            sentence: Int,
//            document: Document,
//            keep: Boolean,
//            foundBy: String,
//            attachments: Set[Attachment] = Set.empty
//          ) = this(labels, CrossSentenceFunctionMention.calcTokenInterval(sentence, trigger, arguments, document.sentences(sentence).startOffsets.length),
//    trigger, arguments, Map.empty, trigger.sentence, document, keep, foundBy, attachments)
//
//}

//class CrossSentenceFunctionMention extends EventMention {
//  def tokenInterval: Seq[Interval];
//  def trigger: Seq[TextBoundMention];
//  def foundBy: Seq[String]
//}