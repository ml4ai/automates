package org.clulab.aske.automates.apps

import java.io.{File, PrintWriter}

import ai.lum.common.ConfigUtils._
import ai.lum.common.FileUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.aske.automates.data.{DataLoader, TextRouter, TokenizedLatexDataLoader}
import org.clulab.aske.automates.alignment.{Aligner, Alignment, AlignmentHandler, VariableEditDistanceAligner}
import org.clulab.aske.automates.grfn.GrFNParser.{mkHypothesis, mkLinkElement}
import org.clulab.aske.automates.OdinEngine
import org.clulab.aske.automates.entities.GrFNEntityFinder
import org.clulab.aske.automates.grfn.GrFNParser
import org.clulab.odin.Mention
import org.clulab.utils.{DisplayUtils, FileUtils}
import org.slf4j.LoggerFactory
import ujson.{Obj, Value}
import org.clulab.grounding
import org.clulab.grounding.{Grounding, SVOGrounder, SeqOfGroundings, sparqlResult}

import scala.collection.mutable.ArrayBuffer


object ExtractAndAlign {
  val COMMENT = "comment"
  val TEXT = "text"
  val SOURCE = "source"
  val EQUATION = "equation"
  val SVO_GROUNDING = "SVOgrounding"
  val SRC_TO_COMMENT = "sourceToComment"
  val EQN_TO_TEXT = "equationToText"
  val COMMENT_TO_TEXT = "commentToText"
  val TEXT_TO_SVO = "textToSVO"

  val logger = LoggerFactory.getLogger(this.getClass())

  def groundMentionsToGrfn(
    textMentions: Seq[Mention],
    grfn: Value,
    commentReader: OdinEngine,
    equationChunksAndSource: Seq[(String, String)],
    alignmentHandler: AlignmentHandler,
    numAlignments: Int = 5,
    numAlignmentsSrcToComment: Int = 1,
    scoreThreshold: Double = 0.0): Value = {

    // =============================================
    // Extract the variables and comment Mentions
    // =============================================

    // source code
    val variableNames = GrFNParser.getVariables(grfn)
    // The variable names only (excluding the scope info)
    val variableShortNames = GrFNParser.getVariableShortNames(variableNames)

    // source code comments
    val commentDefinitionMentions = getCommentDefinitionMentions(commentReader, grfn, Some(variableShortNames))

    // svo groundings
    val definitionMentions = textMentions.filter(m => m.label matches "Definition")

    val definitionMentionGroundings = SVOGrounder.groundDefinitionsToSVO(definitionMentions, 5)

    // =============================================
    // Alignment
    // =============================================
    // add in SVO

    val alignments = alignElements(
      alignmentHandler,
      textMentions,
      equationChunksAndSource.unzip._1,
      commentDefinitionMentions,
      variableShortNames,
      numAlignments,
      numAlignmentsSrcToComment,
      scoreThreshold
    )

    val linkElements = getLinkElements(grfn, textMentions, commentDefinitionMentions, equationChunksAndSource, variableNames)

    val hypotheses = getLinkHypotheses(linkElements, alignments, definitionMentionGroundings)

    // =============================================
    //                    EXPORT
    // =============================================

    // Add the grounding links to the GrFN
    GrFNParser.addHypotheses(grfn, hypotheses)
  }

  def loadEquations(filename: String): Seq[(String, String)] = {
    val equationDataLoader = new TokenizedLatexDataLoader
    val equations = equationDataLoader.loadFile(new File(filename))
    // tuple pairing each chunk with the original latex equation it came from
    for {
      sourceEq <- equations
      eqChunk <- equationDataLoader.chunkLatex(sourceEq)
    } yield (eqChunk, sourceEq)
  }

  def getTextDefinitionMentions(textReader: OdinEngine, dataLoader: DataLoader, textRouter: TextRouter, files: Seq[File]): Seq[Mention] = {
    val textMentions = files.par.flatMap { file =>
      logger.info(s"Extracting from ${file.getName}")
      val texts: Seq[String] = dataLoader.loadFile(file)
      // Route text based on the amount of sentence punctuation and the # of numbers (too many numbers = non-prose from the paper)
      texts.flatMap(text => textRouter.route(text).extractFromText(text, filename = Some(file.getName)))
    }
    logger.info(s"Extracted ${textMentions.length} text mentions")

    textMentions.seq.filter(_ matches "Definition")
  }

  def getCommentDefinitionMentions(commentReader: OdinEngine, grfn: Value, variableShortNames: Option[Seq[String]]): Seq[Mention] = {
    val commentDocs = GrFNParser.getCommentDocs(grfn)
    println(s"len commentDocs: ${commentDocs.length}")

    // Iterate through the docs and find the mentions; eliminate duplicates
    val commentMentions = commentDocs.flatMap(doc => commentReader.extractFrom(doc)).distinct
    println(s"len commentMentions: ${commentMentions.length}")
    val definitions = commentMentions.seq.filter(_ matches "Definition")
    println(s"len definitions: ${definitions.length}")
    if (variableShortNames.isEmpty) return definitions
    println("Didn't return in the line above")
    val overlapsWithVariables = definitions.filter(
      m => variableShortNames.get
        .map(string => string.toLowerCase)
        .contains(m.arguments("variable").head.text.toLowerCase)
    )
    println(s"len overlapsWithVariables: ${overlapsWithVariables.length}")
    overlapsWithVariables
  }

  def alignElements(
    alignmentHandler: AlignmentHandler,
    textDefinitionMentions: Seq[Mention],
    equationChunks: Seq[String],
    commentDefinitionMentions: Seq[Mention],
    variableShortNames: Seq[String],
    numAlignments: Int,
    numAlignmentsSrcToComment: Int,
    scoreThreshold: Double): Map[String, Seq[Seq[Alignment]]] = {

    val alignments = scala.collection.mutable.HashMap[String, Seq[Seq[Alignment]]]()

    val varNameAlignments = alignmentHandler.editDistance.alignTexts(variableShortNames, commentDefinitionMentions.map(Aligner.getRelevantText(_, Set("variable"))))
    // group by src idx, and keep only top k (src, dst, score) for each src idx, here k = 1
    alignments(SRC_TO_COMMENT) = Aligner.topKBySrc(varNameAlignments, numAlignmentsSrcToComment)

    /** Align the equation chunks to the text definitions */
    val equationToTextAlignments = alignmentHandler.editDistance.alignTexts(equationChunks, textDefinitionMentions.map(Aligner.getRelevantText(_, Set("variable"))))
    // group by src idx, and keep only top k (src, dst, score) for each src idx
    alignments(EQN_TO_TEXT) = Aligner.topKBySrc(equationToTextAlignments, numAlignments)

    /** Align the comment definitions to the text definitions */
    val commentToTextAlignments = alignmentHandler.w2v.alignMentions(commentDefinitionMentions, textDefinitionMentions)
    // group by src idx, and keep only top k (src, dst, score) for each src idx
    alignments(COMMENT_TO_TEXT) = Aligner.topKBySrc(commentToTextAlignments, numAlignments, scoreThreshold, debug = true)

    alignments.toMap
  }

  def getLinkElements(
    grfn: Value,
    textDefinitionMentions:
    Seq[Mention],
    commentDefinitionMentions: Seq[Mention],
    equationChunksAndSource: Seq[(String, String)],
    variableNames: Seq[String]
  ): Map[String, Seq[Obj]] = {
    // Make Comment Spans from the comment variable mentions
    val linkElements = scala.collection.mutable.HashMap[String, Seq[Obj]]()
    linkElements(COMMENT) = commentDefinitionMentions.map { commentMention =>
      mkLinkElement(
        elemType = "comment_span",
        source = commentMention.document.id.getOrElse("unk_file"),
        content = commentMention.text,
        contentType = "null"
      )
    }

    // Repeat for src code variables
    linkElements(SOURCE) = variableNames.map { varName =>
      mkLinkElement(
        elemType = "identifier",
        source = grfn("source").arr.head.str,
        content = varName,
        contentType = "null"
      )
    }

    // Repeat for text variables
    println("!!!!!!!!!!!")
    println(textDefinitionMentions.length)
    println("!!!!!!!!!!!")
    linkElements(TEXT) = textDefinitionMentions.map { mention =>
      mkLinkElement(
        elemType = "text_span",
        source = mention.document.id.getOrElse("unk_text_file"), // fixme
        content = mention.text, //todo add the relevant parts of the metnion var + def as a string --> smth readable,
        contentType = "null"
      )
    }

    // Repeat for Eqn Variables
    linkElements(EQUATION) = equationChunksAndSource.map { case (chunk, orig) =>
      mkLinkElement(
        elemType = "equation_span",
        source = orig,
        content = chunk,
        contentType = "null"
      )
    }

    linkElements.toMap
  }

  def mkLinkHypothesis(srcElements: Seq[Obj], dstElements: Seq[Obj], alignments: Seq[Seq[Alignment]]): Seq[Obj] = {
    for {
      topK <- alignments
      alignment <- topK
      srcLinkElement = srcElements(alignment.src)
      dstLinkElement = dstElements(alignment.dst)
      score = alignment.score
    } yield mkHypothesis(srcLinkElement, dstLinkElement, score)
  }

  def mkLinkHypothesis(groundings: Seq[Grounding]): Seq[Obj] = {
    for {
      //each grounding is a mapping from text variable to seq of possible svo groundings (as sparqlResults)
      gr <- groundings
      g <- gr.groundings
      //text link element//text link element
      srcLinkElement = mkLinkElement(
        elemType = "text_span",
        source = "text_file", // fixme: the name of the file
        content = gr.variable, //the variable associated with the definition that we used for grounding
        contentType = "null"
      )
      dstLinkElement = GrFNParser.mkSVOElement(g)

    } yield mkHypothesis(srcLinkElement, dstLinkElement, g.score.get)
  }

  def getLinkHypotheses(linkElements: Map[String, Seq[Obj]], alignments: Map[String, Seq[Seq[Alignment]]], SVOGroungings: Seq[Grounding]): Seq[Obj] = {
    // Store them all here
    val hypotheses = new ArrayBuffer[ujson.Obj]()

    // Comment -> Text
    hypotheses.appendAll(mkLinkHypothesis(linkElements(COMMENT), linkElements(TEXT), alignments(COMMENT_TO_TEXT)))

    // Src Variable -> Comment
    hypotheses.appendAll(mkLinkHypothesis(linkElements(SOURCE), linkElements(COMMENT), alignments(SRC_TO_COMMENT)))

    // Equation -> Text
    hypotheses.appendAll(mkLinkHypothesis(linkElements(EQUATION), linkElements(TEXT), alignments(EQN_TO_TEXT)))

    // Text -> SVO grounding
    hypotheses.appendAll(mkLinkHypothesis(SVOGroungings))

    hypotheses
  }

  def main(args: Array[String]): Unit = {

    val config: Config = ConfigFactory.load()
    val numAlignments = config[Int]("apps.numAlignments") // for all but srcCode to comment, which we set to top 1
    val scoreThreshold = config[Double]("apps.commentTextAlignmentScoreThreshold")


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

    // Load text and extract definition mentions
    val inputDir = config[String]("apps.inputDirectory")
    val inputType = config[String]("apps.inputType")
    val dataLoader = DataLoader.selectLoader(inputType) // txt, json (from science parse), pdf supported
    val files = FileUtils.findFiles(inputDir, dataLoader.extension)
    val textDefinitionMentions = getTextDefinitionMentions(textReader, dataLoader, textRouter, files)
    logger.info(s"Extracted ${textDefinitionMentions.length} definitions from text")

    // Load equations and "extract" variables/chunks (using heuristics)
    val equationFile: String = config[String]("apps.predictedEquations")
    val equationChunksAndSource = loadEquations(equationFile)


    // Make an alignment handler which handles all types of alignment being used
    val alignmentHandler = new AlignmentHandler(config[Config]("alignment"))

    // Ground the extracted text mentions, the comments, and the equation variables to the grfn variables
    val groundedGrfn = groundMentionsToGrfn(
      textDefinitionMentions,
      grfn,
      localCommentReader,
      equationChunksAndSource,
      alignmentHandler,
      numAlignments,
      1,
      scoreThreshold)

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