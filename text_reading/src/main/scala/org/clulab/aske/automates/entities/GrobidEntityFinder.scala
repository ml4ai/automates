package org.clulab.aske.automates.entities

import org.clulab.aske.automates.quantities.{GrobidQuantitiesClient, Interval, Measurement, Value}
import org.clulab.odin.{Mention, RelationMention, TextBoundMention}
import org.clulab.processors.Document
import org.clulab.processors.fastnlp.FastNLPProcessor
import org.clulab.struct.{Interval => TokenInterval}
import org.clulab.utils.DisplayUtils

import scala.collection.mutable.ArrayBuffer // Add alias bc we have another Interval

class GrobidEntityFinder(val grobidClient: GrobidQuantitiesClient) extends EntityFinder {

  def extract(doc: Document): Seq[Mention] = {
    // Run the grobid client over document
    // Run by document for now... todo should we revisit? by sentence??
    assert(doc.text.nonEmpty)  // assume that we are keeping text
    val text = doc.text.get
    val measurements = grobidClient.getMeasurements(text)

    // convert to odin (Textbound)Mentions
    val mentions = measurements.flatMap(measurementToMentions(_, doc))

    // return!
    mentions
  }

  def measurementToMentions(measurement: Measurement, doc: Document): Seq[Mention] = {
    measurement match {
      case v: Value => valueToMentions(v, doc)
      case i: Interval => intervalToMentions(i, doc)
    }
  }


  // todo: Values also have a Quantified, which we are ignoring for now...
  def valueToMentions(value: Value, doc: Document): Seq[Mention] = {
    val mentions = new ArrayBuffer[Mention]()
    // Get the TBM for the quantity
    val quantity = value.quantity
    val rawValue = quantity.rawValue
    val sentence = getSentence(doc, quantity.offset.start, quantity.offset.end)
    val rawValueTokenInterval = getTokenOffsets(doc, sentence, quantity.offset.start, quantity.offset.end)
    val rawValueMention = new TextBoundMention(GrobidEntityFinder.RAW_VALUE_LABEL, rawValueTokenInterval, sentence, doc, keep = true, foundBy = GrobidEntityFinder.GROBID_FOUNDBY)
    mentions.append(rawValueMention)

    // Get the TBM for the unit, if any
    if (quantity.rawUnit.isDefined) {
      val unit = quantity.rawUnit.get
      val rawUnit = unit.name
      val unitTokenInterval = getTokenOffsets(doc, sentence, unit.offset.get.start, unit.offset.get.end) // if there is a raw unit, it will always have an Offset
      // todo: we're assuming the same sentence as the values above, revisit?
      val unitMention = new TextBoundMention(GrobidEntityFinder.UNIT_LABEL, unitTokenInterval, sentence, doc, keep = true, foundBy = GrobidEntityFinder.GROBID_FOUNDBY)
      mentions.append(unitMention)

      // Make the RelationMention
      val arguments = Map(GrobidEntityFinder.VALUE_ARG -> Seq(rawValueMention), GrobidEntityFinder.UNIT_ARG -> Seq(unitMention))
      // todo: using same sentence as above and empty map for paths
      val quantityWithUnitMention = new RelationMention(GrobidEntityFinder.VALUE_AND_UNIT, arguments, Map.empty, sentence, doc, keep = true, foundBy = GrobidEntityFinder.GROBID_FOUNDBY)
      mentions.append(quantityWithUnitMention)
    }

    // return
    mentions
  }

  def intervalToMentions(interval: Interval, doc: Document): Seq[Mention] = {
    Seq.empty //fixme
  }

  def getTokenOffsets(doc: Document, sent: Int, start: Int, end: Int): TokenInterval = {
    var startToken = -1
    var endToken = -1
    for (i <- doc.sentences(sent).words.indices) {
      val wordStart = doc.sentences(sent).startOffsets(i) // start offset of word i
      val wordEnd = doc.sentences(sent).endOffsets(i) // end offset of word i
      if (start >= wordStart && start < wordEnd) startToken = i
      if (end > wordStart && end <= wordEnd) endToken = i + 1 // add 1 because this finds the token that CONTAINS the offset, but we want an exclusive offset
      // stop early if possible
      if (startToken != -1 && endToken != -1) return TokenInterval(startToken, endToken)
    }
    if (startToken == -1) sys.error(s"startToken not found: ${startToken}")
    if (endToken == -1) sys.error(s"endToken not found: ${endToken}")
    TokenInterval(startToken, endToken)
  }

  // start and end are character offsets (inclusive, exclusive) ??
  def getSentence(document: Document, start: Int, end: Int): Int = {
    for (i <- document.sentences.indices) {
      val sentenceStart = document.sentences(i).startOffsets.head
      val sentenceEnd = document.sentences(i).endOffsets.last
      if (start >= sentenceStart && end <= sentenceEnd) {
        return i
      }
    }
    sys.error(s"interval [$start, $end] not contained in document")
  }

}

object GrobidEntityFinder {
  // Odin Mention labels
  val RAW_VALUE_LABEL: String = "Value"
  val UNIT_LABEL: String = "Unit"
  val VALUE_AND_UNIT: String = "ValueAndUnit"
  // Argument names
  val VALUE_ARG: String = "value"
  val UNIT_ARG: String = "unit"
  // Other
  val GROBID_FOUNDBY: String = "GrobidEntityFinder"

}


object TestStuff {
  def main(args: Array[String]): Unit = {
    val client = new GrobidQuantitiesClient("localhost", "8060")
    val ef = new GrobidEntityFinder(client)
    val proc = new FastNLPProcessor()
    val text = "The height of the chair was 100 cm and it was 2700.5 mm in length."
    val doc = proc.annotate(text, keepText = true)
    val mentions = ef.extract(doc)
    mentions.foreach(m => DisplayUtils.displayMention(m))
  }
}