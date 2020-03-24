package org.clulab.aske.automates.scienceparse

import java.io.File
import java.nio.file.Path

import com.typesafe.config.Config
import ai.lum.common.ConfigUtils._
import ai.lum.common.FileUtils._

object ScienceParseClient {

  def fromConfig(config: Config): ScienceParseClient = {
    val domain = config[String]("domain")
    val port = config[String]("port")
    new ScienceParseClient(domain, port)
  }
  //------------------------------------------------------
  //     Methods for creating ScienceParseDocuments
  //------------------------------------------------------

  def mkDocument(file: File): ScienceParseDocument = {
    val json = ujson.read(file.readString())
    mkDocument(json)
  }

  def mkDocument(json: ujson.Js): ScienceParseDocument = {
    val id = json("id").str
    val title = json.obj.get("title").map(_.str)
    val year = json.obj.get("year")
    val authors = json("authors").arr.map(mkAuthor).toVector
    val abstractText = json.obj.get("abstractText").map(_.str)
    val sections = {
      if (json.obj.get("sections").nonEmpty) Some(json("sections").arr.map(mkSection).toVector)
      else None
    }
    val references = json("references").arr.map(mkReference).toVector
    ScienceParseDocument(id, title, year, authors, abstractText, sections, references)
  }

  def mkAuthor(json: ujson.Js): Author = {
    val name = json("name").str
    val affiliations = json("affiliations").arr.map(_.str).toVector
    Author(name, affiliations)
  }

  //new line is there to make sure comment-like sections are not concatenated into sentences
  //textEnginePreprocessor substitutes \n with a period or space downstream
  def mkSection(json: ujson.Js): Section = {
    val heading = json.obj.get("heading").map(_.str)
    val text = json("text").str
    val headingAndText = {
      if (heading == None) text
      else if (heading != None & text.isEmpty == true) heading.get
      else heading.get + "\n" + text
    }
    Section(headingAndText)
  }

  def mkReference(json: ujson.Js): Reference = {
    val title = json("title").str
    val authors = json("authors").arr.map(_.str).toVector
    //val venue = json("venue").str
    val venueOption = json.obj.get("venue").map(_.str)
    val yearOption = json.obj.get("year").map(_.num.toInt)
    Reference(title, authors, venueOption, yearOption)
  }



}

class ScienceParseClient(
    val domain: String,
    val port: String
) {

  import ScienceParseClient._

  val url = s"http://$domain:$port/v1"
  val timeout: Int = 150000
  val headers = Map("Content-type" -> "application/pdf")

  /* Parse to ScienceParseDocument */

  def parsePdf(filename: String): ScienceParseDocument = {
    parsePdf(new File(filename))
  }

  def parsePdf(file: File): ScienceParseDocument = {
    val json = ujson.read(parsePdfToJson(file))
    mkDocument(json)
  }

  def parsePdf(path: Path): ScienceParseDocument = {
    val json = ujson.read(parsePdfToJson(path))
    mkDocument(json)
  }

  def parsePdf(bytes: Array[Byte]): ScienceParseDocument = {
    val json = ujson.read(parsePdfToJson(bytes))
    mkDocument(json)
  }

  /* Parse to json String */

  def parsePdfToJson(filename: String): String = {
    parsePdfToJson(new File(filename))
  }

  def parsePdfToJson(file: File): String = {
    val response = requests.post(url, headers = headers, data = file, readTimeout = timeout, connectTimeout = timeout)
    response.text
  }

  def parsePdfToJson(path: Path): String = {
    val response = requests.post(url, headers = headers, data = path, readTimeout = timeout, connectTimeout = timeout)
    response.text
  }

  def parsePdfToJson(bytes: Array[Byte]): String = {
    val response = requests.post(url, headers = headers, data = bytes, readTimeout = timeout, connectTimeout = timeout)
    response.text
  }

}
