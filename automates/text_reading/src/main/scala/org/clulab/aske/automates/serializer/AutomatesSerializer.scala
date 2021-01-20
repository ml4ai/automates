package org.clulab.aske.automates.serializer

import org.clulab.aske.automates.attachments.MentionLocationAttachment
import org.clulab.odin.{Attachment, EventMention, Mention, RelationMention, TextBoundMention}
import org.clulab.processors.{Document, Sentence}


///** JSON serialization utilities */
object AutomatesJSONSerializer {


  def serializeMentions(mentions: Seq[Mention]): ujson.Value = {
    println("START serializing")
    println("len men inside serialize mentions: " + mentions.length)
    val json = ujson.Obj()
//    for (m <- mentions) {
//      toUJson(m)
//    }
    json("mentions") = ujson.Arr(mentions.map(m => toUJson(m)))
    val distinctDocs = mentions.map(_.document).distinct
    for (d <- distinctDocs) println("->" + d.text)

    val docsAsUjsonObj = ujson.Obj()
    for (doc <- distinctDocs) {
      docsAsUjsonObj(doc.equivalenceHash.toString) = toUJson(doc)
    }
    json("documents") = docsAsUjsonObj
    json
  }

  def toUJson(mention: Mention): ujson.Value = {
//    println("choosing type of mention: " + mention)

    mention match {
      case tb: TextBoundMention => toUJson(tb)
      case rm: RelationMention => toUJson(rm)
      case em: EventMention => toUJson(em)
      case _ => ???
    }
  }


  def toUJson(tb: TextBoundMention): ujson.Value = {
//    println("toJson-ing text bound mention")
    ujson.Obj(
      "type" -> "TextBoundMention",
        "text" -> tb.text,
        "labels" -> tb.labels,
        "tokenInterval" -> Map("start" -> tb.tokenInterval.start, "end" -> tb.tokenInterval.end),
        "characterStartOffset" -> tb.startOffset,
        "characterEndOffset" -> tb.endOffset,
        "sentence" -> tb.sentence,
        "document" -> tb.document.equivalenceHash.toString,
        "keep" -> tb.keep,
        "foundBy" -> tb.foundBy
    )
  }


  def toUJson(rm: RelationMention): ujson.Value = {
    ujson.Obj(
      "type" -> "RelationMention",
      //      // used for paths map
      //      ("id" -> em.id) ~
      "text" -> rm.text,
      "labels" -> rm.labels,
      "arguments" -> argsToUJson(rm.arguments),
      // paths are encoded as (arg name -> (mentionID -> path))
      //      ("paths" -> pathsAST(em.paths)) ~
      "tokenInterval" -> Map("start" -> rm.tokenInterval.start, "end" -> rm.tokenInterval.end),
      "characterStartOffset" -> rm.startOffset,
      "characterEndOffset" -> rm.endOffset,
      "sentence" -> rm.sentence,
      "document" -> rm.document.equivalenceHash.toString,
      "keep" -> rm.keep,
      "foundBy" -> rm.foundBy,
      "attachments" -> toUJson(rm.attachments)
    )
  }

  def toUJson(attachments: Set[Attachment]): ujson.Value = {
    val attsAsUJson = ujson.Arr(attachments.map(toUJson(_)).toList)
    attsAsUJson
  }

  def toUJson(attachment: Attachment): ujson.Value = {
    attachment match {
      case a: MentionLocationAttachment => a.toUJson
      case _ => ???
    }
  }



  def toUJson(em: EventMention): ujson.Value = {
    println("doing an event mention")
    ujson.Obj(
    "type" -> "EventMention",
//      // used for paths map
//      ("id" -> em.id) ~
      "text" -> em.text,
      "labels" -> em.labels,
      "trigger" -> toUJson(em.trigger),
      "arguments" -> argsToUJson(em.arguments),
      // paths are encoded as (arg name -> (mentionID -> path))
//      ("paths" -> pathsAST(em.paths)) ~
      "tokenInterval" -> Map("start" -> em.tokenInterval.start, "end" -> em.tokenInterval.end),
      "characterStartOffset" -> em.startOffset,
      "characterEndOffset" -> em.endOffset,
      "sentence" -> em.sentence,
      "document" -> em.document.equivalenceHash.toString,
      "keep" -> em.keep,
      "foundBy" -> em.foundBy,
      "attachments" -> toUJson(em.attachments)
    )
  }

  def argsToUJson(arguments: Map[String, Seq[Mention]]): ujson.Value = {
    val argsAsUJson = ujson.Obj()
    for (arg <- arguments) {
      argsAsUJson(arg._1) = ujson.Arr(arg._2.map(toUJson(_)).toList)
    }
    argsAsUJson
  }

  def toUJson(document: Document): ujson.Value = {

    val sentencesAsUJson = ujson.Arr(document.sentences.map(s => toUJson(s)).toList)

    ujson.Obj(
      "id" -> document.id.get,
      "text" -> document.text.get,
      "sentences" -> sentencesAsUJson
    )
  }

  def toUJson(s: Sentence): ujson.Value = {
    ujson.Obj(
      "words" -> s.words.toList,
      "startOffsets" -> s.startOffsets.toList,
        "endOffsets" -> s.endOffsets.toList,
        "raw" -> s.raw.toList,
        "tags" -> s.tags.get.toList,
        "lemmas" -> s.lemmas.get.toList,
        "entities" -> s.entities.get.toList,
        "norms" -> s.norms.get.toList,
        "chunks" -> s.chunks.get.toList
//        "graphs" -> s.graphs.jsonAST)

    )
  }


}