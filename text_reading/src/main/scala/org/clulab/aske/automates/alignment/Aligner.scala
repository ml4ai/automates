package org.clulab.aske.automates.alignment

import org.clulab.odin.Mention

// todo: decide what to produce
case class Alignment()

trait Aligner {
  def alignMentions(srcMentions: Seq[Mention], dstMentions: Seq[Mention]): Alignment
  def alignTexts(srcTexts: Seq[String], dstTexts: Seq[String]): Alignment
}

class PairwiseExhaustiveAligner() extends Aligner {
  def alignMentions(srcMentions: Seq[Mention], dstMentions: Seq[Mention]): Alignment = ???
  def alignTexts(srcTexts: Seq[String], dstTexts: Seq[String]): Alignment = ???
}