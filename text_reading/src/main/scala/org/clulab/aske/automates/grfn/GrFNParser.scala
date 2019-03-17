package org.clulab.aske.automates.grfn

import ai.lum.common.FileUtils._
import java.io.File

object GrFNParser {

  //------------------------------------------------------
  //     Methods for creating GrFNDocuments
  //------------------------------------------------------

  def mkDocument(file: File): GrFNDocument = {
    val json = ujson.read(file.readString())
    mkDocument(json)
  }

  def mkDocument(json: ujson.Js): GrFNDocument = {
    val functions: Vector[GrFNFunction] = json("functions").arr.map(mkFunction).toVector
    val start: String = json("start").str
    val name: String = json("name").str
    val dateCreated: String = json("dateCreated").str
    GrFNDocument(functions, start, name, dateCreated)
  }

  def mkFunction(json: ujson.Js): GrFNFunction = {
    val name: String = json("name").str
    val functionType: Option[String] = json.obj.get("functionType").map(_.str)
    val sources: Option[Vector[GrFNSource]] = json.obj.get("sources").map(_.arr.map(mkSource).toVector)
    val body: Option[Vector[GrFNBody]] = json.obj.get("body").map(_.arr.map(mkBody).toVector)
    val target: Option[String] = json.obj.get("target").map(_.str)
    val input: Option[Vector[GrFNVariable]] = json.obj.get("input").map(_.arr.map(mkInput).toVector)
    val variables: Option[Vector[GrFNVariable]] = json.obj.get("variables").map(_.arr.map(mkVariable).toVector)
    GrFNFunction(name, functionType, sources, body, target, input, variables)
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
    GrFNVariable(name, domain)
  }

  def mkVariable(json: ujson.Js): GrFNVariable = {
    val name: String = json("name").str
    val domain: String = json("domain").str
    GrFNVariable(name, domain)
  }

}
