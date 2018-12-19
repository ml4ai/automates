package controllers

import play.api.libs.json._
import org.clulab.odin._
import org.clulab.quickstart.PitchInfo

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

  def mkJson(m: TextBoundMention): Json.JsValueWrapper = {
    Json.obj(
      "labels" -> m.labels,
      "words" -> m.words,
      "attachments" -> mkJson(m.attachments),
      "foundBy" -> m.foundBy
    )
  }

  def mkJson(m: RelationMention): Json.JsValueWrapper = {
    Json.obj(
      "labels" -> m.labels,
      "arguments" -> mkJson(m.arguments),
      "attachments" -> mkJson(m.attachments),
      "foundBy" -> m.foundBy
    )
  }

  def mkJson(m: EventMention): Json.JsValueWrapper = {
    Json.obj(
      "labels" -> m.labels,
      "trigger" -> mkJson(m.trigger),
      "arguments" -> mkJson(m.arguments),
      "attachments" -> mkJson(m.attachments),
      "foundBy" -> m.foundBy
    )
  }

  def mkJson(arguments: Map[String, Seq[Mention]]): Json.JsValueWrapper = {
    Json.obj(arguments.mapValues(mkJson).toSeq: _*)
  }

  def mkJson(attachments: Set[Attachment]): Json.JsValueWrapper = {
    Json.arr(attachments.toSeq.map(mkJson): _*)
  }

  def mkJson(attachment: Attachment): Json.JsValueWrapper = attachment match {
    case info: PitchInfo => mkJson(info)
    case _ => ???
  }

  def mkJson(info: PitchInfo): Json.JsValueWrapper = {
    Json.obj(
      "pitch" -> info.pitch,
      "octave" -> info.octave,
      "accidental" -> info.accidental
    )
  }

}
