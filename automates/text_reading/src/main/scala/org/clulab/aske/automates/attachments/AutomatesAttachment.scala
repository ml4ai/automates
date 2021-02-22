package org.clulab.aske.automates.attachments

import org.clulab.odin.Attachment
import play.api.libs.json.{JsValue, Json}

abstract class AutomatesAttachment extends Attachment with Serializable {

    // Support for JSON serialization
  def toJson: JsValue
}

class MentionLocationAttachment(pageNum: Int, blockIdx: Int, attType: String) extends AutomatesAttachment {

  override def toJson: JsValue =  Json.obj("pageNum" -> pageNum,
    "blockIdx" -> blockIdx,
    "attType" -> attType)

  // use 'asInstanceOf' + this method to retrieve the information from the attachment
  def toUJson: ujson.Value = ujson.Obj("pageNum" -> pageNum,
    "blockIdx" -> blockIdx,
    "attType" -> attType)
}

