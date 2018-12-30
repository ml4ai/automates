package org.clulab.aske.automates.scienceparse

import java.io.File
import java.nio.file.Path

class ScienceParseClient(
    val domain: String,
    val port: String
) {

  val url = s"http://$domain:$port/v1"
  val headers = Map("Content-type" -> "application/pdf")

  def parseDocument(filename: String): Document = {
    parseDocument(new File(filename))
  }

  def parseDocument(path: Path): Document = {
    parseDocument(path.toFile())
  }

  def parseDocument(file: File): Document = {
    val response = requests.post(url, headers = headers, data = file)
    val json = ujson.read(response.text)
    mkDocumentFromJson(json)
  }

  def mkDocumentFromJson(json: ujson.Js): Document = {
    val id = json("id").str
    val title = json("title").str
    val year = json("year").num.toInt
    val authors = json("authors").arr.map(mkAuthor).toVector
    val abstractText = json("abstractText").str
    val sections = json("sections").arr.map(mkSection).toVector
    val references = json("references").arr.map(mkReference).toVector
    Document(id, title, year, authors, abstractText, sections, references)
  }

  def mkAuthor(json: ujson.Js): Author = {
    val name = json("name").str
    val affiliations = json("affiliations").arr.map(_.str).toVector
    Author(name, affiliations)
  }

  def mkSection(json: ujson.Js): Section = {
    val heading = if (json.obj.keySet contains "heading") Some(json("heading").str) else None
    val text = json("text").str
    Section(heading, text)
  }

  def mkReference(json: ujson.Js): Reference = {
    val title = json("title").str
    val authors = json("authors").arr.map(_.str).toVector
    val venue = json("venue").str
    val year = json("year").num.toInt
    Reference(title, authors, venue, year)
  }

}
