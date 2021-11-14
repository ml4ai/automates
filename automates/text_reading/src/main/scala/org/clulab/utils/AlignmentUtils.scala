package org.clulab.utils

import java.io.File
import ai.lum.common.FileUtils._
import org.clulab.aske.automates.OdinEngine
import org.clulab.aske.automates.apps.ExtractAndAlign.{getCommentDescriptionMentions, hasRequiredArgs, hasUnitArg}
import org.clulab.aske.automates.apps.{AlignmentArguments, AlignmentBaseline, AutomatesExporter, ExtractAndAlign}
import org.clulab.aske.automates.grfn.GrFNParser
import org.clulab.aske.automates.grfn.GrFNParser.{mkCommentTextElement, parseCommentText}
import org.clulab.aske.automates.serializer.AutomatesJSONSerializer
import org.clulab.grounding.{sparqlResult, sparqlWikiResult}
import org.clulab.odin.serialization.json.JSONSerializer
import org.clulab.processors.Document
import ujson.{Obj, Value}
import ujson.json4s._
import upickle.default.macroRW
import upickle.default.{ReadWriter, macroRW}

import java.util.UUID.randomUUID
import scala.collection.mutable
import scala.collection.mutable.ArrayBuffer


object AlignmentJsonUtils {
  /**stores methods that are specific to processing json with alignment components;
    * other related methods are in GrFNParser*/

  case class GlobalVariable(id: String, identifier: String, textVarObjStrings: Seq[String], textFromAllDescrs: Seq[String], groundings: Option[Seq[sparqlWikiResult]])

  object GlobalVariable {
    implicit val rw: ReadWriter[GlobalVariable] = macroRW
  }

  case class SeqOfGlobalVariables(globalVars: Seq[GlobalVariable])

  object SeqOfGlobalVariables {
    implicit val rw: ReadWriter[SeqOfGlobalVariables] = macroRW
  }

  case class GlobalEquationVariable(id: String, identifier: String, eqVarObjStrings: Seq[String])

  case class GlobalSrcVariable(id: String, identifier: String, srcVarObjStrings: Seq[String])

  /**get arguments for the aligner depending on what data are provided**/
  def getArgsForAlignment(jsonPath: String, json: Value, groundToSVO: Boolean, groundToWiki: Boolean, serializerName: String): AlignmentArguments = {

    val wikigroundings: Option[Map[String, Seq[sparqlWikiResult]]] = if (groundToWiki) {
      val pathToWikiGroundings = json("wikidata").str

      // load if exist; none otherwise
      if (pathToWikiGroundings != "None") {
        val groundingsAsUjson = ujson.read(new File(pathToWikiGroundings))
        val groundingMap = mutable.Map[String, Seq[sparqlWikiResult]]()
        for (item <- groundingsAsUjson("wikiGroundings").arr) {
          val identString = item.obj("variable").str
          val groundings = item.obj("groundings").arr.map(gr => new sparqlWikiResult(gr("searchTerm").str, gr("conceptID").str, gr("conceptLabel").str, Some(gr("conceptDescription").arr.map(_.str).mkString(" ")), Some(gr("alternativeLabel").arr.map(_.str).mkString(" ")), Some(gr("subClassOf").arr.map(_.str).mkString(" ")), Some(gr("score").arr.head.num), gr("source").str)).toSeq
          groundingMap(identString) = groundings
        }
        Some(groundingMap.toMap)
      } else None

    } else None

    val jsonObj = json.obj
    // load text mentions
    val allMentions =  if (jsonObj.contains("mentions")) {
      val mentionsPath = json("mentions").str
      val mentionsFile = new File(mentionsPath)
      val textMentions =  if (serializerName == "AutomatesJSONSerializer") {
        val ujsonOfMenFile = ujson.read(mentionsFile)
        AutomatesJSONSerializer.toMentions(ujsonOfMenFile)
      } else {
        val ujsonMentions = ujson.read(mentionsFile.readString())
        //transform the mentions into json4s format, used by mention serializer
        val jvalueMentions = upickle.default.transform(
          ujsonMentions
        ).to(Json4sJson)
        JSONSerializer.toMentions(jvalueMentions)
      }
      Some(textMentions)
    } else None

    val descriptionMentions = if (allMentions.nonEmpty) {
      Some(allMentions
        .get
        .filter(m => m.label.contains("Description"))
        .filter(m => hasRequiredArgs(m, "description")))
    } else None

    val parameterSettingMentions = if (allMentions.nonEmpty) {
      Some(allMentions
        .get
        .filter(m => m.label matches "ParameterSetting")
        )
    } else None


    val intervalParameterSettingMentions = if (allMentions.nonEmpty) {
      Some(allMentions
        .get
        .filter(m => m.label matches "IntervalParameterSetting")
      )
    } else None


    val unitMentions = if (allMentions.nonEmpty) {
      Some(allMentions
        .get
        .filter(m => m.label matches "UnitRelation")
        )
    } else None

    // get the equations
    val equationChunksAndSource = if (jsonObj.contains("equations")) {
      val equations = json("equations").arr
      Some(ExtractAndAlign.processEquations(equations))
    } else None

    val identifierNames = if (jsonObj.contains("source_code")) {
      Some(json("source_code").obj("variables").arr.map(_.obj("name").str))
    } else None
    // The identifier names only (excluding the scope info)
    val identifierShortNames = if (identifierNames.isDefined) {
      var shortNames = GrFNParser.getVariableShortNames(identifierNames.get)
      Some(shortNames)
    } else None

    // source code comments
    val source = if (identifierNames.isDefined) {
      Some(getSourceFromSrcIdentifiers(identifierNames.get))
    } else None

    val commentDescriptionMentions = if (jsonObj.contains("source_code")) {

      if (jsonObj.contains("comment_mentions")) {
        println("ATTENTION: using previously extracted comment mentions")
        val mentionsPath = json("comment_mentions").str
        val mentionsFile = new File(mentionsPath)
        val textMentions =  if (serializerName == "AutomatesJSONSerializer") {
          val ujsonOfMenFile = ujson.read(mentionsFile)
          AutomatesJSONSerializer.toMentions(ujsonOfMenFile)
        } else {
          val ujsonMentions = ujson.read(mentionsFile.readString())
          //transform the mentions into json4s format, used by mention serializer
          val jvalueMentions = upickle.default.transform(
            ujsonMentions
          ).to(Json4sJson)
          JSONSerializer.toMentions(jvalueMentions)
        }

        Some(textMentions)
      } else {
        val localCommentReader = OdinEngine.fromConfigSectionAndGrFN("CommentEngine", jsonPath)
        Some(getCommentDescriptionMentions(localCommentReader, json, identifierShortNames, source)
          .filter(m => hasRequiredArgs(m, "description")))
      }

    } else None

    // uncomment and add outfile path to serialize comment mentions
    // val outputFile = ""
//    val exporter = AutomatesExporter(outputFile)
//    exporter.export(commentDescriptionMentions.get)


    //deserialize svo groundings if a) grounding svo and b) if svo groundings have been provided in the input
    val svoGroundings = if (groundToSVO) {
      if (jsonObj.contains("SVOgroundings")) {
        Some(json("SVOgroundings").arr.map(v => v.obj("variable").str -> v.obj("groundings").arr.map(gr => new sparqlResult(gr("searchTerm").str, gr("osvTerm").str, gr("className").str, Some(gr("score").arr.head.num), gr("source").str)).toSeq).map(item => (item._1, item._2)))
      } else None

    } else None



    AlignmentArguments(json, identifierNames, identifierShortNames, commentDescriptionMentions, descriptionMentions, parameterSettingMentions, intervalParameterSettingMentions, unitMentions, equationChunksAndSource, svoGroundings, wikigroundings)
  }

  def getVariables(json: Value): Seq[String] = json("source_code")
    .obj("variables")
    .arr.map(_.obj("name").str)

  def getIdentifierShortNames(json: Value): Seq[String] = {
    getIdentifierShortNames(getVariables(json))
  }

  def getSourceFromSrcIdentifiers(identifiers: Seq[String]): String = {
    // fixme: getting source from all variables provided---if there are more than one, the source field will list all of them; need a different solution if the source is different for every variable/comment
    identifiers.map(name => name.split("::")(1)).distinct.mkString(";")
  }

  def getIdentifierShortNames(identifierNames: Seq[String]): Seq[String] = for (
    name <- identifierNames
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
          for (str <- value.arr) if (value.arr.nonEmpty) {
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

  /* Methods for getting global variables */
  def mkGlobalEqVarLinkElement(glv: GlobalEquationVariable): String = {
    ujson.Obj(
      "uid" -> glv.id,
      "content" -> glv.identifier,
      "identifier_objects" -> glv.eqVarObjStrings
    ).toString()
  }

  def mkGlobalSrcVarLinkElement(glv: GlobalSrcVariable): String = {
    ujson.Obj(
      "uid" -> glv.id,
      "content" -> glv.identifier,
      "identifier_objects" -> glv.srcVarObjStrings
    ).toString()

  }
  //searchTerm: String, conceptID: String, conceptLabel: String, conceptDescription: Option[String], alternativeLabel: Option[String], score: Option[Double], source: String = "Wikidata"
  def groundingToJson(grounding: sparqlWikiResult): ujson.Obj = {
    val descriptions = if (grounding.conceptDescription.nonEmpty) grounding.conceptDescription.get else ujson.Null
    val score = if (grounding.score.nonEmpty) grounding.score.get else ujson.Null
    val toReturn = ujson.Obj(
      "search_term" -> grounding.searchTerm,
      "concept_ID" -> grounding.conceptID,
      "concept_label" -> grounding.conceptLabel,
      "source" -> grounding.source
    )

    if (grounding.conceptDescription.isDefined) {
      toReturn("concept_description") = grounding.conceptDescription.get
    } else {
      toReturn("concept_description") = ujson.Null
    }

    if (grounding.alternativeLabel.isDefined) {
      toReturn("alternative_labels") = grounding.alternativeLabel.get
    } else {
      toReturn("alternative_labels") = ujson.Null
    }

    if (grounding.subClassOf.isDefined) {
      toReturn("subClassOf") = grounding.subClassOf.get
    } else {
      toReturn("subClassOf") = ujson.Null
    }

    if (grounding.score.isDefined) {
      toReturn("score") = grounding.score.get
    } else {
      toReturn("score") = ujson.Null
    }

    toReturn

  }

  def mkGlobalVarLinkElement(glv: GlobalVariable): String = {
    val toReturn = ujson.Obj(
      "uid" -> glv.id,
      "content" -> glv.identifier,
      "identifier_objects" -> glv.textVarObjStrings.map(obj => ujson.read(obj).obj("uid").str)
    )

    if (glv.groundings.isDefined) {
      toReturn("groundings") = glv.groundings.get.map(o => groundingToJson(o))
    } else {
      toReturn("groundings") = ujson.Null
    }

    toReturn.toString()
  }

  def getGlobalSrcVars(srcVars: Seq[Value]): Seq[GlobalSrcVariable] = {
    val groupedVars = srcVars.groupBy(_.obj("content").str)
    val allGlobalVars = new ArrayBuffer[GlobalSrcVariable]()
    for (gr <- groupedVars) {
      val glVarID = randomUUID().toString()
      val identifier = gr._1
      val srcVarObjs = gr._2.map(_.obj("uid").str)
      val glVar = new GlobalSrcVariable(glVarID, identifier, srcVarObjs)
      allGlobalVars.append(glVar)
    }
    allGlobalVars
  }

  def getSrcLinkElements(srcVars: Seq[String]): Seq[Value] = {
    srcVars.map { varName =>
      val split = varName.split("::")
      ujson.Obj(
        "uid" -> randomUUID.toString,
        "source" -> varName,
        "content" -> split.takeRight(2).head,
        "model" -> split.takeRight(3).head
      )
    }
  }


  def getGlobalEqVars(equationLinkElements: Seq[Value]): Seq[GlobalEquationVariable] = {


    val groupedVars = equationLinkElements.groupBy(_.obj("content").str)
    val allEqGlobalVars = new ArrayBuffer[GlobalEquationVariable]()
    for (gr <- groupedVars) {
      val glVarID = randomUUID().toString()

      val identifier = AlignmentBaseline.replaceGreekWithWord(gr._1, AlignmentBaseline.greek2wordDict.toMap).replace("\\\\", "")
      // the commented out part is for debugging
      val eqLinkElementObjs = gr._2.map(le => le.obj("uid").str) // + "::" + le.obj("content").str)
      val glVar = new GlobalEquationVariable(glVarID, identifier, eqLinkElementObjs)
      allEqGlobalVars.append(glVar)

    }

    allEqGlobalVars
  }

}
