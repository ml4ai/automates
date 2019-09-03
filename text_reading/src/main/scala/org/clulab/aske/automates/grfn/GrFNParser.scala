package org.clulab.aske.automates.grfn

import ai.lum.common.FileUtils._
import java.io.File

object GrFNParser {

  //------------------------------------------------------
  //     Methods for creating GrFNDocuments
  //------------------------------------------------------

  def mkLinkElement(elemType: String, source: String, content: String, contentType: String): ujson.Obj = {
    val linkElement = ujson.Obj(
      "type" -> elemType,
      "source" -> source,
      "content" -> content,
      "content_type" -> contentType
    )
    linkElement
  }


  def mkCommentTextElement(text: String, source: String, container: String, location: String): ujson.Obj = {
    val commentTextElement = ujson.Obj(
      "text" -> text,
      "source" -> source,
      "container" -> container,
      "location" -> location
    )
    commentTextElement
  }

  def mkHypothesis(elem1: ujson.Obj, elem2: ujson.Obj, score: Double): ujson.Obj = {
    val hypothesis = ujson.Obj(
      "element_1" -> elem1,
      "element_2" -> elem2,
      "score" -> score
    )
    hypothesis
  }


  def mkDocument(file: File): GrFNDocument = {
    val json = ujson.read(file.readString())
    mkDocument(json)
  }

  def mkDocument(json: ujson.Js): GrFNDocument = {
    val functions: Vector[GrFNFunction] = json("functions").arr.map(mkFunction).toVector
    val start: String = json("start").str
    val name: Option[String] = json.obj.get("name").map(_.str)
    val dateCreated: String = json("dateCreated").str
    GrFNDocument(functions, start, name, dateCreated, None, None) // fixme
  }

  def mkFunction(json: ujson.Js): GrFNFunction = {
    val name: String = json("name").str
    val functionType: Option[String] = json.obj.get("functionType").map(_.str)
    val sources: Option[Vector[GrFNSource]] = json.obj.get("sources").map(_.arr.map(mkSource).toVector)
    //val body: Option[Vector[GrFNBody]] = json.obj.get("body").map(_.arr.map(mkBody).toVector) // fixme!!
    val target: Option[String] = json.obj.get("target").map(_.str)
    val input: Option[Vector[GrFNVariable]] = json.obj.get("input").map(_.arr.map(mkInput).toVector)
    val variables: Option[Vector[GrFNVariable]] = json.obj.get("variables").map(_.arr.map(mkVariable).toVector)
    GrFNFunction(name, functionType, sources, None, target, input, variables)
  }


  def mkSource(json: ujson.Js): GrFNSource = {
    val name = json("name").str
    val sourceType = json("type").str
    GrFNSource(name, sourceType)
  }

  def mkBody(json: ujson.Js): GrFNBody = {
    val bodyType: Option[String] = json.obj.get("bodyType").map(_.str)
    val name: String = json("name").str
    val reference: Option[Int] = json.obj.get("reference").map(_.num.toInt)
    GrFNBody(bodyType, name, reference)
  }

  // fixme: same as mkVariable???
  def mkInput(json: ujson.Js): GrFNVariable = {
    val name: String = json("name").str
    val domain: String = json("domain").str
    val description: Option[GrFNProvenance] = None // fixme
    GrFNVariable(name, domain, description)
  }

  def mkVariable(json: ujson.Js): GrFNVariable = {
    val name: String = json("name").str
    val domain: String = json("domain").str
    val description: Option[GrFNProvenance] = None // fixme
    GrFNVariable(name, domain, description)
  }

}
