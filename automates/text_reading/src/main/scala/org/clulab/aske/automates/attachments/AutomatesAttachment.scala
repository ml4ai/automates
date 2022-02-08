package org.clulab.aske.automates.attachments

import org.clulab.aske.automates.quantities.Interval
import org.clulab.odin.Attachment
import play.api.libs.json.{JsValue, Json}

abstract class AutomatesAttachment extends Attachment with Serializable {

    // Support for JSON serialization
  def toJson: JsValue

  def toUJson: ujson.Value

}

class MentionLocationAttachment(filename: String, pageNum: Seq[Int], blockIdx: Seq[Int], attType: String) extends AutomatesAttachment {

  override def toJson: JsValue =  Json.obj(
    "filename" -> filename,
    "pageNum" -> pageNum,
    "blockIdx" -> blockIdx,
    "attType" -> attType)

  // use 'asInstanceOf' + this method to retrieve the information from the attachment

  def toUJson: ujson.Value = ujson.Obj(
    "filename" -> filename,
    "pageNum" -> pageNum,
    "blockIdx" -> blockIdx,
    "attType" -> attType) //"MentionLocation"
}

class DiscontinuousCharOffsetAttachment(charOffsets: Seq[(Int, Int)], attType: String) extends AutomatesAttachment {

  override def toJson: JsValue = ???

  def toUJson: ujson.Value = ujson.Obj(
    "charOffsets" -> offsetsToUJson(charOffsets),
    "attType" -> attType) //"DiscontinuousCharOffset"

  def offsetsToUJson(charOffsets: Seq[(Int, Int)]): ujson.Value = {
    val json = charOffsets.map(seq => ujson.Arr(seq._1, seq._2))
    json
  }

}


class ParamSetAttachment(attachedTo: String, attType: String) extends AutomatesAttachment {

  override def toJson: JsValue = ???

  def toUJson: ujson.Value = {
    val toReturn = ujson.Obj()

    toReturn("attachedTo") = attachedTo
    toReturn("attType") = attType //"ParamSetAtt"
    toReturn
  }

}

class ParamSettingIntAttachment(inclusiveLower: Option[Boolean], inclusiveUpper: Option[Boolean], attachedTo: String, attType: String) extends AutomatesAttachment {

  override def toJson: JsValue = ???

  def toUJson: ujson.Value = {
    val toReturn = ujson.Obj()

    if (inclusiveLower.isDefined) {
      toReturn("inclusiveLower") = inclusiveLower.get
    } else {
      toReturn("inclusiveLower") = ujson.Null
    }

    if (inclusiveUpper.isDefined) {
      toReturn("inclusiveUpper") = inclusiveUpper.get
    } else {
      toReturn("inclusiveUpper") = ujson.Null
    }

    toReturn("attachedTo") = attachedTo
    toReturn("attType") = attType //"ParamSettingIntervalAtt"
    toReturn
  }

}

class UnitAttachment(attachedTo: String, attType: String) extends AutomatesAttachment {

  override def toJson: JsValue = ???

  def toUJson: ujson.Value = {
    val toReturn = ujson.Obj()

    toReturn("attachedTo") = attachedTo
    toReturn("attType") = attType //"UnitAtt"
    toReturn
  }

}

class ContextAttachment(attType: String, context: ujson.Value, foundBy: String) extends AutomatesAttachment {

  override def toJson: JsValue = ???

  def toUJson: ujson.Value = ujson.Obj (
      "contexts" -> contextsToJsonObj(context),
      "attType" -> attType,
      "foundBy" -> foundBy
    )

  def contextsToJsonObj(contexts: ujson.Value): ujson.Value = {
//    val contextsToJsonObj = contexts.map(seq => ujson.Arr(seq))
    val contextsToJsonObj = ujson.Value(contexts)
    contextsToJsonObj
  }
}

class FunctionAttachment(attType: String, trigger: String, foundBy: String) extends AutomatesAttachment {

  override def toJson: JsValue = ???

  def toUJson: ujson.Value = {
    val toReturn = ujson.Obj()
    toReturn("attType") = attType //"FunctionAtt"
    toReturn("trigger") = trigger
    toReturn("foundBy") = foundBy
    toReturn
  }

}