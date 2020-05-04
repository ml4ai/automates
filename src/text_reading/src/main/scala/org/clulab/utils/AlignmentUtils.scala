package org.clulab.utils

import org.clulab.aske.automates.OdinEngine
import org.clulab.aske.automates.apps.ExtractAndAlign.{getCommentDefinitionMentions, hasRequiredArgs}
import org.clulab.aske.automates.apps.{ExtractAndAlign, alignmentArguments}
import org.clulab.aske.automates.grfn.GrFNParser
import org.clulab.aske.automates.grfn.GrFNParser.{mkCommentTextElement, parseCommentText}
import org.clulab.grounding.sparqlResult
import org.clulab.odin.serialization.json.JSONSerializer
import org.clulab.processors.Document
import ujson.{Obj, Value}
import ujson.json4s._

import scala.collection.mutable.ArrayBuffer


object AlignmentJsonUtils {
  /**stores methods that are specific to processing json with alignment components;
    * other related methods are in GrFNParser*/

  /**get arguments for the aligner depending on what data are provided**/
  def getArgsForAlignment(jsonPath: String, json: Value, groundToSVO: Boolean): alignmentArguments = {

    val jsonKeys = json.obj.keys.toList

    val svoGroundings = if (groundToSVO) {
      if (jsonKeys.contains("SVOgroundings")) {
        Some(json("SVOgroundings").arr.map(v => v.obj("variable").str -> v.obj("groundings").arr.map(gr => new sparqlResult(gr("searchTerm").str, gr("osvTerm").str, gr("className").str, Some(gr("score").arr.head.num), gr("source").str)).toSeq).toMap)
      } else None

    } else None


    // load text mentions
    val definitionMentions =  if (jsonKeys.contains("mentions")) {
      val ujsonMentions = json("mentions") //the mentions loaded from json in the ujson format
      //transform the mentions into json4s format, used by mention serializer
      val jvalueMentions = upickle.default.transform(
        ujsonMentions
      ).to(Json4sJson)
      val textMentions = JSONSerializer.toMentions(jvalueMentions)

      Some(textMentions
        .filter(m => m.label matches "Definition")
        .filter(hasRequiredArgs))
    } else None

    // get the equations
    val equationChunksAndSource = if (jsonKeys.contains("equations")) {
      val equations = json("equations").arr
      Some(ExtractAndAlign.processEquations(equations))
    } else None

//    for (item <- equationChunksAndSource.get) println(item._1 + " | " + item._2)

    val variableNames = if (jsonKeys.contains("source_code")) {
      Some(json("source_code").obj("variables").arr.map(_.obj("name").str))
    } else None
    // The variable names only (excluding the scope info)
    val variableShortNames = if (variableNames.isDefined) {
      var shortNames = GrFNParser.getVariableShortNames(variableNames.get)
      Some(shortNames)
    } else None
    // source code comments

    val source = if (variableNames.isDefined) {
      Some(getSourceFromSrcVariables(variableNames.get))
    } else None

    val commentDefinitionMentions = if (jsonKeys.contains("source_code")) {

      val localCommentReader = OdinEngine.fromConfigSectionAndGrFN("CommentEngine", jsonPath)
      Some(getCommentDefinitionMentions(localCommentReader, json, variableShortNames, source)
        .filter(hasRequiredArgs))
    } else None



    new alignmentArguments(json, variableNames, variableShortNames, commentDefinitionMentions, definitionMentions, equationChunksAndSource, svoGroundings)
  }

  def getVariables(json: Value): Seq[String] = json("source_code")
    .obj("variables")
    .arr.map(_.obj("name").str)

  def getVariableShortNames(json: Value): Seq[String] = {
    getVariableShortNames(getVariables(json))
  }

  def getSourceFromSrcVariables(variables: Seq[String]): String = {
    // fixme: getting source from all variables provided---if there are more than one, the source field will list all of them; need a different solution if the source is different for every variable/comment
    variables.map(name => name.split("::")(1)).distinct.mkString(";")
  }

  def getVariableShortNames(variableNames: Seq[String]): Seq[String] = for (
    name <- variableNames
  ) yield name.split("::").reverse.slice(1, 2).mkString("")

  def getCommentDocs(json: Value, source: Option[String]): Seq[Document] = {
    val source_file = if (source.isDefined) source.get else "Unknown"
    val sourceCommentObject = json("source_code").obj("comments").obj
    val commentTextObjects = new ArrayBuffer[Obj]()

    val keys = sourceCommentObject.keys
    for (k <- keys) {
      if (sourceCommentObject(k).isInstanceOf[Value.Arr]) {
        val text = sourceCommentObject(k).arr.map(_.str).mkString("")
        if (text.length > 0) {
          commentTextObjects.append(mkCommentTextElement(text, source.get, k, ""))
        }
      } else {
        for (item <- sourceCommentObject(k).obj) if (item._2.isInstanceOf[Value.Arr]) {
          val value = item._2
          for (str <- value.arr) if (value.arr.length > 0) {
            val text = str.str
            if (text.length > 0) {
              commentTextObjects.append(mkCommentTextElement(text, source.get, k, item._1))
            }
          }
        }
      }
    }

    // Parse the comment texts
    commentTextObjects.map(parseCommentText(_))
  }

}

