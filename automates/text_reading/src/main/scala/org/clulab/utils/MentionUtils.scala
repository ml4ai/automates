package org.clulab.utils

import org.clulab.aske.automates.OdinEngine

import java.io.{File, IOException}
import org.clulab.aske.automates.attachments.{AutomatesAttachment, MentionLocationAttachment}
import org.clulab.odin.{EventMention, Mention}
import org.clulab.aske.automates.apps._
import org.clulab.aske.automates.mentions.CrossSentenceEventMention
import org.clulab.processors.fastnlp.FastNLPProcessor
import org.slf4j.{Logger, LoggerFactory}

import scala.collection.mutable.ArrayBuffer


object MentionUtils {
  /**stores methods related to text mention extraction*/
  protected lazy val logger: Logger = LoggerFactory.getLogger(this.getClass)
  lazy val proc = new FastNLPProcessor()

  def getMentionText(mention: Mention): String = {

    // get text bound mention text taking into account the presence of discontinuous character offset attachment
    if (mention.attachments.nonEmpty & mention.attachments.exists(att => att.asInstanceOf[AutomatesAttachment].toUJson("attType").str == "DiscontinuousCharOffset")) {
      val attAsJson = ExtractAndAlign.returnAttachmentOfAGivenType(mention.attachments, "DiscontinuousCharOffset").toUJson
      val charOffsets = attAsJson("charOffsets").arr.map(v => (v.arr.head.num.toInt, v.arr.last.num.toInt))
      val textPieces = new ArrayBuffer[String]()
      val fullDocText =  try {
        mention.document.text.get
      } catch {
        case e: IOException => throw new RuntimeException("Document text missing; try extracting mentions with keepText set to true")
      }

      for (offset <- charOffsets) {
        textPieces.append(fullDocText.slice(offset._1, offset._2).mkString(""))
      }

      textPieces.mkString(" ")
    } else {
      mention.text
    }
  }


  def getMentionsWithoutLocations(texts: Seq[String], file: File, reader: OdinEngine): Seq[Mention] = {
    // this is for science parse
    val mentions = texts.flatMap(t => reader.extractFromText(t, filename = Some(file.getName)))
    // most fields here will be null, but there will be a filename field; doing this so that all mentions, regardless of whether they have dtailed location (in the document) can be processed the same way
    val mentionsWithLocations = new ArrayBuffer[Mention]()
    for (m <- mentions) {
      val newAttachment = new MentionLocationAttachment(file.getName, Seq(-1), Seq(-1), "MentionLocation")
      val newMen = m match {
        case m: CrossSentenceEventMention => m.asInstanceOf[CrossSentenceEventMention].newWithAttachment(newAttachment)
        case _ => m.withAttachment(newAttachment)
      }
      mentionsWithLocations.append(newMen)
    }
    mentionsWithLocations
  }

  def getMentionsWithLocations(texts: Seq[String], file: File, reader: OdinEngine): Seq[Mention] = {
    // this is for cosmos jsons
    val textsAndFilenames = texts.map(_.split("<::>").slice(0,2).mkString("<::>"))
    val locations = texts.map(_.split("<::>").takeRight(2).mkString("<::>")) //location = pageNum::blockIdx
    val mentions = for (tf <- textsAndFilenames) yield {
      val Array(text, filename) = tf.split("<::>")
      reader.extractFromText(text, keepText = true, Some(filename))
    }
    // store location information from cosmos as an attachment for each mention
    val menWInd = mentions.zipWithIndex
    val mentionsWithLocations = new ArrayBuffer[Mention]()
    for (tuple <- menWInd) {
      // get page and block index for each block; cosmos location information will be the same for all the mentions within one block
      val menInTextBlocks = tuple._1
      val id = tuple._2
      val location = locations(id).split("<::>").map(loc => loc.split(",").map(_.toInt)) //(_.toDouble.toInt)
      val pageNum = location.head
      val blockIdx = location.last

      for (m <- menInTextBlocks) {
        val newAttachment = new MentionLocationAttachment(file.getName, pageNum, blockIdx, "MentionLocation")
        val newMen = m match {
          case m: CrossSentenceEventMention => m.asInstanceOf[CrossSentenceEventMention].newWithAttachment(newAttachment)
          case _ => m.withAttachment(newAttachment)
        }
        mentionsWithLocations.append(newMen)
      }
    }
    mentionsWithLocations
  }

  def distinctByText(mentions: Seq[Mention]): Seq[Mention] = {
    val toReturn = new ArrayBuffer[Mention]()

    val groupedByLabel = mentions.groupBy(_.label)
    for (gr <- groupedByLabel) {
      val groupedByText = gr._2.groupBy(_.text)
      for (g <- groupedByText) {
        val distinctInGroup = g._2.head
        toReturn.append(distinctInGroup)
      }
    }
    toReturn
  }

  def getTriggerText(m: Mention): String = {
    m match {
      case csem: CrossSentenceEventMention => csem.trigger.text
      case em: EventMention => em.trigger.text
      case _ => null
    }
  }
}


