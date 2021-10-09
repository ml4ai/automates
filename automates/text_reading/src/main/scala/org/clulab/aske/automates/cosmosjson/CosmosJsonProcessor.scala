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

  // for handling bad OCR
  def addSpaces(string: String): String = {
    val newString = string.replaceAll(" (where|by|and|if|of)", " $1 ").replaceAll("  ", " ")
    newString

  }

  def mkCosmosObject(json: ujson.Js, blockIdx: Int): CosmosObject = {
    val pdfName = json.obj.get("pdf_name").map(_.str)
    val content = addSpaces(org.apache.commons.text.StringEscapeUtils.unescapeJava(json("content").str))
    val pageNum = json("page_num").num.toInt
    val cls = json("postprocess_cls").str
    val detectCls = json("detect_cls").str
    val postprocessScore = json("postprocess_score").num
    val detect_cls = json("detect_cls").str

    CosmosObject(pdfName, Some(pageNum), Some(blockIdx), Some(content), Some(cls), Some(detectCls), Some(postprocessScore)) //todo: add bounding box?
  }


}
