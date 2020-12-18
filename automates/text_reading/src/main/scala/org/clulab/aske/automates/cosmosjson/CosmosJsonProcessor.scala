package org.clulab.aske.automates.cosmosjson

import java.io.File
import java.nio.file.Path

import com.typesafe.config.Config
import ai.lum.common.ConfigUtils._
import ai.lum.common.FileUtils._

import scala.collection.mutable.ArrayBuffer

object CosmosJsonProcessor {
  def mkDocument(file: File): CosmosDocument = {
    val json = ujson.read(file.readString())
//    println("JSON: " + json)
    mkDocument(json)
  }

  def mkDocument(json: ujson.Js): CosmosDocument = {
//    val id = json("id").str
//    val title = json.obj.get("title").map(_.str)
//    val year = json.obj.get("year")
//    val authors = json("authors").arr.map(mkAuthor).toVector
//    val abstractText = json.obj.get("abstractText").map(_.str)
    val cosmosObjects = new ArrayBuffer[CosmosObject]()

    println("JSON: " + ujson.Arr)
    for (i <- json.arr) {
      val cosObj = mkCosmosObject(i)
      cosmosObjects.append(cosObj)
    }
//    val cosmosObjects = {
//      if (json.obj.get("sections").nonEmpty) Some(json("sections").arr.map(mkSection).toVector)
//      else None
//    }
//    val references = json("references").arr.map(mkReference).toVector
    CosmosDocument(cosmosObjects)
  }

  def mkCosmosObject(json: ujson.Js): CosmosObject = {
    val pdfName = json.obj.get("pdf_name").map(_.str)
    val content = json("content").str
    val pageNum = json("page_num").num
    val cls = json("postprocess_cls").str
    val postprocessScore = json("postprocess_score").num

    CosmosObject(pdfName, Some(pageNum), Some(content), Some(cls), Some(postprocessScore)) //todo: add bounding box
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
