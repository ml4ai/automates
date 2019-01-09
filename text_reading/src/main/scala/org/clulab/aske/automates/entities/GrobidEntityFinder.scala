package org.clulab.aske.automates.entities

import com.typesafe.config.Config
import org.clulab.aske.automates.quantities._
import org.clulab.odin.{Mention, RelationMention, TextBoundMention, mkTokenInterval}
import org.clulab.processors.Document
import org.clulab.processors.fastnlp.FastNLPProcessor
import org.clulab.struct.{Interval => TokenInterval}
import org.clulab.utils.DisplayUtils
import ai.lum.common.ConfigUtils._
import org.clulab.odin.impl.Taxonomy

import org.clulab.aske.automates.OdinActions

import scala.collection.mutable.ArrayBuffer

class GrobidEntityFinder(val grobidClient: GrobidQuantitiesClient, private var taxonomy: Option[Taxonomy]) extends EntityFinder {

  import GrobidEntityFinder._

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

  def valueToMentions(value: Value, doc: Document): Seq[Mention] = {
    quantityToMentions(value.quantity, doc)
  }

  // todo: Values also have a Quantified, which we are ignoring for now...
  def quantityToMentions(quantity: Quantity, doc: Document): Seq[Mention] = {
    val mentions = new ArrayBuffer[Mention]()
    // Get the TBM for the quantity
    val rawValue = quantity.rawValue
    val sentence = getSentence(doc, quantity.offset.start, quantity.offset.end)
    val rawValueTokenInterval = getTokenOffsets(doc, sentence, quantity.offset.start, quantity.offset.end)
    val rawValueMention = new TextBoundMention(getLabels(RAW_VALUE_LABEL), rawValueTokenInterval, sentence, doc, keep = true, foundBy = GrobidEntityFinder.GROBID_FOUNDBY)
    mentions.append(rawValueMention)

    // Get the TBM for the unit, if any
    if (quantity.rawUnit.isDefined) {
      val unit = quantity.rawUnit.get
      val rawUnit = unit.name
      val unitTokenInterval = getTokenOffsets(doc, sentence, unit.offset.get.start, unit.offset.get.end) // if there is a raw unit, it will always have an Offset
      // todo: we're assuming the same sentence as the values above, revisit?
      val unitMention = new TextBoundMention(getLabels(UNIT_LABEL), unitTokenInterval, sentence, doc, keep = true, foundBy = GrobidEntityFinder.GROBID_FOUNDBY)
      mentions.append(unitMention)

      // Make the RelationMention
      val arguments = Map(GrobidEntityFinder.VALUE_ARG -> Seq(rawValueMention), GrobidEntityFinder.UNIT_ARG -> Seq(unitMention))
      // todo: using same sentence as above and empty map for paths
      val quantityWithUnitMention = new RelationMention(getLabels(VALUE_AND_UNIT), mkTokenInterval(arguments), arguments, Map.empty, sentence, doc, keep = true, foundBy = GrobidEntityFinder.GROBID_FOUNDBY)
      mentions.append(quantityWithUnitMention)
    }

    // return
    mentions
  }

  def getPrimaryMention(mentions: Seq[Mention]): Mention = {
    val (relationMentions, other) = mentions.partition(_.isInstanceOf[RelationMention])
    if (relationMentions.nonEmpty) {
      assert(relationMentions.length == 1) // I think there should only be one!
      relationMentions.head
    } else {
      assert(other.length == 1) // I think that there should only be 1, which is a RawValue
      other.head
    }
  }

  def intervalToMentions(interval: Interval, doc: Document): Seq[Mention] = {
    val mentions = new ArrayBuffer[Mention]()
    var sentence: Int = -1
    val arguments = new scala.collection.mutable.HashMap[String, Seq[Mention]]
    // Get the Mentions from each of the Quantities
    val quantLeast = interval.quantityLeast.map(quantityToMentions(_, doc))
    if (quantLeast.nonEmpty) {
      mentions.appendAll(quantLeast.get)
      val leastMention = getPrimaryMention(quantLeast.get)
      arguments.put(GrobidEntityFinder.LEAST_ARG, Seq(leastMention))
      sentence = leastMention.sentence
    }
    val quantMost = interval.quantityMost.map(quantityToMentions(_, doc))
    if (quantMost.nonEmpty) {
      mentions.appendAll(quantMost.get)
      val mostMention = getPrimaryMention(quantMost.get)
      arguments.put(GrobidEntityFinder.MOST_ARG, Seq(mostMention))
      sentence = mostMention.sentence
    }
    // Make a RelationMention that has however many there are...
    assert(arguments.size > 0 && sentence != -1) // We should have had one or the other at least!
    val args = arguments.toMap
    val intervalMention = new RelationMention(getLabels(GrobidEntityFinder.INTERVAL_LABEL), mkTokenInterval(args), args, Map.empty, sentence, doc, keep = true, foundBy = GrobidEntityFinder.GROBID_FOUNDBY)
    mentions.append(intervalMention)

    mentions
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

  // --------------------------------------
  //            Helper Methods
  // --------------------------------------

  /**
    * Get the labels for the Mention based on the taxonomy.
    * @param label
    * @return
    */
  def getLabels(label: String): Seq[String] = {
    taxonomy match {
      case Some(t) => t.hypernymsFor(label)
      case None => Seq(label)
    }
  }

}

object GrobidEntityFinder {
  // Odin Mention labels
  val RAW_VALUE_LABEL: String = "Value"
  val UNIT_LABEL: String = "Unit"
  val VALUE_AND_UNIT: String = "ValueAndUnit"
  val INTERVAL_LABEL: String = "Interval"
  // Argument names
  val VALUE_ARG: String = "value"
  val UNIT_ARG: String = "unit"
  val LEAST_ARG: String = "least"
  val MOST_ARG: String = "most"
  // Other
  val GROBID_FOUNDBY: String = "GrobidEntityFinder"

  def fromConfig(config: Config): GrobidEntityFinder = {
    val taxonomy = OdinActions.readTaxonomy(config[String]("taxonomy"))
    val domain = config[String]("domain")
    val port = config[String]("port")

    new GrobidEntityFinder(new GrobidQuantitiesClient(domain, port), Some(taxonomy))
  }

}


object TestStuff {
  def main(args: Array[String]): Unit = {
    val client = new GrobidQuantitiesClient("localhost", "8060")
    val ef = new GrobidEntityFinder(client, None)
    val proc = new FastNLPProcessor()
    val text = "The height of the chair was 100-150 cm."
    val doc = proc.annotate(text, keepText = true)
    val mentions = ef.extract(doc)
    mentions.foreach(m => DisplayUtils.displayMention(m))
  }
}