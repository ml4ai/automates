package controllers

import org.clulab.aske.automates.attachments._
import play.api.libs.json._
import org.clulab.odin._


/** utilities to convert odin mentions into json objects
 *  that can be returned in http responses
 */
object JsonUtils {

  def mkJsonFromMentions(mentions: Seq[Mention]): JsValue = {
    Json.obj(
      "mentions" -> mkJson(mentions)
    )
  }

  def mkJson(mentions: Seq[Mention]): Json.JsValueWrapper = {
    Json.arr(mentions.map(mkJson): _*)
  }

  def mkJson(m: Mention): Json.JsValueWrapper = m match {
    case m: TextBoundMention => mkJson(m)
    case m: RelationMention => mkJson(m)
    case m: EventMention => mkJson(m)
    case _ => ???
  }

//  def mkJson(m: TextBoundMention): Json.JsValueWrapper = {
//    Json.obj(
//      "labels" -> m.labels,
//      "words" -> m.words,
//      "attachments" -> mkJson(m.attachments),
//      "foundBy" -> m.foundBy
//    )
//  }

  def mkJson(m: TextBoundMention): Json.JsValueWrapper = {
    Json.obj(
      "foundBy" -> m.foundBy,
      "document" -> m.document.id,
      "keep" -> m.keep,
      "text" -> m.text,
      "labels" -> m.labels,
      "characterEndOffset" -> m.endOffset,
      "type" -> "TextBoundMention",
      "characterStartOffset" -> m.startOffset,
      "tokenInterval" -> m.tokenInterval,
      "sentence" -> m.sentence,
      "attachments" -> mkJson(m.attachments)
    )
  }

//  def mkJson(m: RelationMention): Json.JsValueWrapper = {
//    Json.obj(
//      "labels" -> m.labels,
//      "arguments" -> mkJson(m.arguments),
//      "attachments" -> mkJson(m.attachments),
//      "foundBy" -> m.foundBy
//    )
//  }

  def mkJson(m: RelationMention): Json.JsValueWrapper = {
    Json.obj(
      "foundBy" -> m.foundBy,
      "document" -> m.document.id,
      "keep" -> m.keep,
      "text" -> m.text,
      "labels" -> m.labels,
      "characterEndOffset" -> m.endOffset,
      "type" -> "RelationMention",
      "characterStartOffset" -> m.startOffset,
      "tokenInterval" -> m.tokenInterval,
      "sentence" -> m.sentence,
      "attachments" -> mkJson(m.attachments)
    )
  }

//  def mkJson(m: EventMention): Json.JsValueWrapper = {
//    Json.obj(
//      "labels" -> m.labels,
//      "trigger" -> mkJson(m.trigger),
//      "arguments" -> mkJson(m.arguments),
//      "attachments" -> mkJson(m.attachments),
//      "foundBy" -> m.foundBy
//    )
//  }

  def mkJson(m: EventMention): Json.JsValueWrapper = {

    Json.obj(
      "foundBy" -> m.foundBy,
      "document" -> m.document.id,
      "keep" -> m.keep,
      "text" -> m.text,
      "labels" -> m.labels,
    "characterEndOffset" -> m.endOffset,
    "type" -> "EventMention",
    "characterStartOffset" -> m.startOffset,
    "tokenInterval" -> m.tokenInterval,
    "sentence" -> m.sentence,
      "trigger" -> mkJson(m.trigger),
      "attachments" -> mkJson(m.attachments)
    )
  }

  def mkJson(arguments: Map[String, Seq[Mention]]): Json.JsValueWrapper = {
    Json.obj(arguments.mapValues(mkJson).toSeq: _*)
  }

  def mkJson(attachments: Set[Attachment]): Json.JsValueWrapper = {
    Json.arr(attachments.toSeq.map(_.asInstanceOf[AutomatesAttachment]).map(mkJson): _*)

  }

  def mkJson(attachment: AutomatesAttachment): Json.JsValueWrapper = attachment match {
    case attachment: MentionLocationAttachment  => attachment.toJson
    case _ => ???
  }





}
