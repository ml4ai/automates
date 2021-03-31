package org.clulab.aske.automates.apps

import java.io.{File, PrintWriter}
import java.util.UUID
import org.clulab.utils.TextUtils._

import ai.lum.common.ConfigUtils._
import ai.lum.common.FileUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.aske.automates.data.{DataLoader, TextRouter, TokenizedLatexDataLoader}
import org.clulab.aske.automates.alignment.{Aligner, Alignment, AlignmentHandler, VariableEditDistanceAligner}
import org.clulab.aske.automates.grfn.GrFNParser.{mkHypothesis, mkLinkElement, mkTextLinkElement, mkTextVarLinkElement, mkTextVarLinkElementForModelComparison}
import org.clulab.aske.automates.OdinEngine
import org.clulab.aske.automates.apps.AlignmentBaseline.{greek2wordDict, word2greekDict}
import org.clulab.aske.automates.grfn.GrFNParser
import org.clulab.odin.{Attachment, Mention}
import org.clulab.utils.{AlignmentJsonUtils, DisplayUtils, FileUtils}
import org.slf4j.LoggerFactory
import ujson.{Obj, Value}
import org.clulab.grounding.{SVOGrounder, sparqlResult}
import org.clulab.odin.serialization.json.JSONSerializer
import java.util.UUID.randomUUID
import org.clulab.aske.automates.attachments.{AutomatesAttachment, MentionLocationAttachment}

import scala.collection.mutable
import scala.collection.mutable.ArrayBuffer

case class alignmentArguments(json: Value, variableNames: Option[Seq[String]], variableShortNames: Option[Seq[String]], commentDefinitionMentions: Option[Seq[Mention]], definitionMentions: Option[Seq[Mention]], parameterSettingMentions: Option[Seq[Mention]], intervalParameterSettingMentions: Option[Seq[Mention]], unitMentions: Option[Seq[Mention]], equationChunksAndSource: Option[Seq[(String, String)]], svoGroundings: Option[ArrayBuffer[(String, Seq[sparqlResult])]])

object ExtractAndAlign {
  val COMMENT = "comment"
  val TEXT = "text"
  val TEXT_VAR = "text_var"
  val CONCEPT_PARAM_SETTING = "concept_param_setting"
  val VAR_PARAM_SETTING = "var_param_setting"
  val CONCEPT_UNIT = "concept_unit"
  val VAR_UNIT = "var_unit"
  val SOURCE = "source"
  val EQUATION = "equation"
  val FULL_TEXT_EQUATION = "full_text_equation"
  val SVO_GROUNDING = "SVOgrounding"
  val SRC_TO_COMMENT = "source_to_comment"
  val TEXT_VAR_TO_UNIT = "text_var_to_unit"
  val TEXT_TO_UNIT = "text_to_unit"
  val TEXT_VAR_TO_PARAM_SETTING = "text_var_to_param_setting"
  val TEXT_VAR_TO_INT_PARAM_SETTING = "text_var_to_int_param_setting"
  val TEXT_TO_INT_PARAM_SETTING = "text_to_int_param_setting"
  val TEXT_TO_PARAM_SETTING = "text_to_param_setting"
  val INT_PARAM_SETTING_THRU_CONCEPT = "int_param_setting_through_concept"
  val INT_PARAM_SETTING_THRU_VAR = "int_param_setting_through_var"
  val PARAM_SETTING_THRU_CONCEPT = "parameter_setting_through_concept"
  val PARAM_SETTING_THRU_VAR = "parameter_setting_through_var"
  val UNIT_THRU_VAR = "unit_through_var"
  val UNIT_THRU_CONCEPT = "unit_through_concept"
  val EQN_TO_TEXT = "equation_to_text"
  val COMMENT_TO_TEXT = "comment_to_text"
  val TEXT_TO_SVO = "textToSVO"
  val DEFINITION = "definition"
  val VARIABLE = "variable"
  val DEF_LABEL = "Definition"
  val PARAMETER_SETTING_LABEL = "parameter_setting"
  val INTERVAL_PARAMETER_SETTING_LABEL = "interval_parameter_setting"
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
                      intervalParameterSettingMentions: Option[Seq[Mention]],
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
      intervalParameterSettingMentions,
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

    val linkElements = getLinkElements(grfn, definitionMentions, commentDefinitionMentions, equationChunksAndSource, variableNames, parameterSettingMention, intervalParameterSettingMentions,  unitMentions)


    // fixme: rethink svo grounding
//    linkElements(TEXT_VAR) =  if (groundToSVO) {
//      // update if svo groundings have been previously extracted or set to none to be extracted during rehydrateLinkElement
//      if (alignments.contains("TEXT_TO_SVO")) {
//        updateTextVarsWithSVO(linkElements(TEXT_VAR), SVOgroundings, alignments(TEXT_TO_SVO))
//      } else linkElements(TEXT_VAR).map(tvle => updateTextVariable(tvle, "None"))
//
//    } else linkElements(TEXT_VAR).map(tvle => updateTextVariable(tvle, "None"))

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

  def rehydrateLinkElement(element: String, groundToSvo: Boolean, maxSVOgroundingsPerVar: Int, debug: Boolean): ujson.Value = {

    val ujsonObj = ujson.read(element).obj
    ujsonObj
  }

  def hasRequiredArgs(m: Mention, argLabel: String): Boolean = m.arguments.contains(VARIABLE) && m.arguments.contains(argLabel)

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

  def getTextMentions(textReader: OdinEngine, dataLoader: DataLoader, textRouter: TextRouter, files: Seq[File]): (Seq[Mention], Seq[Mention], Seq[Mention], Seq[Mention]) = {
    val textMentions = files.par.flatMap { file =>
      logger.info(s"Extracting from ${file.getName}")
      val texts: Seq[String] = dataLoader.loadFile(file)
      // Route text based on the amount of sentence punctuation and the # of numbers (too many numbers = non-prose from the paper)
      texts.flatMap(text => textRouter.route(text).extractFromText(text, filename = Some(file.getName)))
    }
    logger.info(s"Extracted ${textMentions.length} text mentions")
    val onlyEventsAndRelations = textMentions.seq.filter(m => m.matches("EventMention") || m.matches("RelationMention"))
    (onlyEventsAndRelations.filter(_ matches DEF_LABEL), onlyEventsAndRelations.filter(_ matches PARAMETER_SETTING_LABEL), onlyEventsAndRelations.filter(_ matches INTERVAL_PARAMETER_SETTING_LABEL), onlyEventsAndRelations.filter(_ matches UNIT_LABEL))
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


  def returnAttachmentOfAGivenType(atts: Set[Attachment], attType: String): AutomatesAttachment = {
    atts.map(att => att.asInstanceOf[AutomatesAttachment]).filter(aa => aa.toUJson("attType").str ==attType).head
  }

  def alignElements(
    alignmentHandler: AlignmentHandler,
    textDefinitionMentions: Option[Seq[Mention]],
    parameterSettingMentions: Option[Seq[Mention]],
    intParameterSettingMentions: Option[Seq[Mention]],
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

    /** Align text definition to unit variable
      * this should take care of unit relations like this: The density of water is taken as 1.0 Mg m-3.
      */
    if (textDefinitionMentions.isDefined && unitMentions.isDefined) {

      val (throughVar, throughConcept) = unitMentions.get.partition(m => returnAttachmentOfAGivenType(m.attachments, "UnitAtt").toUJson("attachedTo").str=="variable")

      // link the units attached to a var ('t' in 't is measured in days') to the variable of the definition mention ('t' in 't is time')
      if (throughVar.nonEmpty) {
        val varNameAlignments = alignmentHandler.editDistance.alignTexts(textDefinitionMentions.get.map(Aligner.getRelevantText(_, Set("variable"))).map(_.toLowerCase), throughVar.map(Aligner.getRelevantText(_, Set("variable"))).map(_.toLowerCase()))
        // group by src idx, and keep only top k (src, dst, score) for each src idx, here k = 1
        alignments(TEXT_VAR_TO_UNIT) = Aligner.topKBySrc(varNameAlignments, 1)
      }
      // link the params attached to a concept ('time' in 'time is measured in days') to the definition of the definition mention ('time' in 't is time')
      if (throughConcept.nonEmpty) {
        val varNameAlignments = alignmentHandler.editDistance.alignTexts(textDefinitionMentions.get.map(Aligner.getRelevantText(_, Set("definition"))).map(_.toLowerCase), throughConcept.map(Aligner.getRelevantText(_, Set("variable"))).map(_.toLowerCase()))
        // group by src idx, and keep only top k (src, dst, score) for each src idx, here k = 1
        alignments(TEXT_TO_UNIT) = Aligner.topKBySrc(varNameAlignments, 1)
      }
    }

    /** Align text variable to SVO groundings
      */
    if (textDefinitionMentions.isDefined && SVOgroundings.isDefined) {
      val varNameAlignments = alignmentHandler.editDistance.alignTexts(textDefinitionMentions.get.map(Aligner.getRelevantText(_, Set("variable"))).map(_.toLowerCase), SVOgroundings.get.map(_._1.toLowerCase))

      // group by src idx, and keep only top k (src, dst, score) for each src idx, here k = 1
      alignments(TEXT_TO_SVO) = Aligner.topKBySrc(varNameAlignments, 1)
    }


    /** Align text variable to param setting
      */
    if (textDefinitionMentions.isDefined && parameterSettingMentions.isDefined) {
      val (throughVar, throughConcept) = parameterSettingMentions.get.partition(m => returnAttachmentOfAGivenType(m.attachments, "ParamSetAtt").toUJson("attachedTo").str=="variable")

      // link the params attached to a var ('t' in 't = 5 (days)') to the variable of the definition mention ('t' in 't is time')
      if (throughVar.nonEmpty) {
        val varNameAlignments = alignmentHandler.editDistance.alignTexts(textDefinitionMentions.get.map(Aligner.getRelevantText(_, Set("variable"))).map(_.toLowerCase), throughVar.map(Aligner.getRelevantText(_, Set("variable"))).map(_.toLowerCase()))
        // group by src idx, and keep only top k (src, dst, score) for each src idx, here k = 1
        alignments(TEXT_VAR_TO_PARAM_SETTING) = Aligner.topKBySrc(varNameAlignments, 1)
      }

      // link the params attached to a concept ('time' in 'time is set to 5 days') to the definition of the definition mention ('time' in 't is time')
      if (throughConcept.nonEmpty) {
        val varNameAlignments = alignmentHandler.editDistance.alignTexts(textDefinitionMentions.get.map(Aligner.getRelevantText(_, Set("definition"))).map(_.toLowerCase), throughConcept.map(Aligner.getRelevantText(_, Set("variable"))).map(_.toLowerCase()))
        // group by src idx, and keep only top k (src, dst, score) for each src idx, here k = 1
        alignments(TEXT_TO_PARAM_SETTING) = Aligner.topKBySrc(varNameAlignments, 1)
      }

    }


    /** Align text variable to param setting interval
      */
    if (textDefinitionMentions.isDefined && intParameterSettingMentions.isDefined) {
      val (throughVar, throughConcept) = intParameterSettingMentions.get.partition(m => returnAttachmentOfAGivenType(m.attachments, "ParamSettingIntervalAtt").toUJson("attachedTo").str=="variable")

      // link the params attached to a var ('t' in 't = 5 (days)') to the variable of the definition mention ('t' in 't is time')
      if (throughVar.nonEmpty) {
        val varNameAlignments = alignmentHandler.editDistance.alignTexts(textDefinitionMentions.get.map(Aligner.getRelevantText(_, Set("variable"))).map(_.toLowerCase), throughVar.map(Aligner.getRelevantText(_, Set("variable"))).map(_.toLowerCase()))
        // group by src idx, and keep only top k (src, dst, score) for each src idx, here k = 1
        alignments(TEXT_VAR_TO_INT_PARAM_SETTING) = Aligner.topKBySrc(varNameAlignments, 1)
      }

      // link the params attached to a concept ('time' in 'time is set to 5 days') to the definition of the definition mention ('time' in 't is time')
      if (throughConcept.nonEmpty) {
        val varNameAlignments = alignmentHandler.editDistance.alignTexts(textDefinitionMentions.get.map(Aligner.getRelevantText(_, Set("definition"))).map(_.toLowerCase), throughConcept.map(Aligner.getRelevantText(_, Set("variable"))).map(_.toLowerCase()))
        // group by src idx, and keep only top k (src, dst, score) for each src idx, here k = 1
        alignments(TEXT_TO_INT_PARAM_SETTING) = Aligner.topKBySrc(varNameAlignments, 1)
      }

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


  def makeLocationObj(mention: Mention, givenPage: Option[Int], givenBlock: Option[Int]): ujson.Obj = {
      val (page, block) = if (givenPage.isEmpty & givenBlock.isEmpty) {
        if (mention.attachments.exists(_.asInstanceOf[AutomatesAttachment].toUJson.obj("attType").str == "MentionLocation")) {
          val menAttAsJson = mention.attachments.map(_.asInstanceOf[AutomatesAttachment].toUJson.obj).filter(_ ("attType").str == "MentionLocation").head
          val page = menAttAsJson("pageNum").num.toInt
          val block = menAttAsJson("blockIdx").num.toInt
          (page, block)
        } else {
          (-1000, -1000)
        }
      } else (givenPage.get, givenBlock.get)



    val span = new ArrayBuffer[Value]()
    val attsAsUjson = mention.attachments.map(a => a.asInstanceOf[AutomatesAttachment].toUJson)
    if (attsAsUjson.exists(a => a("attType").str == "DiscontinuousCharOffset")) {
      val discontCharOffsetAtt = returnAttachmentOfAGivenType(mention.attachments, "DiscontinuousCharOffset")
      val charOffsets = discontCharOffsetAtt.toUJson("charOffsets").arr.map(v => (v.arr.head.num.toInt, v.arr.last.num.toInt))

      for (offset <- charOffsets) {
        val oneOffsetObj = ujson.Obj()
        oneOffsetObj("char_begin") = offset._1
        oneOffsetObj("char_end") = offset._2
        span.append(oneOffsetObj)
      }

    } else {
      span.append(
        ujson.Obj(
          "char_begin" -> mention.startOffset,
          "char_end" -> mention.endOffset
        )
      )
    }

    val locationObj = if  (page != -1000 & block != -1000)  {

      ujson.Obj(
        "page" -> page,
        "block" -> block,
        "spans" -> span
      )
    } else {
      ujson.Obj(
        "page" -> ujson.Null,
        "block" -> ujson.Null,
        "spans" -> span
      )
    }
    locationObj
  }


  def makeArgObject(mention: Mention, page: Int, block: Int, argType: String): ujson.Obj = {
    ujson.Obj(
      "name" -> argType,
      "text" -> getMentionText(mention),
      "spans" -> makeLocationObj(mention, Some(page), Some(block))
    )
  }

  def makeIntParamSettingObj(mention: Mention, paramSetAttJson: Value, page: Int, block: Int): ujson.Obj = {
    val lowerBound = paramSetAttJson("inclusiveLower")
    val upperBound = paramSetAttJson("inclusiveUpper")
    val toReturn = ujson.Obj(
      "name" -> "parameter_interval",
      "inclusive_lower" -> lowerBound,
      "inclusive_upper" -> upperBound,
      "lower_bound" -> ujson.Null,
      "upper_bound" -> ujson.Null,

    )

    val spans = new ArrayBuffer[ujson.Value]()
    val menArgs = mention.arguments
    if (menArgs.exists(arg => arg._1 == "valueLeast")) {
      val valLeastMen = menArgs("valueLeast").head
      toReturn("lower_bound") = valLeastMen.text.toDouble
      spans.append(makeLocationObj(valLeastMen, Some(page), Some(block)))

    }
    if (menArgs.exists(arg => arg._1 == "valueMost")) {
      val valMostMen = menArgs("valueMost").head
      toReturn("upper_bound") = valMostMen.text.toDouble
      spans.append(makeLocationObj(valMostMen, Some(page), Some(block)))

    }
    toReturn("spans") = spans
    toReturn
  }

  def getIntParamSetArgObj(mention: Mention): ArrayBuffer[Value] = {
    // NB! this one is different from getArgObj because it needs to put two args into one param interval obj; the others can just be done iterating through args

    val (page, block) = if (mention.attachments.exists(_.asInstanceOf[AutomatesAttachment].toUJson.obj("attType").str == "MentionLocation")) {
      val menAttAsJson = mention.attachments.map(_.asInstanceOf[AutomatesAttachment].toUJson.obj).filter(_ ("attType").str == "MentionLocation").head //head.asInstanceOf[MentionLocationAttachment].toUJson.obj
      val page = menAttAsJson("pageNum").num.toInt
      val block = menAttAsJson("blockIdx").num.toInt
      (page, block)
    } else {
      (-1000, -1000)
    }


    val argObjs = new ArrayBuffer[Value]()

    val paramSetAttJson = returnAttachmentOfAGivenType(mention.attachments, "ParamSettingIntervalAtt").toUJson
    val attTo = paramSetAttJson("attachedTo")
    val varMen = mention.arguments("variable").head


    val varObj = if (attTo.str == "variable") {
      makeArgObject(varMen, page, block, "identifier")
    } else {
      makeArgObject(varMen, page, block, "definition")
    }
    argObjs.append(varObj)

    val paramSettingObj = makeIntParamSettingObj(mention, paramSetAttJson, page, block)
    argObjs.append(paramSettingObj)
    argObjs
  }

  def getArgObj(mention: Mention): ArrayBuffer[Value] = {

    val (page, block) = if (mention.attachments.exists(_.asInstanceOf[AutomatesAttachment].toUJson.obj("attType").str == "MentionLocation")) {
      val menAttAsJson = mention.attachments.map(_.asInstanceOf[AutomatesAttachment].toUJson.obj).filter(_ ("attType").str == "MentionLocation").head //head.asInstanceOf[MentionLocationAttachment].toUJson.obj
      val page = menAttAsJson("pageNum").num.toInt
      val block = menAttAsJson("blockIdx").num.toInt
      (page, block)
    } else {
      (-1000, -1000)
    }

    val attTo = mention.label match {
      case "ParameterSetting" => {
        val paramSetAttJson = returnAttachmentOfAGivenType(mention.attachments, "ParamSetAtt").toUJson
        paramSetAttJson("attachedTo").str
      }
      case "UnitRelation" => {
        val unitAttJson = returnAttachmentOfAGivenType(mention.attachments, "UnitAtt").toUJson
        unitAttJson("attachedTo").str
      }
      case _ => "variable"
    }

    val argObjs = new ArrayBuffer[Value]()
    val varMen = mention.arguments("variable").head


    val varObj = if (attTo == "concept") {
      makeArgObject(varMen, page, block, "definition") // aka concept
    } else {
      makeArgObject(varMen, page, block, "identifier")
    }

    argObjs.append(varObj)

    val theOtherArgObj = mention.label match {
      case "ParameterSetting" => {
        makeArgObject(mention.arguments("value").head, page, block, "parameter_setting")
      }
      case "UnitRelation" => {
        makeArgObject(mention.arguments("unit").head, page, block, "unit")
      }
      case "Definition" | "ConjDefinition" => {
        makeArgObject(mention.arguments("definition").head, page, block, "definition")
      }
      case _ => ???
    }
    argObjs.append(theOtherArgObj)
    argObjs
  }

  def mentionToIDedObjString(mention: Mention, mentionType: String): String = {
    // creates an id'ed object for each mention
    val docId = mention.document.id.getOrElse("unk_text_file")
    val originalSentence = mention.sentenceObj.words.mkString(" ")
    val offsets = mention.tokenInterval.toString()
    val args = mentionType match {
      case INT_PARAM_SETTING_THRU_VAR | INT_PARAM_SETTING_THRU_CONCEPT => getIntParamSetArgObj(mention)
      case PARAM_SETTING_THRU_VAR | PARAM_SETTING_THRU_CONCEPT | UNIT_THRU_VAR | UNIT_THRU_CONCEPT | TEXT_VAR =>  getArgObj(mention)
      case _ => ???
    }

    val jsonObj = ujson.Obj(
      "uid" -> randomUUID.toString(),
      "source" -> docId,
      "original_sentence" -> originalSentence,
      "content" -> mention.text,
      "spans" -> makeLocationObj(mention, None, None),
      "arguments" -> ujson.Arr(args)

    )

    jsonObj.toString()
  }

  def getLinkElements(
    grfn: Value,
    textDefinitionMentions:
    Option[Seq[Mention]],
    commentDefinitionMentions: Option[Seq[Mention]],
    equationChunksAndSource: Option[Seq[(String, String)]],
    variableNames: Option[Seq[String]],
    parameterSettingMentions: Option[Seq[Mention]],
    intervalParameterSettingMentions: Option[Seq[Mention]],
    unitRelationMentions: Option[Seq[Mention]]
  ): mutable.HashMap[String, Seq[String]] = {
    // Make Comment Spans from the comment variable mentions
    val linkElements = scala.collection.mutable.HashMap[String, Seq[String]]()

    if (commentDefinitionMentions.isDefined) {
      linkElements(COMMENT) = commentDefinitionMentions.get.map { commentMention => {
        ujson.Obj(
          "uid" -> randomUUID.toString,
          "source" -> commentMention.document.id.getOrElse("unk_file").toString,
          "content" -> commentMention.text
        ).toString()
        }
      }
    }


    // Repeat for src code variables
    if (variableNames.isDefined) {
      linkElements(SOURCE) = variableNames.get.map { varName =>
        ujson.Obj(
          "uid" -> randomUUID.toString,
          "source" ->  varName.split("::")(1),
          "content" -> varName.split("::")(2)
        ).toString()
      }
    }

    if (textDefinitionMentions.isDefined) {
      linkElements(TEXT_VAR) = textDefinitionMentions.get.map { mention =>
        mentionToIDedObjString(mention, TEXT_VAR)
      }
    }

    if (intervalParameterSettingMentions.isDefined) {
      val (throughVar, throughConcept) = intervalParameterSettingMentions.get.partition(m => returnAttachmentOfAGivenType(m
       .attachments, "ParamSettingIntervalAtt").toUJson("attachedTo").str=="variable")

      if (throughVar.nonEmpty) {
        linkElements(INT_PARAM_SETTING_THRU_VAR) = throughVar.map { mention =>
          mentionToIDedObjString(mention, INT_PARAM_SETTING_THRU_VAR)
        }
      }

      if (throughConcept.nonEmpty) {
        linkElements(INT_PARAM_SETTING_THRU_CONCEPT) = throughVar.map { mention =>
          mentionToIDedObjString(mention, INT_PARAM_SETTING_THRU_CONCEPT)
        }
      }

    }

    if (parameterSettingMentions.isDefined) {

      val (throughVar, throughConcept) = parameterSettingMentions.get.partition(m => returnAttachmentOfAGivenType(m
        .attachments, "ParamSetAtt").toUJson("attachedTo").str=="variable")

      if (throughVar.nonEmpty) {
        linkElements(PARAM_SETTING_THRU_VAR) = throughVar.map { mention =>
          mentionToIDedObjString(mention, PARAM_SETTING_THRU_VAR)

        }
      }

      if (throughConcept.nonEmpty) {
        linkElements(PARAM_SETTING_THRU_CONCEPT) = throughVar.map { mention =>
          mentionToIDedObjString(mention, PARAM_SETTING_THRU_VAR)
        }
      }

    }


    if (unitRelationMentions.isDefined) {

      val (throughVar, throughConcept) = unitRelationMentions.get.partition(m => returnAttachmentOfAGivenType(m
        .attachments, "UnitAtt").toUJson("attachedTo").str=="variable")

      if (throughVar.nonEmpty) {
        linkElements(UNIT_THRU_VAR) = throughVar.map { mention =>
          mentionToIDedObjString(mention, UNIT_THRU_VAR)
        }
      }

      if (throughConcept.nonEmpty) {
        linkElements(UNIT_THRU_CONCEPT) = throughVar.map { mention =>
          mentionToIDedObjString(mention, UNIT_THRU_CONCEPT)
        }
      }
    }

    // Repeat for Eqn Variables
    if (equationChunksAndSource.isDefined) {
      val equation2uuid = mutable.Map[String, UUID]()
      linkElements(EQUATION) = equationChunksAndSource.get.map { case (chunk, orig) =>
        if (equation2uuid.contains(orig)) {
          ujson.Obj(
            "uid" -> randomUUID.toString(),
            "equation_uid" -> equation2uuid(orig).toString(),
            "content" -> AlignmentBaseline.replaceGreekWithWord(chunk, greek2wordDict.toMap)
          ).toString()
        } else {
          val id = randomUUID
          equation2uuid(orig) = id
          ujson.Obj(
            "uid" -> id.toString(),
            "content" -> AlignmentBaseline.replaceGreekWithWord(chunk, greek2wordDict.toMap)
          ).toString()
        }
      }

      linkElements(FULL_TEXT_EQUATION) = equation2uuid.keys.map(key =>
        ujson.Obj(
          "uid" -> equation2uuid(key).toString(),
          "content" -> key
        ).toString()
      ).toSeq
    }

    linkElements
  }

  /* Align definition mentions from two sources; not currently used */
 def getInterModelComparisonLinkElements(
                       defMentions1:
                       Seq[Mention],
                       defMention2: Seq[Mention]
                     ): Map[String, Seq[String]] = {

    val linkElements = scala.collection.mutable.HashMap[String, Seq[String]]()

      linkElements("TEXT_VAR1") = defMentions1.map { mention =>
        val docId = mention.document.id.getOrElse("unk_text_file")
        val sent = mention.sentence
        val originalSentence = mention.sentenceObj.words.mkString(" ")
        val offsets = mention.tokenInterval.toString()
        val textVar = mention.arguments(VARIABLE).head.text
        val definition = mention.arguments(DEFINITION).head.text

        ujson.Obj(
          "uid" -> randomUUID.toString(),
          "source" -> docId,
          "content" -> textVar,
          "definition" -> definition,
          "original_sentence" -> originalSentence
        ).toString()

      }

      linkElements("TEXT_VAR2") = defMention2.map { mention =>
        val docId = mention.document.id.getOrElse("unk_text_file")
        val sent = mention.sentence
        val originalSentence = mention.sentenceObj.words.mkString(" ")
        val offsets = mention.tokenInterval.toString()
        val textVar = mention.arguments(VARIABLE).head.text
        val definition = mention.arguments(DEFINITION).head.text
        ujson.Obj(
          "uid" -> randomUUID.toString(),
          "source" -> docId,
          "content" -> textVar,
          "definition" -> definition,
          "original_sentence" -> originalSentence
        ).toString()
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


  def mkLinkHypothesisTextVarDef(variables: Seq[String], definitions: Seq[String], debug: Boolean): Seq[Obj] = {

    assert(variables.length == definitions.length)
    for {
      i <- variables.indices
    } yield mkHypothesis(variables(i), definitions(i), 1.0, debug)
  }


  def mkLinkHypothesis(srcElements: Seq[String], dstElements: Seq[String], linkType: String, alignments: Seq[Seq[Alignment]], debug: Boolean): Seq[Obj] = {

    for {
      topK <- alignments
      alignment <- topK
      srcLinkElement = srcElements(alignment.src)
      dstLinkElement = dstElements(alignment.dst)
      score = alignment.score
    } yield mkHypothesis(srcLinkElement, dstLinkElement, linkType, score, debug)
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
    // Comment -> Text Var
    if (linkElKeys.contains(COMMENT) && linkElKeys.contains(TEXT_VAR)) {
      hypotheses.appendAll(mkLinkHypothesis(linkElements(COMMENT), linkElements(TEXT_VAR), COMMENT_TO_TEXT, alignments(COMMENT_TO_TEXT), debug))
    }


    // Src Variable -> Comment
    if (linkElKeys.contains(SOURCE) && linkElKeys.contains(COMMENT)) {
      println("has source and comment")
      hypotheses.appendAll(mkLinkHypothesis(linkElements(SOURCE), linkElements(COMMENT), SRC_TO_COMMENT, alignments(SRC_TO_COMMENT), debug))
    }

    // Equation -> Text
    if (linkElKeys.contains(EQUATION) && linkElKeys.contains(TEXT_VAR)) {
      println("has eq and text")
      hypotheses.appendAll(mkLinkHypothesis(linkElements(EQUATION), linkElements(TEXT_VAR), EQN_TO_TEXT, alignments(EQN_TO_TEXT), debug))
    }

    // Comment -> Text Var
    if (linkElKeys.contains(COMMENT) && linkElKeys.contains(TEXT_VAR)) {
      hypotheses.appendAll(mkLinkHypothesis(linkElements(COMMENT), linkElements(TEXT_VAR), COMMENT_TO_TEXT, alignments(COMMENT_TO_TEXT), debug))
    }

    // TextVar to Unit (through var)
    if (linkElKeys.contains(TEXT_VAR) && linkElKeys.contains(UNIT_THRU_VAR)) {
      hypotheses.appendAll(mkLinkHypothesis(linkElements(TEXT_VAR), linkElements(TEXT_VAR), TEXT_VAR_TO_UNIT, alignments(TEXT_VAR_TO_UNIT), debug))
    }

    // TextVar to Unit (through concept)
    if (linkElKeys.contains(TEXT_VAR) && linkElKeys.contains(UNIT_THRU_CONCEPT)) {
      hypotheses.appendAll(mkLinkHypothesis(linkElements(TEXT_VAR), linkElements(TEXT_VAR), TEXT_TO_UNIT, alignments(TEXT_TO_UNIT), debug))
    }


    // TextVar to ParamSetting (through var)
    if (linkElKeys.contains(TEXT_VAR) && linkElKeys.contains(PARAM_SETTING_THRU_VAR)) {
      hypotheses.appendAll(mkLinkHypothesis(linkElements(TEXT_VAR), linkElements(PARAM_SETTING_THRU_VAR), TEXT_VAR_TO_PARAM_SETTING, alignments(TEXT_VAR_TO_PARAM_SETTING), debug))
    }

    // TextVar to ParamSetting (through concept)
    if (linkElKeys.contains(TEXT_VAR) && linkElKeys.contains(PARAM_SETTING_THRU_CONCEPT)) {
      hypotheses.appendAll(mkLinkHypothesis(linkElements(TEXT_VAR), linkElements(PARAM_SETTING_THRU_VAR), TEXT_TO_PARAM_SETTING, alignments(TEXT_TO_PARAM_SETTING), debug))
    }


    // TextVar to IntervalParamSetting (through var)
    if (linkElKeys.contains(TEXT_VAR) && linkElKeys.contains(INT_PARAM_SETTING_THRU_VAR)) {
      hypotheses.appendAll(mkLinkHypothesis(linkElements(TEXT_VAR), linkElements(INT_PARAM_SETTING_THRU_VAR), TEXT_VAR_TO_INT_PARAM_SETTING, alignments(TEXT_VAR_TO_INT_PARAM_SETTING), debug))
    }

    // TextVar to IntervalParamSetting (through concept)
    if (linkElKeys.contains(TEXT_VAR) && linkElKeys.contains(INT_PARAM_SETTING_THRU_CONCEPT)) {
      hypotheses.appendAll(mkLinkHypothesis(linkElements(TEXT_VAR), linkElements(INT_PARAM_SETTING_THRU_CONCEPT), TEXT_TO_INT_PARAM_SETTING, alignments(TEXT_TO_INT_PARAM_SETTING), debug))
    }


    hypotheses
  }


  def getInterPaperLinkHypotheses(linkElements: Map[String, Seq[String]], alignment: Seq[Seq[Alignment]], debug: Boolean): Seq[Obj] = {
    val paper1LinkElements = linkElements("TEXT_VAR1")
    val paper2LinkElements = linkElements("TEXT_VAR2")
    val hypotheses = new ArrayBuffer[ujson.Obj]()
    // fixme: there should be no link type here bc link types are all the same in this task
    hypotheses.appendAll(mkLinkHypothesis(paper1LinkElements, paper2LinkElements, "VAR1_VAR2", alignment, debug))
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
      .filter(m => hasRequiredArgs(m, "definition"))

    val allUsedTextMentions = if (loadMentions) {
      val mentionsFile = new File(config[String]("apps.mentionsFile"))
      (JSONSerializer.toMentions(mentionsFile).filter(_.label matches "Definition"),
        JSONSerializer.toMentions(mentionsFile).filter(_.label matches "ParameterSetting"),
        JSONSerializer.toMentions(mentionsFile).filter(_.label matches "IntervalParameterSetting"),
        JSONSerializer.toMentions(mentionsFile).filter(_.label matches "UnitRelation"))
    } else {
      val inputDir = config[String]("apps.inputDirectory")
      val inputType = config[String]("apps.inputType")
      val dataLoader = DataLoader.selectLoader(inputType) // txt, json (from science parse), pdf supported
      val files = FileUtils.findFiles(inputDir, dataLoader.extension)
      getTextMentions(textReader, dataLoader, textRouter, files)

    }
    val textDefinitionMentions = allUsedTextMentions._1
    val parameterSettingMentions = allUsedTextMentions._2
    val intervalParameterSettingMentions = allUsedTextMentions._3
    val unitMentions = allUsedTextMentions._4

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
      Some(intervalParameterSettingMentions),
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
