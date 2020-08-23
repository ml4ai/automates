package org.clulab.aske.automates.quantities

import com.typesafe.config.Config
import ai.lum.common.ConfigUtils._
import org.slf4j.LoggerFactory
import requests.TimeoutException

object GrobidQuantitiesClient {
  val logger = LoggerFactory.getLogger(this.getClass())

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

  import GrobidQuantitiesClient.logger

  val url = s"http://$domain:$port/service/processQuantityText"
  val timeout: Int = 150000

  def getMeasurements(text: String): Vector[Measurement] = {
    try{
      val response = requests.post(url, data = Map("text" -> text), readTimeout = timeout, connectTimeout=timeout)
      val json = ujson.read(response.text)
      json("measurements").arr.flatMap(mkMeasurement).toVector
    } catch { // todo: we can count these one day... should we log them now?
      case time: TimeoutException => Vector.empty[Measurement]
      case parse: ujson.ParseException =>
        logger.warn(s"ujson.ParseException with: $text")
        Vector.empty[Measurement]
      case incomplete: ujson.IncompleteParseException =>
        logger.warn(s"ujson.IncompleteParseException with: $text")
        Vector.empty[Measurement]
    }
  }

  def mkMeasurement(json: ujson.Js): Option[Measurement] = json("type").str match {
    case "value" => Some(mkValue(json))
    case "interval" => Some(mkValueListFromInterval(json)) //returning intervals as value lists
    case "listc" => Some(mkValueListFromListc(json))
    //case t => throw new RuntimeException(s"unsupported measurement type '$t'")
    case t =>
      logger.warn(s"there was an unsupported Measurement type ==> $t")
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


  def mkValueListFromInterval(json: ujson.Js): ValueList = {
    var values = List[Option[Quantity]]()
    if (json.obj.get("quantityLeast").map(mkQuantity).nonEmpty) {values = values :+ json.obj.get("quantityLeast").map(mkQuantity)}
    if (json.obj.get("quantityMost").map(mkQuantity).nonEmpty) {values = values :+ json.obj.get("quantityMost").map(mkQuantity)}
    val quantified = json.obj.get("quantified").map(mkQuantified) //quantifies has not been in interval examples so far, but I keep it as option bc that's how I defined ValueList class (maxaalexeeva)
    ValueList(values, quantified)
  }

  def mkValueListFromListc(json: ujson.Js): ValueList = {
    val quantityList = json("quantities").arr.toList
    val values = for (quant <- quantityList) yield {Some(mkQuantity(quant))}
    val quantified = json.obj.get("quantified").map(mkQuantified)
    ValueList(values, quantified)
  }

  def mkQuantity(json: ujson.Js): Quantity = {
    val rawValue = json("rawValue").str
    val parsedValue = try {
      json.obj.get("parsedValue").map(value => value.num)
    } catch {
      case e: ujson.Value.InvalidData => None
      case other: Throwable => throw other
    }

    val normalizedValue = json.obj.get("normalizedQuantity").map(_.num)
    val rawUnit = json.obj.get("rawUnit").map(mkUnit)
    val normalizedUnit = json.obj.get("normalizedUnit").map(mkUnit)
    val offset = mkOffset(json)
    Quantity(rawValue, parsedValue, normalizedValue, rawUnit, normalizedUnit, offset)
  }


  def mkUnit(json: ujson.Js): UnitOfMeasurement = {
    val name = json("name").str
    val unitType = json.obj.get("type").map(_.str)
    val system = json.obj.get("system").map(_.str)
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
