package org.clulab.aske.automates.apps

import java.io.{File, PrintWriter}
import java.util.UUID

import ai.lum.common.ConfigUtils._
import ai.lum.common.FileUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.aske.automates.data.{DataLoader, TextRouter, TokenizedLatexDataLoader}
import org.clulab.aske.automates.alignment.{Aligner, Alignment, AlignmentHandler, VariableEditDistanceAligner}
import org.clulab.aske.automates.grfn.GrFNParser.{mkHypothesis, mkLinkElement, mkTextLinkElement, mkTextVarLinkElement, mkTextVarLinkElementForModelComparison}
import org.clulab.aske.automates.OdinEngine
import org.clulab.aske.automates.apps.AlignmentBaseline.{greek2wordDict, word2greekDict}
import org.clulab.aske.automates.grfn.GrFNParser
import org.clulab.odin.Mention
import org.clulab.utils.{AlignmentJsonUtils, DisplayUtils, FileUtils}
import org.slf4j.LoggerFactory
import ujson.{Obj, Value}
import org.clulab.grounding.{SVOGrounder, sparqlResult}
import org.clulab.odin.serialization.json.JSONSerializer
import java.util.UUID.randomUUID
import org.clulab.aske.automates.attachments.{AutomatesAttachment, MentionLocationAttachment}


import scala.collection.mutable
import scala.collection.mutable.ArrayBuffer

case class alignmentArguments(json: Value, variableNames: Option[Seq[String]], variableShortNames: Option[Seq[String]], commentDefinitionMentions: Option[Seq[Mention]], definitionMentions: Option[Seq[Mention]], parameterSettingMentions: Option[Seq[Mention]], unitMentions: Option[Seq[Mention]], equationChunksAndSource: Option[Seq[(String, String)]], svoGroundings: Option[ArrayBuffer[(String, Seq[sparqlResult])]])

object ExtractAndAlign {
  val COMMENT = "comment"
  val TEXT = "text"
  val TEXT_VAR = "text_var"
  val SOURCE = "source"
  val EQUATION = "equation"
  val FULL_TEXT_EQUATION = "fullTextEquation"
  val SVO_GROUNDING = "SVOgrounding"
  val SRC_TO_COMMENT = "sourceToComment"
  val TEXT_TO_UNIT = "textToUnit"
  val TEXT_TO_UNIT_THROUGH_DEFINITION = "textToUnitThroughDefinition"
  val TEXT_TO_PARAM_SETTING = "textToParamSetting"
  val EQN_TO_TEXT = "equationToText"
  val COMMENT_TO_TEXT = "commentToText"
  val TEXT_TO_SVO = "textToSVO"
  val DEFINITION = "definition"
  val VARIABLE = "variable"
  val DEF_LABEL = "Definition"
  val PARAMETER_SETTING_LABEL = "ParameterSetting"
  val UNIT_LABEL = "Unit"

  val logger = LoggerFactory.getLogger(this.getClass())


  val config = ConfigFactory.load()
  val pdfAlignDir = config[String]("apps.pdfalignDir")

  def groundMentions(
                      grfn: Value,
                      variableNames: Option[Seq[String]],
                      variableShortNames: Option[Seq[String]],
                      definitionMentions: Option[Seq[Mention]],
                      parameterSettingMention: Option[Seq[Mention]],
                      unitMentions: Option[Seq[Mention]],
                      commentDefinitionMentions: Option[Seq[Mention]],
                      equationChunksAndSource: Option[Seq[(String, String)]],
                      SVOgroundings: Option[ArrayBuffer[(String, Seq[sparqlResult])]],
                      groundToSVO: Boolean,
                      maxSVOgroundingsPerVar: Int,
                      alignmentHandler: AlignmentHandler,
                      numAlignments: Option[Int],
                      numAlignmentsSrcToComment: Option[Int],
                      scoreThreshold: Double = 0.0,
                      appendToGrFN: Boolean,
                      debug: Boolean

    ): Value = {

    // =============================================
    // Alignment
    // =============================================

    val alignments = alignElements(
      alignmentHandler,
      definitionMentions,
      parameterSettingMention,
      unitMentions,
      equationChunksAndSource,
      commentDefinitionMentions,
      variableShortNames,
      SVOgroundings,
      numAlignments,
      numAlignmentsSrcToComment,
      scoreThreshold
    )

    var outputJson = ujson.Obj()

    val linkElements = getLinkElements(grfn, definitionMentions, commentDefinitionMentions, equationChunksAndSource, variableNames)

//    linkElements(TEXT_VAR) = updateTextVarsWithUnits(linkElements(TEXT_VAR), unitMentions, alignments(TEXT_TO_UNIT_THROUGH_DEFINITION), alignments(TEXT_TO_UNIT))

//    linkElements(TEXT_VAR) = updateTextVarsWithParamSettings(linkElements(TEXT_VAR), parameterSettingMention, alignments(TEXT_TO_PARAM_SETTING))

    linkElements(TEXT_VAR) =  if (groundToSVO) {
      // update if svo groundings have been previously extracted or set to none to be extracted during rehydrateLinkElement
      if (alignments.contains("TEXT_TO_SVO")) {
        updateTextVarsWithSVO(linkElements(TEXT_VAR), SVOgroundings, alignments(TEXT_TO_SVO))
      } else linkElements(TEXT_VAR).map(tvle => updateTextVariable(tvle, "None"))

    } else linkElements(TEXT_VAR).map(tvle => updateTextVariable(tvle, "None"))

    for (le <- linkElements.keys) {
      outputJson(le) = linkElements(le).map{element => rehydrateLinkElement(element, groundToSVO, maxSVOgroundingsPerVar, false)}
    }

    val hypotheses = getLinkHypotheses(linkElements.toMap, alignments, debug)
    outputJson("links") = hypotheses

    // the produced hypotheses can be either appended to the input file as "groundings" or returned as a separate ujson object
    if (appendToGrFN) {
      // Add the grounding links to the GrFN
      GrFNParser.addHypotheses(grfn, hypotheses)
    } else outputJson
  }

  def updateTextVariable(textVarLinkElementString: String, update: String): String = {
    textVarLinkElementString + "::" + update

  }

  def updateTextVariable(textVarLinkElementString: String, update: Object): String = {
    val updateString = update.toString()
    textVarLinkElementString + "::" + updateString

  }

  def updateTextVarsWithUnits(textVarLinkElements: Seq[String], unitMentions: Option[Seq[Mention]], textToUnitThroughDefAlignments: Seq[Seq[Alignment]], textToUnitAlignments: Seq[Seq[Alignment]]): Seq[String] = {

    // fixme: units can come through links directly to vars or to "definitions"; use this to analyze diff types of unit extractions
//    println("through def: ")
//    for ((topKThroughDef, i) <- textToUnitThroughDefAlignments.zipWithIndex) {
////      println(topK.head.src + " " + topK.head.dst)
//      for (al <- topKThroughDef) {
//        println("i: " + i)
//        println("text var link el: " + textVarLinkElements(al.src))
//        println("Unit: " + unitMentions.get(al.dst).arguments("unit").head.text)
//        println("updated: " + updateTextVariable(textVarLinkElements(al.src), unitMentions.get(al.dst).arguments("unit").head.text))
//
//      }
//    }
//    println("through var: ")
//    for ((topKThroughDef, i) <- textToUnitAlignments.zipWithIndex) {
//      //      println(topK.head.src + " " + topK.head.dst)
//      for (al <- topKThroughDef) {
//        println("i: " + i)
//        println("text var link el: " + textVarLinkElements(al.src))
//        println("Unit: " + unitMentions.get(al.dst).arguments("unit").head.text)
//        println("updated: " + updateTextVariable(textVarLinkElements(al.src), unitMentions.get(al.dst).arguments("unit").head.text))
//
//      }
//    }

    val updatedTextVars = if (textToUnitThroughDefAlignments.length > 0) {

      for {
        topK <- textToUnitThroughDefAlignments
        alignment <- topK
        textVarLinkElement = textVarLinkElements(alignment.src)
        unit = if (hasArg(unitMentions.get(alignment.dst), "unit")) {
          unitMentions.get(alignment.dst).arguments("unit").head.text
        } else null

        score = alignment.score
      } yield updateTextVariable(textVarLinkElement, unit)
    } else textVarLinkElements.map(el => updateTextVariable(el, null))

    updatedTextVars

  }

  def updateTextVarsWithSVO(textVarLinkElements: Seq[String], SVOgroundings: Option[ArrayBuffer[(String, Seq[sparqlResult])]], textToSVOAlignments: Seq[Seq[Alignment]]): Seq[String] = {

    val updatedTextVars = if (textToSVOAlignments.length > 0) {

      for {
        topK <- textToSVOAlignments
        alignment <- topK
        textVarLinkElement = textVarLinkElements(alignment.src)
        svoGrounding = if (SVOgroundings.nonEmpty) {
          ujson.Obj("grounding" -> SVOgroundings.get(alignment.dst)._2.map(sr => GrFNParser.sparqlResultTouJson(sr)))
        } else null
        score = alignment.score
      } yield updateTextVariable(textVarLinkElement, svoGrounding)
    } else textVarLinkElements.map(tvle => updateTextVariable(tvle, null))



    updatedTextVars

  }

  def hasArg(mention: Mention, arg: String): Boolean = {
    mention.arguments.contains(arg)
  }

  def updateTextVarsWithParamSettings(textVarLinkElements: Seq[String], paramSettingMentions: Option[Seq[Mention]], textToParamSettingAlignments: Seq[Seq[Alignment]]): Seq[String] = {

    val updatedTextVars = if (textToParamSettingAlignments.nonEmpty) {
      for {
        topK <- textToParamSettingAlignments
        alignment <- topK
        textVarLinkElement = textVarLinkElements(alignment.src)
        value = if (hasArg(paramSettingMentions.get(alignment.dst), "value")) {
          paramSettingMentions.get(alignment.dst).arguments("value").head.text
        } else null

        valueLeast = if (hasArg(paramSettingMentions.get(alignment.dst), "valueLeast")) {
          paramSettingMentions.get(alignment.dst).arguments("valueLeast").head.text
        } else null

        valueMost = if (hasArg(paramSettingMentions.get(alignment.dst), "valueMost")) {
          paramSettingMentions.get(alignment.dst).arguments("valueMost").head.text
        } else null


        update = value + "::" + valueLeast + "::" + valueMost
        score = alignment.score
      } yield updateTextVariable(textVarLinkElement, update)
    } else textVarLinkElements.map(el => updateTextVariable(el, "null::null::null"))

    updatedTextVars
  }

  def rehydrateLinkElement(element: String, groundToSvo: Boolean, maxSVOgroundingsPerVar: Int, debug: Boolean): ujson.Obj = {

    //todo: add more informative source by type, e.g., for text var it's "text" (check with ph about this)

    val splitElStr = element.split("::")
    for (el <- splitElStr) println("el: " + el)
    println("----")
    val elType = splitElStr(1)

    elType match {
      case "text_var" => {
        val id = splitElStr(0)
        val source = splitElStr(2)
        val identifier = splitElStr(3)
        val originalSentence = splitElStr(4)
        val definition = splitElStr(5)
        val svo_terms = splitElStr(7)
//        val unit = splitElStr(9)
//        val value = splitElStr(10)
//        val valueLeast = splitElStr(11)
//        val valueMost = splitElStr(12)
        val svoString = splitElStr(9)
        val locationJsonStr = splitElStr(8)
        println("svo: " + svoString)
        println("loc: " + locationJsonStr)


        val locationAsJson = ujson.read(locationJsonStr)

        val results = if (groundToSvo) {
          if (svoString != "None") {
            val updateJson = ujson.read(svoString)
            ujson.Arr(updateJson("grounding").arr.map(sr => ujson.Obj("osv_term" -> sr("osv_term").str, "class_name" -> sr("class_name").str, "score" -> sr("score").num, "source" -> sr("source").str)))
          } else {
            logger.info("Querying SVO server")
            SVOGrounder.groundTermsToSVOandRank(identifier, svo_terms.split(","), maxSVOgroundingsPerVar)
          }
        } else ujson.Null

//        val paramSetting = ujson.Obj()
//
//        if (value == "null") paramSetting("value") = ujson.Null
//        if (valueLeast == "null") paramSetting("valueLeast") = ujson.Null
//        if (valueMost == "null") paramSetting("valueMost") = ujson.Null

        mkTextVarLinkElement(
          uid = id,
          source = source,
          originalSentence = originalSentence,
          identifier = identifier,
          definition = definition,
          svo_terms = svo_terms,
//          unit = unit,
//          paramSetting = paramSetting,
          svo = results,
          spans = locationAsJson
        )

      }



      case "text_var_for_model_comparison" => {
        val id = splitElStr(0)
        val source = splitElStr(2)
        val identifier = splitElStr(3)
        val originalSentence = splitElStr(4)
        val definition = splitElStr(5)

        mkTextVarLinkElementForModelComparison(
          uid = id,
          source = source,
          originalSentence = originalSentence,
          identifier = identifier,
          definition = definition,
          debug = debug
        )

      }


      case "identifier" => {
        val id = splitElStr(0)
        val source = splitElStr(2)
        val identifier = splitElStr.takeRight(3)(0)

        mkLinkElement(
          id = id,
          source = source,
          content = identifier,
          contentType = "null"
        )
      }
      case "fullTextEquation" => {
        val id = splitElStr(0)
        val equation = splitElStr(2)

        mkLinkElement(
          id = id,
          source = "text",
          content = equation,
          contentType = "null"
        )

      }
      case _ => {
        val id = splitElStr(0)
        val elType = splitElStr(1)
        val source = splitElStr(2)
        val content = splitElStr(3)

        mkLinkElement(
          id = id,
          source = source,
          content = content,
          contentType = "null"
        )

      }
    }
  }

  def hasRequiredArgs(m: Mention): Boolean = m.arguments.contains(VARIABLE) && m.arguments.contains(DEFINITION)

  def hasUnitArg(m: Mention): Boolean = m.arguments.contains("unit")

  def loadEquations(filename: String): Seq[(String, String)] = {
    val equationDataLoader = new TokenizedLatexDataLoader
    val equations = equationDataLoader.loadFile(new File(filename))
    // tuple pairing each chunk with the original latex equation it came from
    for {
      sourceEq <- equations
      eqChunk <- filterEquations(equationDataLoader.chunkLatex(sourceEq))
    } yield (eqChunk, sourceEq)
  }

  def processEquations(equationsVal: Value): Seq[(String, String)] = {
    val equationDataLoader = new TokenizedLatexDataLoader
    val equations = equationsVal.arr.map(_.str)
    // tuple pairing each chunk with the original latex equation it came from
    for {
      sourceEq <- equations
      eqChunk <- filterEquations(equationDataLoader.chunkLatex(sourceEq))
    } yield (eqChunk, sourceEq)
  }

  /**get rid of chunks that are not good equation variable candidates and replace spelled out greek letters with unicode to make sure they are not lost during rendering */
  def filterEquations(equations: Seq[String]): Seq[String] = {
    equations.filter(cand => cand.count(char => char.isDigit) < 2) //to eliminate chunks that have numerical data in them
      .filter(cand => is_balanced(cand)) //todo: check this if missing vars
      .map(c => AlignmentBaseline.replaceWordWithGreek(c, word2greekDict.toMap)) //before filtering out latex control sequences, change greek letters from latex control spelling; it will be switch back to word while creating the link element
      .filter(chunk => !chunk.matches("&?\\\\\\w+&?")) //to eliminate standalone latex control sequences, e.g., \\times (they can have ampersands on each side)
  }

  def getTextMentions(textReader: OdinEngine, dataLoader: DataLoader, textRouter: TextRouter, files: Seq[File]): (Seq[Mention], Seq[Mention], Seq[Mention]) = {
    val textMentions = files.par.flatMap { file =>
      logger.info(s"Extracting from ${file.getName}")
      val texts: Seq[String] = dataLoader.loadFile(file)
      // Route text based on the amount of sentence punctuation and the # of numbers (too many numbers = non-prose from the paper)
      texts.flatMap(text => textRouter.route(text).extractFromText(text, filename = Some(file.getName)))
    }
    logger.info(s"Extracted ${textMentions.length} text mentions")
    val onlyEventsAndRelations = textMentions.seq.filter(m => m.matches("EventMention") || m.matches("RelationMention"))
    (onlyEventsAndRelations.filter(_ matches DEF_LABEL), onlyEventsAndRelations.filter(_ matches PARAMETER_SETTING_LABEL), onlyEventsAndRelations.filter(_ matches UNIT_LABEL))
  }

  def getCommentDefinitionMentions(commentReader: OdinEngine, alignmentInputFile: Value, variableShortNames: Option[Seq[String]], source: Option[String]): Seq[Mention] = {
    val commentDocs = if (alignmentInputFile.obj.get("source_code").isDefined) {
      AlignmentJsonUtils.getCommentDocs(alignmentInputFile, source)
    } else GrFNParser.getCommentDocs(alignmentInputFile)

    // Iterate through the docs and find the mentions; eliminate duplicates
    val commentMentions = commentDocs.flatMap(doc => commentReader.extractFrom(doc)).distinct

    val definitions = commentMentions.seq.filter(_ matches DEF_LABEL)

    if (variableShortNames.isEmpty) return definitions
    val overlapsWithVariables = definitions.filter(
      m => variableShortNames.get
        .map(string => string.toLowerCase)
        .contains(m.arguments(VARIABLE).head.text.toLowerCase)
    )
    overlapsWithVariables
  }

  def alignElements(
    alignmentHandler: AlignmentHandler,
    textDefinitionMentions: Option[Seq[Mention]],
    parameterSettingMentions: Option[Seq[Mention]],
    unitMentions: Option[Seq[Mention]],
    equationChunksAndSource: Option[Seq[(String, String)]],
    commentDefinitionMentions: Option[Seq[Mention]],
    variableShortNames: Option[Seq[String]],
    SVOgroundings: Option[ArrayBuffer[(String, Seq[sparqlResult])]],
    numAlignments: Option[Int],
    numAlignmentsSrcToComment: Option[Int],
    scoreThreshold: Double): Map[String, Seq[Seq[Alignment]]] = {


    val alignments = scala.collection.mutable.HashMap[String, Seq[Seq[Alignment]]]()

    if (commentDefinitionMentions.isDefined && variableShortNames.isDefined) {
      val varNameAlignments = alignmentHandler.editDistance.alignTexts(variableShortNames.get.map(_.toLowerCase), commentDefinitionMentions.get.map(Aligner.getRelevantText(_, Set("variable"))).map(_.toLowerCase()))
      // group by src idx, and keep only top k (src, dst, score) for each src idx, here k = 1
      alignments(SRC_TO_COMMENT) = Aligner.topKBySrc(varNameAlignments, numAlignmentsSrcToComment.get)
    }

    /** Align text variable to unit variable
      * this should take care of unit relaions like this: "T = daily mean air temperature [°C]"
      */
    // todo: add these to updateTextVarsWithUnits; currently, just linking through definitions
    if (textDefinitionMentions.isDefined && unitMentions.isDefined) {
      val varNameAlignments = alignmentHandler.editDistance.alignTexts(textDefinitionMentions.get.map(Aligner.getRelevantText(_, Set("variable"))).map(_.toLowerCase), unitMentions.get.map(Aligner.getRelevantText(_, Set("variable"))).map(_.toLowerCase()))
      // group by src idx, and keep only top k (src, dst, score) for each src idx, here k = 1
      alignments(TEXT_TO_UNIT) = Aligner.topKBySrc(varNameAlignments, 1)
    }

    /** Align text variable to unit variable
      * this should take care of unit relaions like this: "T = daily mean air temperature [°C]"
      */
    if (textDefinitionMentions.isDefined && SVOgroundings.isDefined) {
      val varNameAlignments = alignmentHandler.editDistance.alignTexts(textDefinitionMentions.get.map(Aligner.getRelevantText(_, Set("variable"))).map(_.toLowerCase), SVOgroundings.get.map(_._1.toLowerCase))

      // group by src idx, and keep only top k (src, dst, score) for each src idx, here k = 1
      alignments(TEXT_TO_SVO) = Aligner.topKBySrc(varNameAlignments, 1)
    }

    /** Align text definition to unit variable
      * this should take care of unit relations like this: The density of water is taken as 1.0 Mg m-3.
      */
    if (textDefinitionMentions.isDefined && unitMentions.isDefined) {
      val varNameAlignments = alignmentHandler.editDistance.alignTexts(textDefinitionMentions.get.map(Aligner.getRelevantText(_, Set("definition"))).map(_.toLowerCase), unitMentions.get.map(Aligner.getRelevantText(_, Set("variable"))).map(_.toLowerCase()))
      // group by src idx, and keep only top k (src, dst, score) for each src idx, here k = 1
      alignments(TEXT_TO_UNIT_THROUGH_DEFINITION) = Aligner.topKBySrc(varNameAlignments, 1)
    }

    /** Align text variable to param setting variable
      * this should take care of unit relaions like this: The density of water is taken as 1.0 Mg m-3.
      */
    if (textDefinitionMentions.isDefined && parameterSettingMentions.isDefined) {
      val varNameAlignments = alignmentHandler.editDistance.alignTexts(textDefinitionMentions.get.map(Aligner.getRelevantText(_, Set("variable"))).map(_.toLowerCase), parameterSettingMentions.get.map(Aligner.getRelevantText(_, Set("variable"))).map(_.toLowerCase()))
      // group by src idx, and keep only top k (src, dst, score) for each src idx, here k = 1
      alignments(TEXT_TO_PARAM_SETTING) = Aligner.topKBySrc(varNameAlignments, 1)
    }


    /** Align the equation chunks to the text definitions */
      if (equationChunksAndSource.isDefined && textDefinitionMentions.isDefined) {
        val equationToTextAlignments = alignmentHandler.editDistance.alignEqAndTexts(equationChunksAndSource.get.unzip._1, textDefinitionMentions.get.map(Aligner.getRelevantText(_, Set("variable"))))
        // group by src idx, and keep only top k (src, dst, score) for each src idx
        alignments(EQN_TO_TEXT) = Aligner.topKBySrc(equationToTextAlignments, numAlignments.get)
      }

    /** Align the comment definitions to the text definitions */
    if (commentDefinitionMentions.isDefined && textDefinitionMentions.isDefined) {
      val commentToTextAlignments = alignmentHandler.w2v.alignMentions(commentDefinitionMentions.get, textDefinitionMentions.get)
      // group by src idx, and keep only top k (src, dst, score) for each src idx
      alignments(COMMENT_TO_TEXT) = Aligner.topKBySrc(commentToTextAlignments, numAlignments.get, scoreThreshold, debug = false)
    }

    alignments.toMap
  }

  def getLinkElements(
    grfn: Value,
    textDefinitionMentions:
    Option[Seq[Mention]],
    commentDefinitionMentions: Option[Seq[Mention]],
    equationChunksAndSource: Option[Seq[(String, String)]],
    variableNames: Option[Seq[String]]
  ): mutable.HashMap[String, Seq[String]] = {
    // Make Comment Spans from the comment variable mentions
    val linkElements = scala.collection.mutable.HashMap[String, Seq[String]]()

    if (commentDefinitionMentions.isDefined) {
      linkElements(COMMENT) = commentDefinitionMentions.get.map { commentMention => {
        randomUUID + "::" + "comment_span" + "::" + commentMention.document.id.getOrElse("unk_file").toString + "::" +commentMention.arguments(DEFINITION).head.text + "::" + "null"

      }

      }
    }


    // Repeat for src code variables
    if (variableNames.isDefined) {
      linkElements(SOURCE) = variableNames.get.map { varName =>

        randomUUID + "::" + "identifier" + "::" + varName.split("::")(1) + "::" + varName + "::" + "null"

      }
    }


//     Repeat for text variables
    if (textDefinitionMentions.isDefined) {
      linkElements(TEXT) = textDefinitionMentions.get.map { mention =>
        val docId = mention.document.id.getOrElse("unk_text_file")
        val sent = mention.sentence
        val offsets = mention.tokenInterval.toString()
        randomUUID + "::" + "text_span" +"::" +  s"${docId}_sent${sent}_$offsets" + "::" + mention.arguments(DEFINITION).head.text + "::" + "null"
      }
    }

    def getDiscontinuousText(mention: Mention): String = {
      val subStrings = new ArrayBuffer[String]()
      val discontAttachment = mention.attachments.map(_.asInstanceOf[AutomatesAttachment].toUJson).filter(_("attType").str == "DiscontinuousCharOffset").head // for now, assume there's only one
      val charOffset = discontAttachment("charOffsets").arr
      val docText = mention.document.text.getOrElse("No text")
      for (offsetSet <- charOffset) {
        val start = offsetSet.arr.head.num.toInt
        val end = offsetSet.arr.last.num.toInt
        subStrings.append(docText.slice(start, end).mkString(""))
      }
      subStrings.mkString(" ")
    }

    if (textDefinitionMentions.isDefined) {

      // todo: merge if same text var but diff definitions? if yes, needs to be done here before the randomUUID is assigned; check with ph
      linkElements(TEXT_VAR) = textDefinitionMentions.get.map { mention =>
        val docId = mention.document.id.getOrElse("unk_text_file")
        val sent = mention.sentence
        val originalSentence = mention.sentenceObj.words.mkString(" ")
        val offsets = mention.tokenInterval.toString()
        val textVar = mention.arguments(VARIABLE).head.text

        val definition = if (mention.attachments.nonEmpty && mention.attachments.exists(_.asInstanceOf[AutomatesAttachment].toUJson.obj("attType").str == "DiscontinuousCharOffset")) {
          getDiscontinuousText(mention)
        } else {
          mention.arguments(DEFINITION).head.text
        }

        val charBegin = mention.startOffset
        val charEnd = mention.endOffset

        val continuousMenSpanJson = if (mention.attachments.exists(_.asInstanceOf[AutomatesAttachment].toUJson.obj("attType").str == "MentionLocation")) {

          val menAttAsJson = mention.attachments.map(_.asInstanceOf[AutomatesAttachment].toUJson.obj).filter(_("attType").str=="MentionLocation").head//head.asInstanceOf[MentionLocationAttachment].toUJson.obj
          val page = menAttAsJson("pageNum").num.toInt
          val block = menAttAsJson("blockIdx").num.toInt

          // todo: this is for mentions that came from one block
          // mentions that come from separate cosmos blocks will require additional processing and can have two location spans
          ujson.Obj(
            "page" -> page,
            "block" -> block,
            "span" -> ujson.Obj(
              "char_begin" -> charBegin,
              "char_end" -> charEnd
                      )
                    )
        } else {
          ujson.Obj(
            "page" -> ujson.Null,
            "block" -> ujson.Null,
            "span" -> ujson.Obj(
              "char_begin" -> charBegin,
              "char_end" -> charEnd
            )
          )
        }
          randomUUID + "::" + "text_var" + "::" + s"${docId}_sent${sent}_$offsets" + "::" + s"${textVar}" + "::" + s"${originalSentence}" + "::" + s"${definition}" + "::"  +  "null" + "::" + SVOGrounder.getTerms(mention).getOrElse(Seq.empty).mkString(",") + "::" + continuousMenSpanJson.toString()

      }
    }


    // Repeat for Eqn Variables
    if (equationChunksAndSource.isDefined) {
      val equation2uuid = mutable.Map[String, UUID]()
      linkElements(EQUATION) = equationChunksAndSource.get.map { case (chunk, orig) =>
        if (equation2uuid.contains(orig)) {
          randomUUID + "::" + "equation_span" + "::" + equation2uuid(orig) + "::" + AlignmentBaseline.replaceGreekWithWord(chunk, greek2wordDict.toMap) + "::" + "null"
        } else {
          val id = randomUUID
          equation2uuid(orig) = id
          randomUUID + "::" + "equation_span" + "::" + id + "::" + AlignmentBaseline.replaceGreekWithWord(chunk, greek2wordDict.toMap) + "::" + "null"
        }
      }

      linkElements(FULL_TEXT_EQUATION) = equation2uuid.keys.map(key => equation2uuid(key).toString() + "::" + "fullTextEquation" + "::" + key ).toSeq
    }

    linkElements
  }


  def getInterModelComparisonLinkElements(
                       defMentions1:
                       Seq[Mention],
                       defMention2: Seq[Mention]
                     ): Map[String, Seq[String]] = {

    val linkElements = scala.collection.mutable.HashMap[String, Seq[String]]()


      // todo: merge if same text var but diff definitions? if yes, needs to be done here before the randomUUID is assigned; check with ph - do not merge
      linkElements("TEXT_VAR1") = defMentions1.map { mention =>
        val docId = mention.document.id.getOrElse("unk_text_file")
        val sent = mention.sentence
        val originalSentence = mention.sentenceObj.words.mkString(" ")
        val offsets = mention.tokenInterval.toString()
        val textVar = mention.arguments(VARIABLE).head.text
        val definition = mention.arguments(DEFINITION).head.text


        randomUUID + "::" + "text_var_for_model_comparison" + "::" + s"${docId}_sent${sent}_$offsets" + "::" + s"${textVar}" + "::" + s"${originalSentence}" + "::" + s"${definition}"
      }

      linkElements("TEXT_VAR2") = defMention2.map { mention =>
        val docId = mention.document.id.getOrElse("unk_text_file")
        val sent = mention.sentence
        val originalSentence = mention.sentenceObj.words.mkString(" ")
        val offsets = mention.tokenInterval.toString()
        val textVar = mention.arguments(VARIABLE).head.text
        val definition = mention.arguments(DEFINITION).head.text


        randomUUID + "::" + "text_var_for_model_comparison" + "::" + s"${docId}_sent${sent}_$offsets" + "::" + s"${textVar}" + "::" + s"${originalSentence}" + "::" + s"${definition}"
      }

    linkElements.toMap
  }

  def getInterModelComparisonLinkElements(
                                       paper1Objects:
                                       Seq[ujson.Value],
                                       paper1id: String,
                                       paper2Objects: Seq[ujson.Value],
                                       paper2id: String
                                     ): Map[String, Seq[ujson.Value]] = {

    val linkElements = scala.collection.mutable.HashMap[String, Seq[ujson.Value]]()


    // todo: merge if same text var but diff definitions? if yes, needs to be done here before the randomUUID is assigned; check with ph - do not merge
    val updatedWithPaperId1 = for {
      o <- paper1Objects
      updated = ujson.Obj(
      "var_uid" -> o.obj("var_uid"),
      "code_identifier"-> o.obj("code_identifier"),
      "text_definition"-> o.obj("text_definition"),
      "text_identifier"-> o.obj("text_identifier"),
        "grfn1_var_uid" -> paper1id
      )
    } yield updated

    val updatedWithPaperId2 = for {
      o <- paper2Objects
      updated = ujson.Obj(
        "var_uid" -> o.obj("var_uid"),
        "code_identifier"-> o.obj("code_identifier"),
        "text_definition"-> o.obj("text_definition"),
        "text_identifier"-> o.obj("text_identifier"),
        "grfn2_var_uid" -> paper2id
      )
    } yield updated


    linkElements("grfn1_vars") = updatedWithPaperId1

    linkElements("grfn2_vars") = updatedWithPaperId2
    linkElements.toMap
  }


//  def mkLinkHypothesisTextVarDef(variables: Seq[Obj], definitions: Seq[Obj]): Seq[Obj] = {

  def mkLinkHypothesisTextVarDef(variables: Seq[String], definitions: Seq[String], debug: Boolean): Seq[Obj] = {

    assert(variables.length == definitions.length)
    for {
      i <- variables.indices
    } yield mkHypothesis(variables(i), definitions(i), 1.0, debug)
  }


  def mkLinkHypothesis(srcElements: Seq[String], dstElements: Seq[String], alignments: Seq[Seq[Alignment]], debug: Boolean): Seq[Obj] = {

    for {
      topK <- alignments
      alignment <- topK
      srcLinkElement = srcElements(alignment.src)
      dstLinkElement = dstElements(alignment.dst)
      score = alignment.score
    } yield mkHypothesis(srcLinkElement, dstLinkElement, score, debug)
  }

  def mkLinkHypothesisFromValueSequences(srcElements: Seq[Value], dstElements: Seq[Value], alignments: Seq[Seq[Alignment]], debug: Boolean): Seq[Obj] = {

    for {
      topK <- alignments
      alignment <- topK
      srcLinkElement = srcElements(alignment.src)
      dstLinkElement = dstElements(alignment.dst)
      score = alignment.score
    } yield mkHypothesis(srcLinkElement, dstLinkElement, score, debug)
  }



  def getLinkHypotheses(linkElements: Map[String, Seq[String]], alignments: Map[String, Seq[Seq[Alignment]]], debug: Boolean): Seq[Obj] = {//, SVOGroungings: Map[String, Seq[sparqlResult]]): Seq[Obj] = {
    // Store them all here
    val hypotheses = new ArrayBuffer[ujson.Obj]()
    val linkElKeys = linkElements.keys.toSeq
    // Comment -> Text
    if (linkElKeys.contains(COMMENT) && linkElKeys.contains(TEXT_VAR)) {
      hypotheses.appendAll(mkLinkHypothesis(linkElements(COMMENT), linkElements(TEXT_VAR), alignments(COMMENT_TO_TEXT), debug))
    }


    // Src Variable -> Comment
    if (linkElKeys.contains(SOURCE) && linkElKeys.contains(COMMENT)) {
      println("has source and comment")
      hypotheses.appendAll(mkLinkHypothesis(linkElements(SOURCE), linkElements(COMMENT), alignments(SRC_TO_COMMENT), debug))
    }


    // Equation -> Text
    if (linkElKeys.contains(EQUATION) && linkElKeys.contains(TEXT_VAR)) {
      println("has eq and text")
      hypotheses.appendAll(mkLinkHypothesis(linkElements(EQUATION), linkElements(TEXT_VAR), alignments(EQN_TO_TEXT), debug))
    }

    // TextVar -> TextDef (text_span)
    //taken care of while creating link elements
    if (linkElKeys.contains(TEXT_VAR) && linkElKeys.toSeq.contains(TEXT)) {
      hypotheses.appendAll(mkLinkHypothesisTextVarDef(linkElements(TEXT_VAR), linkElements(TEXT), debug))
    }

    hypotheses
  }


  def getInterPaperLinkHypotheses(linkElements: Map[String, Seq[String]], alignment: Seq[Seq[Alignment]], debug: Boolean): Seq[Obj] = {
    val paper1LinkElements = linkElements("TEXT_VAR1")
    val paper2LinkElements = linkElements("TEXT_VAR2")
    val hypotheses = new ArrayBuffer[ujson.Obj]()
    hypotheses.appendAll(mkLinkHypothesis(paper1LinkElements, paper2LinkElements, alignment, debug))
    hypotheses
  }

  def getInterPaperLinkHypothesesWithValues(linkElements: Map[String, Seq[Value]], alignment: Seq[Seq[Alignment]], debug: Boolean): Seq[Obj] = {
    val paper1LinkElements = linkElements("grfn1_vars")
    val paper2LinkElements = linkElements("grfn2_vars")
    val hypotheses = new ArrayBuffer[ujson.Obj]()
    hypotheses.appendAll(mkLinkHypothesisFromValueSequences(paper1LinkElements, paper2LinkElements, alignment, debug))
    hypotheses
  }

  def is_balanced(string: String): Boolean = {
    is_balanced_delim(string, "(", ")") && is_balanced_delim(string, "{", "}") && is_balanced_delim(string, "[", "]")
  }

  def is_balanced_delim(string: String, open_delim: String, close_delim: String): Boolean = {
    var n_open = 0
    for (char <- string) {
      if (char.toString == open_delim) n_open += 1 else if (char.toString == close_delim) n_open -= 1
      if (n_open < 0) return false

    }
    n_open == 0
  }

  def main(args: Array[String]): Unit = {
    val toAlign = Seq("Comment", "Text", "Equation")
    val groundToSVO = true //load from config
    val maxSVOgroundingsPerVar = 5 //load from config
    val config: Config = ConfigFactory.load()
    val numAlignments = config[Int]("apps.numAlignments") // for all but srcCode to comment, which we set to top 1
    val scoreThreshold = config[Double]("apps.commentTextAlignmentScoreThreshold")
    val loadMentions = config[Boolean]("apps.loadMentions")
    val appendToGrFN = config[Boolean]("apps.appendToGrFN")
    val serializerName = config[String]("apps.serializerName")

    // =============================================
    //                 DATA LOADING
    // =============================================

    // Instantiate the text reader
    val textConfig: Config = config[Config]("TextEngine")
    val textReader = OdinEngine.fromConfig(textConfig)

    // Instantiate the comment reader
    val localCommentReader = OdinEngine.fromConfig(config[Config]("CommentEngine"))
    // todo: future readers
    //    val glossaryReader = OdinEngine.fromConfig(config[Config]("GlossaryEngine"))
    //    val tocReader = OdinEngine.fromConfig(config[Config]("TableOfContentsEngine"))
    val textRouter = new TextRouter(Map(TextRouter.TEXT_ENGINE -> textReader, TextRouter.COMMENT_ENGINE -> localCommentReader))

    // Load a GrFN
    val grfnPath: String = config[String]("apps.grfnFile")
    val grfnFile = new File(grfnPath)
    val grfn = ujson.read(grfnFile.readString())

    val source = if (grfn.obj.get("source").isDefined) {
      Some(grfn.obj("source").arr.mkString(";"))
    } else None
    // Get source variables
    val variableNames = Some(GrFNParser.getVariables(grfn))
    val variableShortNames = Some(GrFNParser.getVariableShortNames(variableNames.get))

    // Get comment definitions
    val commentDefinitionMentions = getCommentDefinitionMentions(localCommentReader, grfn, variableShortNames, source)
      .filter(hasRequiredArgs)

    val allUsedTextMentions = if (loadMentions) {
      val mentionsFile = new File(config[String]("apps.mentionsFile"))
      (JSONSerializer.toMentions(mentionsFile).filter(_.label matches "Definition"),
        JSONSerializer.toMentions(mentionsFile).filter(_.label matches "ParameterSetting"),
        JSONSerializer.toMentions(mentionsFile).filter(_.label matches "Unit"))
    } else {
      val inputDir = config[String]("apps.inputDirectory")
      val inputType = config[String]("apps.inputType")
      val dataLoader = DataLoader.selectLoader(inputType) // txt, json (from science parse), pdf supported
      val files = FileUtils.findFiles(inputDir, dataLoader.extension)
      getTextMentions(textReader, dataLoader, textRouter, files)

    }
    val textDefinitionMentions = allUsedTextMentions._1
    val parameterSettingMentions = allUsedTextMentions._2
    val unitMentions = allUsedTextMentions._3
    logger.info(s"Extracted ${textDefinitionMentions.length} definitions from text")

    // Load equations and "extract" variables/chunks (using heuristics)
    val equationFile: String = config[String]("apps.predictedEquations")
    val equationChunksAndSource = Some(loadEquations(equationFile))

    // Make an alignment handler which handles all types of alignment being used
    val alignmentHandler = new AlignmentHandler(config[Config]("alignment"))

    // Ground the extracted text mentions, the comments, and the equation variables to the grfn variables
    val groundedGrfn = groundMentions(
      grfn: Value,
      variableNames,
      variableShortNames,
      Some(textDefinitionMentions),
      Some(parameterSettingMentions),
      Some(unitMentions),
      Some(commentDefinitionMentions),
      equationChunksAndSource,
      None, //not passing svo groundings from grfn
      groundToSVO: Boolean,
      maxSVOgroundingsPerVar: Int,
      alignmentHandler,
      Some(numAlignments),
      Some(numAlignments),
      scoreThreshold,
      appendToGrFN,
      debug = false
      )


    // Export
    val outputDir = config[String]("apps.outputDirectory")
    val grfnBaseName = new File(grfnPath).getBaseName()
    val grfnWriter = new PrintWriter(s"$outputDir/${grfnBaseName}_with_groundings.json")
    ujson.writeTo(groundedGrfn, grfnWriter)
    grfnWriter.close()



//For debugging:
//        topKCommentToText.foreach { aa =>
//          println("====================================================================")
//          println(s"              SRC VAR: ${commentDefinitionMentions(aa.head.src).arguments("variable").head.text}")
//          println("====================================================================")
//          aa.foreach { topK =>
//            val v1Text = commentDefinitionMentions(topK.src).text
//            val v2Text = textDefinitionMentions(topK.dst).text
//            println(s"aligned variable (comment): ${commentDefinitionMentions(topK.src).arguments("variable").head.text} ${commentDefinitionMentions(topK.src).arguments("variable").head.foundBy}")
//            println(s"aligned variable (text): ${textDefinitionMentions(topK.dst).arguments("variable").head.text}")
//            println(s"comment: ${v1Text}")
//            println(s"text: ${v2Text}")
//              println(s"text: ${v2Text} ${textDefinitionMentions(topK.dst).label} ${textDefinitionMentions(topK.dst).foundBy}") //printing out the label and the foundBy helps debug rules
//            println(s"score: ${topK.score}\n")
//          }
//        }
  }


}
