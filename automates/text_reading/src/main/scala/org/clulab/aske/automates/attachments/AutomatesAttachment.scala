package org.clulab.aske.automates.attachments

import org.clulab.odin.Attachment
import play.api.libs.json.{JsValue, Json}

abstract class AutomatesAttachment extends Attachment with Serializable {

    // Support for JSON serialization
  def toJson: JsValue

  def toUJson: ujson.Value

}

class MentionLocationAttachment(pageNum: Int, blockIdx: Int, attType: String) extends AutomatesAttachment {

  override def toJson: JsValue =  Json.obj(
    "pageNum" -> pageNum,
    "blockIdx" -> blockIdx,
    "attType" -> attType)

  // use 'asInstanceOf' + this method to retrieve the information from the attachment

  def toUJson: ujson.Value = ujson.Obj(
    "pageNum" -> pageNum,
    "blockIdx" -> blockIdx,
    "attType" -> attType) //"MentionLocation"
}

class DiscontinuousCharOffsetAttachment(charOffsets: Seq[(Int, Int)], discontArg: String, attType: String) extends AutomatesAttachment {

  override def toJson: JsValue = ???

  def toUJson: ujson.Value = ujson.Obj(
    "charOffsets" -> offsetsToUJson(charOffsets),
    "discontinuousArgument" -> discontArg, //which argument the discontinuous char offset describes
    "attType" -> attType) //"DiscontinuousCharOffset"

  def offsetsToUJson(charOffsets: Seq[(Int, Int)]): ujson.Value = {
    val json = charOffsets.map(seq => ujson.Arr(seq._1, seq._2))
    json
  }

}

//class ParamSettingAttachment(charOffsets: Seq[(Int, Int)], discontArg: String, attType: String) extends AutomatesAttachment {
//  // this one will just need whether or not we attach through def or var - but again, maybe we dont need that if i just rename args? but then need to change tests and such?.. might be better with just an attachment
//  // this also applies to units - need an att to store what the unit is linked to
//  // AND all of these need to have a location? (optional because we dont always have cosmos input)
//  ???
//}

class ParamSettingIntAttachment(inclusiveLower: Option[Boolean], inclusiveUpper: Option[Boolean], attachedTo: String, attType: String) extends AutomatesAttachment {

  // incl/excl for lower bound- bool
  // incl/excl for upper bound- bool
  // through def or through var - not sure how to store that ; maybe arg should be def instead of var in some cases? probably - some are concepts and some are vars - although if it will be based on arg name, no need to store that info..

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