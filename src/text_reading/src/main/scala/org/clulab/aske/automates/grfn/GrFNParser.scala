package org.clulab.aske.automates.grfn

import ai.lum.common.FileUtils._
import java.io.File

import org.clulab.grounding.{Grounding, sparqlResult}
import org.clulab.processors.Document
import org.clulab.processors.fastnlp.FastNLPProcessor
import org.json4s.jackson.Json
import ujson.{Obj, Value}

import scala.collection.mutable.ArrayBuffer

object GrFNParser {

  def addHypotheses(grfn: Value, hypotheses: Seq[Obj]): Value = {
    grfn("grounding") = hypotheses.toList
    grfn
  }

  def getVariableShortNames(variableNames: Seq[String]): Seq[String] = for (
    name <- variableNames
  ) yield name.split("::").reverse.slice(1, 2).mkString("")

  def getVariableShortNames(grfn: Value): Seq[String] = {
    getVariableShortNames(getVariables(grfn))
  }

  def getVariables(grfn: Value): Seq[String] = grfn("variables").arr.map(_.obj("name").str)

  def getCommentDocs(grfn: Value): Seq[Document] = {

    val sourceCommentObject = grfn("source_comments").obj
    val commentTextObjects = new ArrayBuffer[Obj]()

    val keys = sourceCommentObject.keys
    for (k <- keys) {
      if (sourceCommentObject(k).isInstanceOf[Value.Arr]) {
        val text = sourceCommentObject(k).arr.map(_.str).mkString("")
        if (text.length > 0) {
          commentTextObjects.append(mkCommentTextElement(text, grfn("source").arr.head.str, k, ""))
        }
      } else {
        for (item <- sourceCommentObject(k).obj) if (item._2.isInstanceOf[Value.Arr]) {
          val value = item._2
          for (str <- value.arr) if (value.arr.length > 0) {
            val text = str.str
            if (text.length > 0) {
              commentTextObjects.append(mkCommentTextElement(text, grfn("source").arr.head.str, k, item._1))
            }
          }
        }
      }
    }

    // Parse the comment texts
    commentTextObjects.map(parseCommentText(_))
  }


  def parseCommentText(textObj: Obj): Document = {
    val proc = new FastNLPProcessor()
    //val Docs = Source.fromFile(filename).getLines().mkString("\n")
    val text = textObj("text").str
    val lines = for (sent <- text.split("\n") if ltrim(sent).length > 1 //make sure line is not empty
      && sent.stripMargin.replaceAll("^\\s*[C!]", "!") //switch two different comment start symbols to just one
      .startsWith("!")) //check if the line is a comment based on the comment start symbol (todo: is there a regex version of startWith to avoide prev line?
      yield ltrim(sent)
    var lines_combined = Array[String]()
    // which lines we want to ignore (for now, may change later)
    val ignoredLines = "(^Function:|^Calculates|^Calls:|^Called by:|([\\d\\?]{1,2}\\/[\\d\\?]{1,2}\\/[\\d\\?]{4})|REVISION|head:|neck:|foot:|SUBROUTINE|Subroutine|VARIABLES|Variables|State variables)".r

    for (line <- lines if ignoredLines.findAllIn(line).isEmpty) {
      if (line.startsWith(" ") && lines.indexOf(line) != 0) { //todo: this does not work if there happens to be more than five spaces between the comment symbol and the comment itself---will probably not happen too frequently. We shouldn't make it much more than 5---that can effect the lines that are indented because they are continuations of previous lines---that extra indentation is what helps us know it's not a complete line.
        var prevLine = lines(lines.indexOf(line) - 1)
        if (lines_combined.contains(prevLine)) {
          prevLine = prevLine + " " + ltrim(line)
          lines_combined = lines_combined.slice(0, lines_combined.length - 1)
          lines_combined = lines_combined :+ prevLine
        }
      }
      else {
        if (!lines_combined.contains(line)) {
          lines_combined = lines_combined :+ line
        }
      }
    }

    val doc = proc.annotateFromSentences(lines_combined, keepText = true)
    //include more detailed info about the source of the comment: the container and the location in the container (head/neck/foot)
    doc.id = Option(textObj("source").str + "; " + textObj("container").str + "; " + textObj("location").str)
    doc
  }

  def ltrim(s: String): String = s.replaceAll("^\\s*[C!]?[-=]*\\s{0,5}", "")



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

  def mkTextLinkElement(elemType: String, source: String, content: String, contentType: String, svoQueryTerms: Seq[String]): ujson.Obj = {
    val linkElement = ujson.Obj(
      "type" -> elemType,
      "source" -> source,
      "content" -> content,
      "content_type" -> contentType,
      "svo_query_terms" -> svoQueryTerms
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

  def mkSVOElement(grounding: sparqlResult): ujson.Obj = {
    val linkElement = ujson.Obj(
      "type" -> "svo_grounding",
      "source" -> "svo_ontology",
      "content" -> sparqlResultTouJson(grounding)
    )
    linkElement
  }

  def mkSVOElement(grounding: Grounding): ujson.Obj = {
    val linkElement = ujson.Obj(
      "type" -> "svo_grounding",
      "source" -> "svo_ontology",
      "content" -> ujson.Arr(grounding.groundings.map(gr => sparqlResultTouJson(gr)))
    )
    linkElement
  }

  //losing the score from the sparqlResult bc the score goes to the hypothesis and not the link element
  def sparqlResultTouJson(grounding: sparqlResult): ujson.Obj = {
    val sparqlResuJson = ujson.Obj(
      "osv_term" -> grounding.osvTerm,
      "class_name" -> grounding.className,
      "source" -> grounding.source
    )
    sparqlResuJson
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
