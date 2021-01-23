package org.clulab.aske.automates.attachments

import org.clulab.odin.Attachment
import org.json4s.JsonDSL._
import org.json4s._
import play.api.libs.json.{JsValue, Json}

abstract class AutomatesAttachment extends Attachment with Serializable {

    // Support for JSON serialization
  def toJson: JsValue
}

class MentionLocationAttachment(pageNum: Int, blockIdx: Int, sentNum: Int, attType: String) extends AutomatesAttachment {

  override def toJson: JsValue =  Json.obj("pageNum" -> pageNum,
    "blockIdx" -> blockIdx,
    "sentNum" -> sentNum,
    "attType" -> attType)

  // use 'asInstanceOf' + this method to retrieve the information from the attachment
  def toUJson: ujson.Value = ujson.Obj("pageNum" -> pageNum,
    "blockIdx" -> blockIdx,
    "sentNum" -> sentNum,
    "attType" -> attType)
}

//object MentionLocationAttachment
