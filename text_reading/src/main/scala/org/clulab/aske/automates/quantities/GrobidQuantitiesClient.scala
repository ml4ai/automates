package org.clulab.aske.automates.quantities

import com.typesafe.config.Config
import ai.lum.common.ConfigUtils._

object GrobidQuantitiesClient {
  def fromConfig(config: Config): GrobidQuantitiesClient = {
    val domain = config[String]("domain")
    val port = config[String]("port")
    new GrobidQuantitiesClient(domain, port)
  }
}

class GrobidQuantitiesClient(
    val domain: String,
    val port: String
) {

  val url = s"http://$domain:$port/service/processQuantityText"

  def getMeasurements(text: String): Vector[Measurement] = {
    val response = requests.post(url, data = Map("text" -> text))
    val json = ujson.read(response.text)
    json("measurements").arr.flatMap(mkMeasurement).toVector
  }

  def mkMeasurement(json: ujson.Js): Option[Measurement] = json("type").str match {
    case "value" => Some(mkValue(json))
    case "interval" => Some(mkInterval(json))
    //case t => throw new RuntimeException(s"unsupported measurement type '$t'")
    case t =>
      println(s"WARNING: there was an unsupported Measurement type ==> $t")
      None
  }

  def mkValue(json: ujson.Js): Value = {
    val quantity = mkQuantity(json("quantity"))
    val quantified = json.obj.get("quantified").map(mkQuantified)
    Value(quantity, quantified)
  }

  def mkInterval(json: ujson.Js): Interval = {
    val quantityLeast = json.obj.get("quantityLeast").map(mkQuantity)
    val quantityMost = json.obj.get("quantityMost").map(mkQuantity)
    Interval(quantityLeast, quantityMost)
  }

  def mkQuantity(json: ujson.Js): Quantity = {
    val rawValue = json("rawValue").str
    val parsedValue = json("parsedValue")("numeric").num
    val normalizedValue = json.obj.get("normalizedQuantity").map(_.num)
    val rawUnit = json.obj.get("rawUnit").map(mkUnit)
    val normalizedUnit = json.obj.get("normalizedUnit").map(mkUnit)
    val offset = mkOffset(json)
    Quantity(rawValue, parsedValue, normalizedValue, rawUnit, normalizedUnit, offset)
  }

  def mkUnit(json: ujson.Js): UnitOfMeasurement = {
    val name = json("name").str
    val unitType = json("type").str
    val system = json("system").str
    val offset = if (json.obj.keySet contains "offsetStart") Some(mkOffset(json)) else None
    UnitOfMeasurement(name, unitType, system, offset)
  }

  def mkOffset(json: ujson.Js): Offset = {
    val start = json("offsetStart").num.toInt
    val end = json("offsetEnd").num.toInt
    Offset(start, end)
  }

  def mkQuantified(json: ujson.Js): Quantified = {
    val rawName = json("rawName").str
    val normalizedName = json("normalizedName").str
    val offset = mkOffset(json)
    Quantified(rawName, normalizedName, offset)
  }

}
