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
    mkDocument(json)
  }

  def mkDocument(json: ujson.Js): CosmosDocument = {
    val cosmosObjects = new ArrayBuffer[CosmosObject]()

    var currentPage = 0
    var currentBlockIdx = 0
    for (block <- json.arr) {
      val newCurrentPage = block("page_num").num.toInt
      if (newCurrentPage > currentPage) {
        currentBlockIdx = 0
        currentPage = newCurrentPage
      } else currentBlockIdx += 1
      val cosObj = mkCosmosObject(block, currentBlockIdx)
      cosmosObjects.append(cosObj)
    }
    CosmosDocument(cosmosObjects)
  }

  def addSpaces(string: String): String = {
    val funcWords = Seq("by", "and", "if", "of")
//    println("STRING: " + string)
//    var newString = string
//    for (fw <- funcWords) {
////      val regex = f"\b${fw}"//(?=[A-Z])"
////      println("regex: " + regex)
//      newString.replaceAll(f"\b${fw}", f"${fw} ")
////      println(f"updated with $fw: $newString")
//
//    }
    val newString = string.replaceAll(" (where|by|and|if|of)", " $1 ").replaceAll("  ", " ")
//    println("updated: " + newString)
    newString

  }

  def mkCosmosObject(json: ujson.Js, blockIdx: Int): CosmosObject = {
    val pdfName = json.obj.get("pdf_name").map(_.str)
    // the apache conversion might not be necessary
    val content = addSpaces(org.apache.commons.text.StringEscapeUtils.unescapeJava(json("content").str))
//    println("\n\ncontent1 " + json("content").str)
//    println("\ncontent2 " + content)
    val pageNum = json("page_num").num.toInt
    val cls = json("postprocess_cls").str
    val detectCls = json("detect_cls").str
    val postprocessScore = json("postprocess_score").num

    CosmosObject(pdfName, Some(pageNum), Some(blockIdx), Some(content), Some(cls), Some(detectCls), Some(postprocessScore)) //todo: add bounding box?
  }


}
