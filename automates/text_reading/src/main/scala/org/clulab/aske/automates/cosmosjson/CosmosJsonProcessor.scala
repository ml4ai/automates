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

  def combineBlocks(cosmosObjects: Seq[CosmosObject] ): Seq[CosmosObject] = {
    val newBlocks = new ArrayBuffer[CosmosObject]()
    val (onlyBodyTextBlocks, otherBlocks) = cosmosObjects.filter(_.content.get.nonEmpty).partition(_.detectCls.get == "Body Text")
//    for (obtb <- onlyBodyTextBlocks) println("obtb: " + obtb)
    val blockEndPunkt = Seq(".", ":")
    for ((block, idx) <- onlyBodyTextBlocks.zipWithIndex) {
//      println("Block: " + block)
      if (idx == 0) {
        newBlocks.append(block)
      }
      //else if (idx == onlyBodyTextBlocks.length - 1) {
        //newBlocks.append(block)
      //}
    else {
        val previousBlock = newBlocks.last
//        println("->" + previousBlock.content.get)
//        println(">>" + block.content.get)
        if (!previousBlock.content.get.endsWith(blockEndPunkt) && block.content.get.head.isLower) {
        // then combine
        // need to skip the next combined then
        //
        //        pdfName: Option[String],
        //        pageNum: Option[Seq[Int]],
        //        blockIdx: Option[Seq[Int]],
        //        content: Option[String],
        //        cls: Option[String], //postprocess_cls (class)
        //        detectCls: Option[String],
        //        postprocessScore: Option[Double]

        val newBlock = CosmosObject(
          block.pdfName,
          Some(previousBlock.pageNum.get ++ block.pageNum.get),
          Some(previousBlock.blockIdx.get ++ block.blockIdx.get),
          Some(previousBlock.content.get ++ " " ++ block.content.get),
          previousBlock.cls,
          previousBlock.detectCls,
          previousBlock.postprocessScore
        )
        newBlocks -= previousBlock
        newBlocks.append(newBlock)
      } else {
        newBlocks.append(block)
      }
    }
    }
    newBlocks ++ otherBlocks
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
    CosmosDocument(combineBlocks(cosmosObjects))
  }

  // for handling bad OCR
  def addSpaces(string: String): String = {
    val newString = string.replaceAll(" (where|by|and|if|of)", " $1 ").replaceAll("  ", " ")
    newString

  }

  def mkCosmosObject(json: ujson.Js, blockIdx: Int): CosmosObject = {
    val pdfName = json.obj.get("pdf_name").map(_.str)
    val content = addSpaces(org.apache.commons.text.StringEscapeUtils.unescapeJava(json("content").str)).replace("- ", "")
    val pageNum = json("page_num").num.toInt
    val cls = json("postprocess_cls").str
    val detectCls = json("detect_cls").str
    val postprocessScore = json("postprocess_score").num

    CosmosObject(pdfName, Some(Seq(pageNum)), Some(Seq(blockIdx)), Some(content), Some(cls), Some(detectCls), Some(postprocessScore)) //todo: add bounding box?
  }


}
