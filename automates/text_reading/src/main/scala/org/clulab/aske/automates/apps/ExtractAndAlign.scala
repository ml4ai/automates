package org.clulab.aske.automates.apps

import ai.lum.common.ConfigFactory

import java.io.{File, PrintWriter}
import java.util.UUID
import org.clulab.utils.MentionUtils._
import ai.lum.common.ConfigUtils._
import ai.lum.common.FileUtils._
import com.typesafe.config.Config
import org.clulab.aske.automates.data.{DataLoader, TextRouter, TokenizedLatexDataLoader}
import org.clulab.aske.automates.alignment.{Aligner, Alignment, AlignmentHandler}
import org.clulab.aske.automates.grfn.GrFNParser.mkHypothesis
import org.clulab.aske.automates.OdinEngine
import org.clulab.aske.automates.apps.AlignmentBaseline.{greek2wordDict, word2greekDict}
import org.clulab.aske.automates.grfn.GrFNParser
import org.clulab.odin.{Attachment, Mention}
import org.clulab.utils.{AlignmentJsonUtils, FileUtils}
import org.slf4j.LoggerFactory
import ujson.{Obj, Value}
import org.clulab.grounding.{SVOGrounder, SeqOfWikiGroundings, WikiGrounding, WikidataGrounder, sparqlResult, sparqlWikiResult}
import org.clulab.odin.serialization.json.JSONSerializer

import java.util.UUID.randomUUID
import org.clulab.utils.AlignmentJsonUtils.{GlobalEquationVariable, GlobalSrcVariable, GlobalVariable, getGlobalEqVars, getGlobalSrcVars, getSrcLinkElements, mkGlobalEqVarLinkElement, mkGlobalSrcVarLinkElement, mkGlobalVarLinkElement}
import org.clulab.aske.automates.attachments.AutomatesAttachment
import org.clulab.embeddings.word2vec.Word2Vec
import org.clulab.grounding.SVOGrounder.getTerms
import upickle.default.write

import scala.collection.mutable
import scala.collection.mutable.ArrayBuffer
import scala.util.Try

case class AlignmentArguments(json: Value, identifierNames: Option[Seq[String]], identifierShortNames: Option[Seq[String]], commentDescriptionMentions: Option[Seq[Mention]], descriptionMentions: Option[Seq[Mention]], parameterSettingMentions: Option[Seq[Mention]], intervalParameterSettingMentions: Option[Seq[Mention]], unitMentions: Option[Seq[Mention]], equationChunksAndSource: Option[Seq[(String, String)]], svoGroundings: Option[ArrayBuffer[(String, Seq[sparqlResult])]], wikigroundings: Option[Map[String, Seq[sparqlWikiResult]]])

object ExtractAndAlign {


  // Link element types
  val COMMENT = "comment"
  val GLOBAL_COMMENT = "gl_comm"
  val TEXT_VAR = "text_var" // stores information about each variable, e.g., identifier, associated description, arguments, and when available location in the original document (e.g., in the pdf)
  val GLOBAL_VAR = "gvar" // stores ids of text variables that are likely different instances of the same global variable
  val GLOBAL_EQ_VAR = "gl_eq_var"
  val SOURCE = "src" // identifiers found in source code
  val GLOBAL_SRC_VAR = "gl_src_var"
  val EQUATION = "equation" // an equation extracted from the original document
  val SVO_GROUNDING = "SVOgrounding"
  // Below, "via concept" means the arg in question is attached to a variable concept,
  // e.g., temperature is measured in celsius, while "via identifier" means the arg is attached to an identifier, e.g., T is measured in celsius.
  val INT_PARAM_SETTING_VIA_CNCPT = "int_param_setting_via_cncpt"
  val INT_PARAM_SETTING_VIA_IDFR = "int_param_setting_via_idfr"
  val PARAM_SETTING_VIA_CNCPT = "parameter_setting_via_cncpt"
  val PARAM_SETTING_VIA_IDFR = "parameter_setting_via_idfr"
  val UNIT_VIA_CNCPT = "unit_via_cncpt"
  val UNIT_VIA_IDFR = "unit_via_idfr"
  val FULL_TEXT_EQUATION = "full_text_equation"

  // Relations between links
  val SRC_TO_COMMENT = "source_to_comment"
  val GLOBAL_VAR_TO_UNIT_VIA_IDENTIFIER = "gvar_to_unit_via_idfr"
  val GLOBAL_VAR_TO_UNIT_VIA_CONCEPT = "gvar_to_unit_via_cpcpt"
  val GLOBAL_VAR_TO_PARAM_SETTING_VIA_IDENTIFIER = "gvar_to_param_setting_via_idfr"
  val GLOBAL_VAR_TO_PARAM_SETTING_VIA_CONCEPT = "gvar_to_param_setting_via_cpcpt"
  val GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_IDENTIFIER = "gvar_to_interval_param_setting_via_idfr"
  val GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_CONCEPT = "gvar_to_interval_param_setting_via_cpcpt"

  val EQN_TO_GLOBAL_VAR = "equation_to_gvar"
  val COMMENT_TO_GLOBAL_VAR = "comment_to_gvar"
  val GLOBAL_VAR_TO_SVO = "gvar_to_svo"

  // These are temporary thresholds - to be set
  val allLinkTypes = ujson.Obj("direct" -> ujson.Obj(
    GLOBAL_VAR_TO_UNIT_VIA_IDENTIFIER -> 1.0,
    GLOBAL_VAR_TO_UNIT_VIA_CONCEPT -> 1.8,
    GLOBAL_VAR_TO_PARAM_SETTING_VIA_IDENTIFIER -> 1.0,
    GLOBAL_VAR_TO_PARAM_SETTING_VIA_CONCEPT -> 1.8,
    GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_IDENTIFIER -> 1.0,
    GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_CONCEPT -> 1.8,
    EQN_TO_GLOBAL_VAR -> 0.5,
    COMMENT_TO_GLOBAL_VAR -> 0.5),
    "indirect" -> ujson.Obj(
      SRC_TO_COMMENT -> 0.5
    ),
    "disabled" -> ujson.Obj(
      GLOBAL_VAR_TO_SVO -> 0.5)
  )

  val whereIsGlobalVar = Map[String, String](
    GLOBAL_VAR_TO_UNIT_VIA_IDENTIFIER -> "element_1",
    GLOBAL_VAR_TO_UNIT_VIA_CONCEPT -> "element_1",
    GLOBAL_VAR_TO_PARAM_SETTING_VIA_IDENTIFIER -> "element_1",
    GLOBAL_VAR_TO_PARAM_SETTING_VIA_CONCEPT -> "element_1",
    GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_IDENTIFIER -> "element_1",
    GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_CONCEPT -> "element_1",
    EQN_TO_GLOBAL_VAR -> "element_2",
    COMMENT_TO_GLOBAL_VAR -> "element_2",
    GLOBAL_VAR_TO_SVO -> "element_1"
  )

  val whereIsNotGlobalVar = Map[String, String](
    GLOBAL_VAR_TO_UNIT_VIA_IDENTIFIER -> "element_2",
    GLOBAL_VAR_TO_UNIT_VIA_CONCEPT -> "element_2",
    GLOBAL_VAR_TO_PARAM_SETTING_VIA_IDENTIFIER -> "element_2",
    GLOBAL_VAR_TO_PARAM_SETTING_VIA_CONCEPT -> "element_2",
    GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_IDENTIFIER -> "element_2",
    GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_CONCEPT -> "element_2",
    EQN_TO_GLOBAL_VAR -> "element_1",
    COMMENT_TO_GLOBAL_VAR -> "element_1",
    GLOBAL_VAR_TO_SVO -> "element_2"
  )

  // labels and argument names
  val DESCRIPTION = "description"
  val VARIABLE = "variable"
  val DESCR_LABEL = "Description"
  val CONJUNCTION_DESCR_LABEL = "ConjDescription"
  val CONJUNCTION_DESCR_TYPE_2_LABEL = "ConjDescriptionType2"
  val PARAMETER_SETTING_LABEL = "ParameterSetting"
  val INTERVAL_PARAMETER_SETTING_LABEL = "IntervalParameterSetting"
  val UNIT_LABEL = "Unit"
  val UNIT_RELATION_LABEL = "UnitRelation"

  val logger = LoggerFactory.getLogger(this.getClass())


  val config: Config = ConfigFactory.load()
  val pdfAlignDir: String = config[String]("apps.pdfalignDir")
  val numOfWikiGroundings: Int = config[Int]("apps.numOfWikiGroundings")
  val vectors: String = config[String]("alignment.w2vPath")
  val w2v = new Word2Vec(vectors, None)

  def parseDouble(s: String): Option[Double] = Try { s.toDouble }.toOption

  def groundMentions(
                      grfn: Value,
                      variableNames: Option[Seq[String]],
                      variableShortNames: Option[Seq[String]],
                      descriptionMentions: Option[Seq[Mention]],
                      parameterSettingMention: Option[Seq[Mention]],
                      intervalParameterSettingMentions: Option[Seq[Mention]],
                      unitMentions: Option[Seq[Mention]],
                      commentDescriptionMentions: Option[Seq[Mention]],
                      equationChunksAndSource: Option[Seq[(String, String)]],
                      SVOgroundings: Option[ArrayBuffer[(String, Seq[sparqlResult])]],
                      wikigroundings: Option[Map[String, Seq[sparqlWikiResult]]],
                      groundToSVO: Boolean,
                      groundToWiki: Boolean,
                      saveWikiGroundings: Boolean,
                      maxSVOgroundingsPerVar: Int,
                      alignmentHandler: AlignmentHandler,
                      numAlignments: Option[Int],
                      numAlignmentsSrcToComment: Option[Int],
                      scoreThreshold: Double = 0.0,
                      appendToGrFN: Boolean,
                      debug: Boolean

    ): Value = {

    // get all global variables before aligning
    val allGlobalVars = if (descriptionMentions.nonEmpty) {
      getGlobalVars(descriptionMentions.get, wikigroundings, groundToWiki)
    } else Seq.empty

    if (saveWikiGroundings) {
      val groundings = SeqOfWikiGroundings(allGlobalVars.map(gv => WikiGrounding(gv.identifier, gv.groundings.getOrElse(Seq.empty))))
      val asString = write(groundings, indent = 4)
      val exporter = JSONDocExporter()
      val fileName = if (descriptionMentions.isDefined && descriptionMentions.get.nonEmpty) descriptionMentions.get.head.document.id.getOrElse("unknown_document") else "unknown_document"
      exporter.export(asString, fileName.replace(".json", "").concat("-wikidata-groundings"))
    }



    // keep for debugging align
//    for (g <- allGlobalVars) println("gv: " + g.identifier + "\n------\n" + g.textFromAllDescrs.mkString("\n") +
//      "\n=========\n")


    // todo: have a separate method for gl comment vars with no grounding and no location on the page
    val allCommentGlobalVars = if (commentDescriptionMentions.nonEmpty) {
      getGlobalVars(commentDescriptionMentions.get, wikigroundings, false)
    } else Seq.empty

    // keep for debugging align
//    for (g <- allCommentGlobalVars) println("comment gv: " + g.identifier + "\n------\n" + g.textFromAllDescrs.mkString("\n") +
//      "\n=========\n")

    val (eqLinkElements, fullEquations) = if (equationChunksAndSource.nonEmpty) getEquationLinkElements(equationChunksAndSource.get) else (Seq.empty, Seq.empty)
    val globalEqVariables = if (eqLinkElements.nonEmpty) getGlobalEqVars(eqLinkElements) else Seq.empty
    val srcLinkElements = if (variableNames.nonEmpty) getSrcLinkElements(variableNames.get) else Seq.empty
    val globalSrcVars = if (srcLinkElements.nonEmpty) getGlobalSrcVars(srcLinkElements) else Seq.empty

    // =============================================
    // Alignment
    // =============================================

    val alignments = alignElements(
      alignmentHandler,
      allGlobalVars,
      parameterSettingMention,
      intervalParameterSettingMentions,
      unitMentions,
      globalEqVariables,
      allCommentGlobalVars,
      globalSrcVars,
      SVOgroundings,
      numAlignments,
      numAlignmentsSrcToComment,
      scoreThreshold
    )

    var outputJson = ujson.Obj()

    val linkElements = getLinkElements(grfn, allGlobalVars, allCommentGlobalVars, equationChunksAndSource, variableNames, parameterSettingMention, intervalParameterSettingMentions,  unitMentions)

    linkElements(SOURCE) = srcLinkElements.map(_.toString())
    linkElements(GLOBAL_SRC_VAR) = globalSrcVars.map(glv => mkGlobalSrcVarLinkElement(glv))
    linkElements(FULL_TEXT_EQUATION) = fullEquations
    linkElements(EQUATION) = eqLinkElements.map(_.toString())
    linkElements(GLOBAL_EQ_VAR) = globalEqVariables.map(glv => mkGlobalEqVarLinkElement(glv))

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

  def getGlobalVars(descrMentions: Seq[Mention], wikigroundings: Option[Map[String, Seq[sparqlWikiResult]]], groundToWiki: Boolean): Seq[GlobalVariable] = {

    val groupedVars = descrMentions.groupBy(_.arguments("variable").head.text.replace(".", ""))
    val allGlobalVars = new ArrayBuffer[GlobalVariable]()
    for (gr <- groupedVars) {
      val glVarID = randomUUID().toString()
      val identifier = gr._1//AlignmentBaseline.replaceWordWithGreek(gr._1, AlignmentBaseline.word2greekDict.toMap); for now, don't convert: text vars are already symbols and comments shouldnt be converted except for during alignment
      val identifierComponents = if (identifier.contains("_")) {
        val splitIdentifier = identifier.split("_")
        if (!splitIdentifier.map(_.length).contains(1)) {
          splitIdentifier.filter(_.length > 1).toSeq
        } else Seq.empty
      } else Seq.empty
//      println("IDENTIFIER: " + identifier)

      val textVarObjs = gr._2.map(m => mentionToIDedObjString(m, TEXT_VAR))
      val textFromAllDescrs = gr._2.map(m => getMentionText(m.arguments("description").head)).distinct ++ identifierComponents
      val terms = gr._2.flatMap(g => getTerms(g)).distinct
      val groundings = if (groundToWiki) {
        // if there are no existing wikigroundings, ground
        if (!wikigroundings.isDefined || wikigroundings.get.isEmpty) {
          WikidataGrounder.groundTermsToWikidataRanked(identifier, terms.flatten, textFromAllDescrs, w2v, numOfWikiGroundings)
        } else {
          // if there are previously extracted groundings, find grounding for the identifier
          if (wikigroundings.get.contains(identifier)) {
            Some(wikigroundings.get(identifier))
          } else {
            None
          }
        }
      } else None
      val glVar = GlobalVariable(glVarID, identifier, textVarObjs, textFromAllDescrs, groundings)
      allGlobalVars.append(glVar)
    }
    allGlobalVars
  }

  def updateTextVariable(textVarLinkElementString: String, update: String): String = {
    textVarLinkElementString + "::" + update

  }

  def updateTextVariable(textVarLinkElementString: String, update: Object): String = {
    val updateString = update.toString()
    textVarLinkElementString + "::" + updateString

  }

  def updateTextVarsWithUnits(textVarLinkElements: Seq[String], unitMentions: Option[Seq[Mention]], textToUnitThroughDescrAlignments: Seq[Seq[Alignment]], textToUnitAlignments: Seq[Seq[Alignment]]): Seq[String] = {


    val updatedTextVars = if (textToUnitThroughDescrAlignments.nonEmpty) {

      for {
        topK <- textToUnitThroughDescrAlignments
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
    (onlyEventsAndRelations.filter(_ matches DESCR_LABEL), onlyEventsAndRelations.filter(_ matches PARAMETER_SETTING_LABEL), onlyEventsAndRelations.filter(_ matches INTERVAL_PARAMETER_SETTING_LABEL), onlyEventsAndRelations.filter(_ matches UNIT_LABEL)) // fixme: should this be UNIT_RELATION_LABEL?
  }

  def getCommentDescriptionMentions(commentReader: OdinEngine, alignmentInputFile: Value, variableShortNames: Option[Seq[String]], source: Option[String]): Seq[Mention] = {
    val commentDocs = if (alignmentInputFile.obj.get("source_code").isDefined) {
      AlignmentJsonUtils.getCommentDocs(alignmentInputFile, source)
    } else GrFNParser.getCommentDocs(alignmentInputFile)

    // Iterate through the docs and find the mentions; eliminate duplicates
    val commentMentions = commentDocs.flatMap(doc => commentReader.extractFrom(doc)).distinct

    val descriptions = commentMentions.seq.filter(_ matches DESCR_LABEL)

    if (variableShortNames.isEmpty) return descriptions
    val overlapsWithVariables = descriptions.filter(
      m => variableShortNames.get
        .map(string => string.toLowerCase)
        .contains(m.arguments(VARIABLE).head.text.toLowerCase)
    )
    overlapsWithVariables
  }


  def returnAttachmentOfAGivenType(atts: Set[Attachment], attType: String): AutomatesAttachment = {
    atts.map(att => att.asInstanceOf[AutomatesAttachment]).filter(aa => aa.toUJson("attType").str ==attType).head
  }

  def returnAttachmentOfAGivenTypeOption(atts: Set[Attachment], attType: String): Option[AutomatesAttachment] = {
    val ofType = atts.map(att => att.asInstanceOf[AutomatesAttachment]).filter(aa => aa.toUJson("attType").str ==attType)
    ofType.headOption
  }

  def alignElements(
    alignmentHandler: AlignmentHandler,
    allGlobalVars: Seq[GlobalVariable],
    parameterSettingMentions: Option[Seq[Mention]],
    intParameterSettingMentions: Option[Seq[Mention]],
    unitMentions: Option[Seq[Mention]],
    globalEqVariables: Seq[GlobalEquationVariable],
    allCommentGlobalVars: Seq[GlobalVariable],
    globalSrcVars: Seq[GlobalSrcVariable],
    SVOgroundings: Option[ArrayBuffer[(String, Seq[sparqlResult])]],
    numAlignments: Option[Int],
    numAlignmentsSrcToComment: Option[Int],
    scoreThreshold: Double): Map[String, Seq[Seq[Alignment]]] = {


    val alignments = scala.collection.mutable.HashMap[String, Seq[Seq[Alignment]]]()

    if (allCommentGlobalVars.nonEmpty && globalSrcVars.nonEmpty) {
      val varNameAlignments = alignmentHandler.editDistance.alignTexts(globalSrcVars.map(_.identifier.toLowerCase), allCommentGlobalVars.map(_.identifier).map(_.toLowerCase()))
      // group by src idx, and keep only top k (src, dst, score) for each src idx, here k = 1
      alignments(SRC_TO_COMMENT) = Aligner.topKBySrc(varNameAlignments, numAlignmentsSrcToComment.get)
    }

    /** Align text description to unit variable
      * this should take care of unit relations like this: The density of water is taken as 1.0 Mg m-3.
      */
    if (allGlobalVars.nonEmpty && unitMentions.isDefined) {

      val (throughVar, throughConcept) = unitMentions.get.partition(m => returnAttachmentOfAGivenType(m.attachments, "UnitAtt").toUJson("attachedTo").str=="variable")

      // link the units attached to a var ('t' in 't is measured in days') to the variable of the description mention ('t' in 't is time')
      if (throughVar.nonEmpty) {
        val varNameAlignments = alignmentHandler.editDistance.alignTexts(allGlobalVars.map(_.identifier).map(_.toLowerCase), throughVar.map(Aligner.getRelevantText(_, Set("variable"))).map(_.toLowerCase()))
        // group by src idx, and keep only top k (src, dst, score) for each src idx, here k = 1
        alignments(GLOBAL_VAR_TO_UNIT_VIA_IDENTIFIER) = Aligner.topKBySrc(varNameAlignments, numAlignments.get, allLinkTypes("direct").obj(GLOBAL_VAR_TO_UNIT_VIA_IDENTIFIER).num)
      }
      // link the params attached to a concept ('time' in 'time is measured in days') to the description of the description mention ('time' in 't is time'); note: the name of the argument of interest is "variable"
      if (throughConcept.nonEmpty) {
        val varNameAlignments = alignmentHandler.w2v.alignTexts(allGlobalVars.map(_.textFromAllDescrs.mkString(" ")).map(_.toLowerCase), throughConcept.map(Aligner.getRelevantText(_, Set("variable"))).map(_.toLowerCase()), useBigrams = true)
        // group by src idx, and keep only top k (src, dst, score) for each src idx, here k = 1
        alignments(GLOBAL_VAR_TO_UNIT_VIA_CONCEPT) = Aligner.topKBySrc(varNameAlignments, numAlignments.get, allLinkTypes("direct").obj(GLOBAL_VAR_TO_UNIT_VIA_CONCEPT).num)
      }
    }

    /** Align text variable to SVO groundings
      */
    if (allGlobalVars.nonEmpty && SVOgroundings.isDefined) {
      val varNameAlignments = alignmentHandler.editDistance.alignTexts(allGlobalVars.map(_.identifier).map(_.toLowerCase), SVOgroundings.get.map(_._1.toLowerCase))

      // group by src idx, and keep only top k (src, dst, score) for each src idx, here k = 1
      alignments(GLOBAL_VAR_TO_SVO) = Aligner.topKBySrc(varNameAlignments, 1)
    }


    /** Align text variable to param setting
      */
    if (allGlobalVars.nonEmpty && parameterSettingMentions.isDefined) {
      val (throughVar, throughConcept) = parameterSettingMentions.get.partition(m => returnAttachmentOfAGivenType(m.attachments, "ParamSetAtt").toUJson("attachedTo").str=="variable")

      // link the params attached to a var ('t' in 't = 5 (days)') to the variable of the description mention ('t' in 't is time')
      if (throughVar.nonEmpty) {
        val varNameAlignments = alignmentHandler.editDistance.alignTexts(allGlobalVars.map(_.identifier).map(_.toLowerCase), throughVar.map(Aligner.getRelevantText(_, Set("variable"))).map(_.toLowerCase()))
        // group by src idx, and keep only top k (src, dst, score) for each src idx, here k = 1
        alignments(GLOBAL_VAR_TO_PARAM_SETTING_VIA_IDENTIFIER) = Aligner.topKBySrc(varNameAlignments, numAlignments.get, allLinkTypes("direct").obj(GLOBAL_VAR_TO_PARAM_SETTING_VIA_IDENTIFIER).num)
      }

      // link the params attached to a concept ('time' in 'time is set to 5 days') to the description of the description mention ('time' in 't is time'); note: the name of the argument of interest is "variable"
      if (throughConcept.nonEmpty) {
        val varNameAlignments = alignmentHandler.w2v.alignTexts(allGlobalVars.map(_.textFromAllDescrs.mkString(" ")).map(_.toLowerCase), throughConcept.map(Aligner.getRelevantText(_, Set("variable"))).map(_.toLowerCase()), useBigrams = false)
        // group by src idx, and keep only top k (src, dst, score) for each src idx, here k = 1
        alignments(GLOBAL_VAR_TO_PARAM_SETTING_VIA_CONCEPT) = Aligner.topKBySrc(varNameAlignments, numAlignments.get, allLinkTypes("direct").obj(GLOBAL_VAR_TO_PARAM_SETTING_VIA_CONCEPT).num)
      }

    }


    /** Align text variable to param setting interval
      */
    if (allGlobalVars.nonEmpty && intParameterSettingMentions.isDefined) {
      val (throughVar, throughConcept) = intParameterSettingMentions.get.partition(m => returnAttachmentOfAGivenType(m.attachments, "ParamSettingIntervalAtt").toUJson("attachedTo").str=="variable")

      // link the params attached to a var ('t' in 't = 5 (days)') to the variable of the description mention ('t' in 't is time')
      if (throughVar.nonEmpty) {
        val varNameAlignments = alignmentHandler.editDistance.alignTexts(allGlobalVars.map(_.identifier).map(_.toLowerCase), throughVar.map(Aligner.getRelevantText(_, Set("variable"))).map(_.toLowerCase()))
        // group by src idx, and keep only top k (src, dst, score) for each src idx, here k = 1
        alignments(GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_IDENTIFIER) = Aligner.topKBySrc(varNameAlignments, numAlignments.get, allLinkTypes("direct").obj(GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_IDENTIFIER).num)
      }

      // link the params attached to a concept ('time' in 'time is set to 5 days') to the description of the description mention ('time' in 't is time'); note: the name of the argument of interest is "variable"
      if (throughConcept.nonEmpty) {
        val varNameAlignments = alignmentHandler.w2v.alignTexts(allGlobalVars.map(_.textFromAllDescrs.mkString(" ")).map(_.toLowerCase), throughConcept.map(Aligner.getRelevantText(_, Set("variable"))).map(_.toLowerCase()), useBigrams = true)
        // group by src idx, and keep only top k (src, dst, score) for each src idx, here k = 1
        alignments(GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_CONCEPT) = Aligner.topKBySrc(varNameAlignments, numAlignments.get, allLinkTypes("direct").obj(GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_CONCEPT).num)
      }

    }



    /** Align the equation chunks to the text descriptions */
      if (allGlobalVars.nonEmpty && globalEqVariables.nonEmpty) {
        val equationToTextAlignments = alignmentHandler.editDistance.alignEqAndTexts(globalEqVariables.map(_.identifier), allGlobalVars.map(_.identifier))
        // group by src idx, and keep only top k (src, dst, score) for each src idx
        alignments(EQN_TO_GLOBAL_VAR) = Aligner.topKByDst(equationToTextAlignments, numAlignments.get)

      }

    /** Align the comment descriptions to the text descriptions */
    if (allGlobalVars.nonEmpty && allCommentGlobalVars.nonEmpty) {
      val commentToTextAlignments = alignmentHandler.w2v.alignGlobalCommentVarAndGlobalVars(allCommentGlobalVars, allGlobalVars)
      // group by src idx, and keep only top k (src, dst, score) for each src idx

      val aligns = Aligner.topKBySrc(commentToTextAlignments, numAlignments.get, scoreThreshold, debug = false)
      alignments(COMMENT_TO_GLOBAL_VAR) = aligns
    }

    alignments.toMap
  }


  def makeLocationObj(mention: Mention, givenPage: Option[Seq[Int]], givenBlock: Option[Seq[Int]]): ujson.Obj = {
      val (page, block) = if (givenPage.isEmpty & givenBlock.isEmpty) {
        if (mention.attachments.exists(_.asInstanceOf[AutomatesAttachment].toUJson.obj("attType").str == "MentionLocation")) {
          val menAttAsJson = mention.attachments.map(_.asInstanceOf[AutomatesAttachment].toUJson.obj).filter(_ ("attType").str == "MentionLocation").head
          val page = menAttAsJson("pageNum").arr.map(_.num.toInt)
          val block = menAttAsJson("blockIdx").arr.map(_.num.toInt)
          (page, block)
        } else {
          (Seq(-1000), Seq(-1000))
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


  def makeArgObject(mention: Mention, page: Seq[Int], block: Seq[Int], argType: String): ujson.Obj = {
    ujson.Obj(
      "name" -> argType,
      "text" -> getMentionText(mention),
      "spans" -> makeLocationObj(mention, Some(page), Some(block))
    )
  }

  def makeIntParamSettingObj(mention: Mention, paramSetAttJson: Value, page: Seq[Int], block: Seq[Int]): ujson.Obj = {
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
      if (parseDouble(valMostMen.text).isDefined) {
        toReturn("upper_bound") =  valMostMen.text.toDouble
      } else {
        toReturn("upper_bound") =  valMostMen.text
      }
      spans.append(makeLocationObj(valMostMen, Some(page), Some(block)))
    }
    toReturn("spans") = spans
    toReturn
  }

  def getIntParamSetArgObj(mention: Mention): ArrayBuffer[Value] = {
    // NB! this one is different from getArgObj because it needs to put two args into one param interval obj; the others can just be done iterating through args

    val (page, block) = if (mention.attachments.exists(_.asInstanceOf[AutomatesAttachment].toUJson.obj("attType").str == "MentionLocation")) {
      val menAttAsJson = mention.attachments.map(_.asInstanceOf[AutomatesAttachment].toUJson.obj).filter(_ ("attType").str == "MentionLocation").head //head.asInstanceOf[MentionLocationAttachment].toUJson.obj
      val page = menAttAsJson("pageNum").arr.map(_.num.toInt)
      val block = menAttAsJson("blockIdx").arr.map(_.num.toInt)
      (page, block)
    } else {
      (Seq(-1000), Seq(-1000))
    }


    val argObjs = new ArrayBuffer[Value]()

    val paramSetAttJson = returnAttachmentOfAGivenType(mention.attachments, "ParamSettingIntervalAtt").toUJson
    val attTo = paramSetAttJson("attachedTo")
    val varMen = mention.arguments("variable").head


    val varObj = if (attTo.str == "variable") {
      makeArgObject(varMen, page, block, "identifier")
    } else {
      makeArgObject(varMen, page, block, "description")
    }
    argObjs.append(varObj)

    val paramSettingObj = makeIntParamSettingObj(mention, paramSetAttJson, page, block)
    argObjs.append(paramSettingObj)
    argObjs
  }

  def getArgObj(mention: Mention): ArrayBuffer[Value] = {

    val (page, block) = if (mention.attachments.exists(_.asInstanceOf[AutomatesAttachment].toUJson.obj("attType").str == "MentionLocation")) {
      val menAttAsJson = mention.attachments.map(_.asInstanceOf[AutomatesAttachment].toUJson.obj).filter(_ ("attType").str == "MentionLocation").head //head.asInstanceOf[MentionLocationAttachment].toUJson.obj
      val page = menAttAsJson("pageNum").arr.map(_.num.toInt).toArray
      val block = menAttAsJson("blockIdx").arr.map(_.num.toInt).toArray
      (page, block)
    } else {
      (Array(-1000), Array(-1000))
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
      makeArgObject(varMen, page, block, "description") // aka concept
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
      case "Description" | "ConjDescription" | "ConjDescriptionType2" => {
        makeArgObject(mention.arguments("description").head, page, block, "description")
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
      case INT_PARAM_SETTING_VIA_IDFR | INT_PARAM_SETTING_VIA_CNCPT => getIntParamSetArgObj(mention)
      case PARAM_SETTING_VIA_IDFR | PARAM_SETTING_VIA_CNCPT | UNIT_VIA_IDFR | UNIT_VIA_CNCPT | TEXT_VAR =>  getArgObj(mention)
      case _ => ???
    }

    val whichArgs: Seq[String] = mention.label match {
      case UNIT_RELATION_LABEL => Seq("unit")
      case PARAMETER_SETTING_LABEL => Seq("value")
      case INTERVAL_PARAMETER_SETTING_LABEL => Seq("valueLeast", "valueMost")
      case DESCR_LABEL | CONJUNCTION_DESCR_LABEL | CONJUNCTION_DESCR_TYPE_2_LABEL => Seq.empty
      case _ => throw new NotImplementedError(s"mention label handling not implemented: ${mention.label}")
    }

    val content = if (whichArgs.nonEmpty) mention.arguments.filter(arg => whichArgs.contains(arg._1)).map(arg => arg._2.head.text).mkString("||") else mention.text
    val jsonObj = ujson.Obj(
      "uid" -> randomUUID.toString(),
      "source" -> docId,
      "original_sentence" -> originalSentence,
      "content" -> content,
      "spans" -> makeLocationObj(mention, None, None),
      "arguments" -> ujson.Arr(args)

    )

    jsonObj.toString()
  }

  def getLinkElements(
    grfn: Value,
    allGlobalVars:
    Seq[GlobalVariable],
    allCommentGlobalVars: Seq[GlobalVariable],
    equationChunksAndSource: Option[Seq[(String, String)]],
    variableNames: Option[Seq[String]],
    parameterSettingMentions: Option[Seq[Mention]],
    intervalParameterSettingMentions: Option[Seq[Mention]],
    unitRelationMentions: Option[Seq[Mention]]
  ): mutable.HashMap[String, Seq[String]] = {
    // Make Comment Spans from the comment variable mentions
    val linkElements = scala.collection.mutable.HashMap[String, Seq[String]]()

    if (allGlobalVars.nonEmpty) {
      linkElements(GLOBAL_VAR) = allGlobalVars.map(glv => mkGlobalVarLinkElement(glv))
      linkElements(TEXT_VAR) = allGlobalVars.flatMap(_.textVarObjStrings)
    }

    if (allCommentGlobalVars.nonEmpty) {
      linkElements(COMMENT) = allCommentGlobalVars.flatMap(_.textVarObjStrings)
      linkElements(GLOBAL_COMMENT) = allCommentGlobalVars.map(glv => mkGlobalVarLinkElement(glv))
      }

    if (intervalParameterSettingMentions.isDefined) {
      val (throughVar, throughConcept) = intervalParameterSettingMentions.get.partition(m => returnAttachmentOfAGivenType(m
       .attachments, "ParamSettingIntervalAtt").toUJson("attachedTo").str=="variable")

      if (throughVar.nonEmpty) {
        linkElements(INT_PARAM_SETTING_VIA_IDFR) = throughVar.map { mention =>
          mentionToIDedObjString(mention, INT_PARAM_SETTING_VIA_IDFR)
        }
      }

      if (throughConcept.nonEmpty) {
        linkElements(INT_PARAM_SETTING_VIA_CNCPT) = throughConcept.map { mention =>
          mentionToIDedObjString(mention, INT_PARAM_SETTING_VIA_CNCPT)
        }
      }
    }

    if (parameterSettingMentions.isDefined) {
      val (throughVar, throughConcept) = parameterSettingMentions.get.partition(m => returnAttachmentOfAGivenType(m
        .attachments, "ParamSetAtt").toUJson("attachedTo").str=="variable")

      if (throughVar.nonEmpty) {
        linkElements(PARAM_SETTING_VIA_IDFR) = throughVar.map { mention =>
          mentionToIDedObjString(mention, PARAM_SETTING_VIA_IDFR)
        }
      }

      if (throughConcept.nonEmpty) {
        linkElements(PARAM_SETTING_VIA_CNCPT) = throughConcept.map { mention =>
          mentionToIDedObjString(mention, PARAM_SETTING_VIA_CNCPT)
        }
      }
    }

    if (unitRelationMentions.isDefined) {

      val (throughVar, throughConcept) = unitRelationMentions.get.partition(m => returnAttachmentOfAGivenType(m
        .attachments, "UnitAtt").toUJson("attachedTo").str=="variable")

      if (throughVar.nonEmpty) {
        linkElements(UNIT_VIA_IDFR) = throughVar.map { mention =>
          mentionToIDedObjString(mention, UNIT_VIA_IDFR)
        }
      }

      if (throughConcept.nonEmpty) {
        linkElements(UNIT_VIA_CNCPT) = throughConcept.map { mention =>
          mentionToIDedObjString(mention, UNIT_VIA_CNCPT)
        }
      }
    }
    linkElements
  }

  def getEquationLinkElements(equationChunksAndSource: Seq[(String, String)]): (Seq[Value], Seq[String]) = {
    // eq link elements are values here bc they will be further manipulated
    // full equations are strings for storage
    val equation2uuid = mutable.Map[String, UUID]()
    val eqLinkElements = equationChunksAndSource.map { case (chunk, orig) =>
      if (equation2uuid.contains(orig)) {
        ujson.Obj(
          "uid" -> randomUUID.toString(),
          "equation_uid" -> equation2uuid(orig).toString(),
          "content" -> chunk//AlignmentBaseline.replaceGreekWithWord(chunk, greek2wordDict.toMap)
        )
      } else {
        // create a random id for full equation if it is not in the equation 2 uuid map...
        val id = randomUUID
        //... and add it to the map
        equation2uuid(orig) = id
        ujson.Obj(
          // create a new id for the equation chunk (corresponds to one identifier)
          "uid" -> randomUUID().toString(),
          "equation_uid" -> id.toString(),
          "content" -> chunk //AlignmentBaseline.replaceGreekWithWord(chunk, greek2wordDict.toMap)
        )
      }
    }

    val fullEquations = equation2uuid.keys.map(key =>
      ujson.Obj(
        "uid" -> equation2uuid(key).toString(),
        "content" -> key
      ).toString()
    ).toSeq
    (eqLinkElements, fullEquations)
  }

  /* Align description mentions from two sources; not currently used */
 def getInterModelComparisonLinkElements(
                       descrMentions1:
                       Seq[Mention],
                       descrMentions2: Seq[Mention]
                     ): Map[String, Seq[String]] = {

    val linkElements = scala.collection.mutable.HashMap[String, Seq[String]]()

      linkElements("TEXT_VAR1") = descrMentions1.map { mention =>
        val docId = mention.document.id.getOrElse("unk_text_file")
        val sent = mention.sentence
        val originalSentence = mention.sentenceObj.words.mkString(" ")
        val offsets = mention.tokenInterval.toString()
        val textVar = mention.arguments(VARIABLE).head.text
        val description = mention.arguments(DESCRIPTION).head.text

        ujson.Obj(
          "uid" -> randomUUID.toString(),
          "source" -> docId,
          "content" -> textVar,
          "description" -> description,
          "original_sentence" -> originalSentence
        ).toString()

      }

      linkElements("TEXT_VAR2") = descrMentions2.map { mention =>
        val docId = mention.document.id.getOrElse("unk_text_file")
        val sent = mention.sentence
        val originalSentence = mention.sentenceObj.words.mkString(" ")
        val offsets = mention.tokenInterval.toString()
        val textVar = mention.arguments(VARIABLE).head.text
        val description = mention.arguments(DESCRIPTION).head.text
        ujson.Obj(
          "uid" -> randomUUID.toString(),
          "source" -> docId,
          "content" -> textVar,
          "description" -> description,
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
      "text_description"-> o.obj("text_description"),
      "text_identifier"-> o.obj("text_identifier"),
        "grfn1_var_uid" -> paper1id
      )
    } yield updated

    val updatedWithPaperId2 = for {
      o <- paper2Objects
      updated = ujson.Obj(
        "var_uid" -> o.obj("var_uid"),
        "code_identifier"-> o.obj("code_identifier"),
        "text_description"-> o.obj("text_description"),
        "text_identifier"-> o.obj("text_identifier"),
        "grfn2_var_uid" -> paper2id
      )
    } yield updated


    linkElements("grfn1_vars") = updatedWithPaperId1
    linkElements("grfn2_vars") = updatedWithPaperId2
    linkElements.toMap
  }


  def mkLinkHypothesisTextVarDescr(variables: Seq[String], descriptions: Seq[String], debug: Boolean): Seq[Obj] = {

    assert(variables.length == descriptions.length)
    for {
      i <- variables.indices
    } yield mkHypothesis(variables(i), descriptions(i), 1.0, debug)
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

    // Src Variable -> Comment
    if (linkElements.contains(GLOBAL_SRC_VAR) && linkElements.contains(GLOBAL_COMMENT)) {
      println("has source and comment")

      hypotheses.appendAll(mkLinkHypothesis(linkElements(GLOBAL_SRC_VAR), linkElements(GLOBAL_COMMENT), SRC_TO_COMMENT, alignments(SRC_TO_COMMENT), debug))
    }

    if (linkElements.contains(GLOBAL_VAR)) {

      // Comment -> Text Var
      if (linkElements.contains(GLOBAL_COMMENT)) {
        hypotheses.appendAll(mkLinkHypothesis(linkElements(GLOBAL_COMMENT), linkElements(GLOBAL_VAR), COMMENT_TO_GLOBAL_VAR, alignments(COMMENT_TO_GLOBAL_VAR), debug))
      }

      // Equation -> Text
      if (alignments.contains(EQN_TO_GLOBAL_VAR)) {
        println("has eq and text")
        hypotheses.appendAll(mkLinkHypothesis(linkElements(GLOBAL_EQ_VAR), linkElements(GLOBAL_VAR), EQN_TO_GLOBAL_VAR, alignments(EQN_TO_GLOBAL_VAR), debug))
      }

      // TextVar to Unit (through identifier)
      if (linkElements.contains(UNIT_VIA_IDFR)) {
        hypotheses.appendAll(mkLinkHypothesis(linkElements(GLOBAL_VAR), linkElements(UNIT_VIA_IDFR), GLOBAL_VAR_TO_UNIT_VIA_IDENTIFIER, alignments(GLOBAL_VAR_TO_UNIT_VIA_IDENTIFIER), debug))
      }

      // TextVar to Unit (through concept)
      if (linkElements.contains(UNIT_VIA_CNCPT)) {
        hypotheses.appendAll(mkLinkHypothesis(linkElements(GLOBAL_VAR), linkElements(UNIT_VIA_CNCPT), GLOBAL_VAR_TO_UNIT_VIA_CONCEPT, alignments(GLOBAL_VAR_TO_UNIT_VIA_CONCEPT), debug))
      }

      // TextVar to ParamSetting (through identifier)
      if (linkElements.contains(PARAM_SETTING_VIA_IDFR)) {
        hypotheses.appendAll(mkLinkHypothesis(linkElements(GLOBAL_VAR), linkElements(PARAM_SETTING_VIA_IDFR), GLOBAL_VAR_TO_PARAM_SETTING_VIA_IDENTIFIER, alignments(GLOBAL_VAR_TO_PARAM_SETTING_VIA_IDENTIFIER), debug))
      }

      // TextVar to ParamSetting (through concept)
      if (linkElements.contains(PARAM_SETTING_VIA_CNCPT)) {
        hypotheses.appendAll(mkLinkHypothesis(linkElements(GLOBAL_VAR), linkElements(PARAM_SETTING_VIA_CNCPT), GLOBAL_VAR_TO_PARAM_SETTING_VIA_CONCEPT, alignments(GLOBAL_VAR_TO_PARAM_SETTING_VIA_CONCEPT), debug))
      }

      // TextVar to IntervalParamSetting (through identifier)
      if (linkElements.contains(INT_PARAM_SETTING_VIA_IDFR)) {
        hypotheses.appendAll(mkLinkHypothesis(linkElements(GLOBAL_VAR), linkElements(INT_PARAM_SETTING_VIA_IDFR), GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_IDENTIFIER, alignments(GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_IDENTIFIER), debug))
      }

      // TextVar to IntervalParamSetting (through concept)
      if (linkElements.contains(INT_PARAM_SETTING_VIA_CNCPT)) {
        hypotheses.appendAll(mkLinkHypothesis(linkElements(GLOBAL_VAR), linkElements(INT_PARAM_SETTING_VIA_CNCPT), GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_CONCEPT, alignments(GLOBAL_VAR_TO_INT_PARAM_SETTING_VIA_CONCEPT), debug))
      }

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

    val config: Config = ConfigFactory.load()
    val numAlignments = config[Int]("apps.numAlignments") // for all but srcCode to comment, which we set to top 1
    val scoreThreshold = config[Double]("apps.commentTextAlignmentScoreThreshold")
    val loadMentions = config[Boolean]("apps.loadMentions")
    val appendToGrFN = config[Boolean]("apps.appendToGrFN")
    val serializerName = config[String]("apps.serializerName")
    val groundToSVO = config[Boolean]("apps.groundToSVO")
    val maxSVOgroundingsPerVar = config[Int]("apps.maxSVOgroundingsPerVar")
    val groundToWiki = config[Boolean]("apps.groundToWiki")
    val numOfWikiGroundings = config[Int]("apps.numOfWikiGroundings")
    val saveWikiGroundings = config[Boolean]("apps.saveWikiGroundingsDefault")
    val pathToWikiGroundings = config[String]("apps.pathToWikiGroundings")

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
    // Get source identifiers
    val identifierNames = Some(GrFNParser.getVariables(grfn))
    val variableShortNames = Some(GrFNParser.getVariableShortNames(identifierNames.get))

    // Get comment descriptions
    val commentDescriptionMentions = getCommentDescriptionMentions(localCommentReader, grfn, variableShortNames, source)
      .filter(m => hasRequiredArgs(m, "description"))

    val allUsedTextMentions = if (loadMentions) {
      val mentionsFile = new File(config[String]("apps.mentionsFile"))
      (JSONSerializer.toMentions(mentionsFile).filter(_.label matches "Description"),
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
    val textDescriptionMentions = allUsedTextMentions._1
    val parameterSettingMentions = allUsedTextMentions._2
    val intervalParameterSettingMentions = allUsedTextMentions._3
    val unitMentions = allUsedTextMentions._4

    logger.info(s"Extracted ${textDescriptionMentions.length} descriptions from text")

    // load wikigroundings if available
    val wikigroundings = if (groundToWiki) {
      if (new File(pathToWikiGroundings.toString).canRead) {
        val groundingsAsUjson = ujson.read(new File(pathToWikiGroundings.toString))
        val groundingMap = mutable.Map[String, Seq[sparqlWikiResult]]()
        for (item <- groundingsAsUjson("wikiGroundings").arr) {
          val identString = item.obj("variable").str
          val groundings = item.obj("groundings").arr.map(gr => new sparqlWikiResult(gr("searchTerm").str, gr("conceptID").str, gr("conceptLabel").str, Some(gr("conceptDescription").arr.map(_.str).mkString(" ")), Some(gr("alternativeLabel").arr.map(_.str).mkString(" ")), Some(gr("subClassOf").arr.map(_.str).mkString(" ")), Some(gr("score").arr.head.num), gr("source").str)).toSeq
          groundingMap(identString) = groundings
        }
        Some(groundingMap.toMap)
      } else None

    } else None
    // Load equations and "extract" variables/chunks (using heuristics)
    val equationFile: String = config[String]("apps.predictedEquations")
    val equationChunksAndSource = Some(loadEquations(equationFile))

    // Make an alignment handler which handles all types of alignment being used
    val alignmentHandler = new AlignmentHandler(config[Config]("alignment"))

    // Ground the extracted text mentions, the comments, and the equation variables to the grfn variables
    val groundedGrfn = groundMentions(
      grfn: Value,
      identifierNames,
      variableShortNames,
      Some(textDescriptionMentions),
      Some(parameterSettingMentions),
      Some(intervalParameterSettingMentions),
      Some(unitMentions),
      Some(commentDescriptionMentions),
      equationChunksAndSource,
      None, //not passing svo groundings from grfn
      wikigroundings: Option[Map[String, Seq[sparqlWikiResult]]],
      groundToSVO: Boolean,
      groundToWiki: Boolean,
      saveWikiGroundings: Boolean,
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
//          println(s"              SRC VAR: ${commentDescriptionMentions(aa.head.src).arguments("variable").head.text}")
//          println("====================================================================")
//          aa.foreach { topK =>
//            val v1Text = commentDescriptionMentions(topK.src).text
//            val v2Text = textDescriptionMentions(topK.dst).text
//            println(s"aligned variable (comment): ${commentDescriptionMentions(topK.src).arguments("variable").head.text} ${commentDescriptionMentions(topK.src).arguments("variable").head.foundBy}")
//            println(s"aligned variable (text): ${textDescriptionMentions(topK.dst).arguments("variable").head.text}")
//            println(s"comment: ${v1Text}")
//            println(s"text: ${v2Text}")
//              println(s"text: ${v2Text} ${textDescriptionMentions(topK.dst).label} ${textDescriptionMentions(topK.dst).foundBy}") //printing out the label and the foundBy helps debug rules
//            println(s"score: ${topK.score}\n")
//          }
//        }
  }


}
