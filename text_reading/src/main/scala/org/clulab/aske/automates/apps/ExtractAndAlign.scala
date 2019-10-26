package org.clulab.aske.automates.apps

import java.io.{File, PrintWriter}

import ai.lum.common.ConfigUtils._
import ai.lum.common.FileUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.aske.automates.data.{DataLoader, TextRouter, TokenizedLatexDataLoader}
import org.clulab.aske.automates.alignment.{Aligner, VariableEditDistanceAligner}
import org.clulab.aske.automates.grfn.GrFNParser.{mkHypothesis, mkLinkElement}
import org.clulab.aske.automates.OdinEngine
import org.clulab.aske.automates.entities.GrFNEntityFinder
import org.clulab.aske.automates.grfn.GrFNParser
import org.clulab.utils.{DisplayUtils, FileUtils}
import org.slf4j.LoggerFactory


import scala.collection.mutable.ArrayBuffer


object ExtractAndAlign {

  val logger = LoggerFactory.getLogger(this.getClass())

  def main(args: Array[String]): Unit = {

    val config: Config = ConfigFactory.load()

    // =============================================
    //                 DATA LOADING
    // =============================================

    // Instantiate the text reader
    val textConfig: Config = config[Config]("TextEngine")
    val textReader = OdinEngine.fromConfig(textConfig)

    // Instantiate the comment reader
    val commentReader = OdinEngine.fromConfig(config[Config]("CommentEngine"))
    // todo: future readers
    //    val glossaryReader = OdinEngine.fromConfig(config[Config]("GlossaryEngine"))
    //    val tocReader = OdinEngine.fromConfig(config[Config]("TableOfContentsEngine"))
    val textRouter = new TextRouter(Map(TextRouter.TEXT_ENGINE -> textReader, TextRouter.COMMENT_ENGINE -> commentReader))

    // Load a GrFN
    val grfnPath: String = config[String]("apps.grfnFile")
    val grfnFile = new File(grfnPath)
    val grfn = ujson.read(grfnFile.readString())


    // Load text input from directory
    val inputDir = config[String]("apps.inputDirectory")
    val inputType = config[String]("apps.inputType")
    val dataLoader = DataLoader.selectLoader(inputType) // txt, json (from science parse), pdf supported
    val files = FileUtils.findFiles(inputDir, dataLoader.extension)


    // Load the equation file and get the tokens, ** chunked with heuristics **
    // FIXME: Paul, this is where we need to plug in calling the equation model
    val equationFile: String = config[String]("apps.predictedEquations")
    val equationDataLoader = new TokenizedLatexDataLoader
    val equations = equationDataLoader.loadFile(new File(equationFile))
    val equationChunksAndSource = for {
      (sourceEq, i) <- equations.zipWithIndex
      eqChunk <- equationDataLoader.chunkLatex(sourceEq)
    } yield (eqChunk, sourceEq)
    val (equationChunks, equationSources) = equationChunksAndSource.unzip


    // =============================================
    //                 EXTRACTION
    // =============================================

    // ---- TEXT -----

    val textMentions = files.par.flatMap { file =>
      logger.info(s"Extracting from ${file.getName}")
      val texts: Seq[String] = dataLoader.loadFile(file)
      // Route text based on the amount of sentence punctuation and the # of numbers (too many numbers = non-prose from the paper)
      texts.flatMap(text => textRouter.route(text).extractFromText(text, filename = Some(file.getName)))
    }
    logger.info(s"Extracted ${textMentions.length} text mentions")
    val textDefinitionMentions = textMentions.seq.filter(_ matches "Definition")

    // ---- SRC CODE VARIABLES -----

    val variableNames = grfn("variables").arr.map(_.obj("name").str)
    // The variable names only (excluding the scope info)
    val variableShortNames = GrFNEntityFinder.getVariableShortNames(variableNames)

    // ---- COMMENTS -----

    val commentDocs = GrFNParser.getCommentDocs(grfn)

    // Iterate through the docs and find the mentions; eliminate duplicates
    val commentMentions = commentDocs.flatMap(doc => commentReader.extractFrom(doc)).distinct

    val commentDefinitionMentions = commentMentions.seq.filter(_ matches "Definition").filter(m => variableShortNames.map(string => string.toLowerCase).contains(m.arguments("variable").head.text.toLowerCase))


    // =============================================
    //                 ALIGNMENT
    // =============================================

    val numAlignments = config[Int]("apps.numAlignments") // for all but srcCode to comment, which we set to top 1
    val numAlignmentsSrcToComment: Int = 1
    val scoreThreshold = config[Double]("apps.commentTextAlignmentScoreThreshold")

    // Initialize the Aligners
    val editDistanceAligner = new VariableEditDistanceAligner(Set("variable"))
    val w2vAligner = Aligner.fromConfig(config[Config]("alignment"))

    /** Align the comment definitions to the GrFN variables */

    val varNameAlignments = editDistanceAligner.alignTexts(variableShortNames, commentDefinitionMentions.map(Aligner.getRelevantText(_, Set("variable"))))
    // group by src idx, and keep only top k (src, dst, score) for each src idx, here k = 1
    val top1SourceToComment = Aligner.topKBySrc(varNameAlignments, numAlignmentsSrcToComment)

    /** Align the equation chunks to the text definitions */
    val equationToTextAlignments = editDistanceAligner.alignTexts(equationChunks, textDefinitionMentions.map(Aligner.getRelevantText(_, Set("variable"))))
    // group by src idx, and keep only top k (src, dst, score) for each src idx
    val topKEquationToText = Aligner.topKBySrc(equationToTextAlignments, numAlignments)

    /** Align the comment definitions to the text definitions */
    val commentToTextAlignments = w2vAligner.alignMentions(commentDefinitionMentions, textDefinitionMentions)
    // group by src idx, and keep only top k (src, dst, score) for each src idx
    val topKCommentToText = Aligner.topKBySrc(commentToTextAlignments, numAlignments, scoreThreshold)

    // =============================================
    //           CREATE JSON LINK ELEMENTS
    // =============================================

    // Make Comment Spans from the comment variable mentions
    val commentLinkElems = commentDefinitionMentions.map { commentMention =>
      mkLinkElement(
        elemType = "comment_span",
        source = commentMention.document.id.getOrElse("unk_file"),
        content = commentMention.text,
        contentType = "null"
      )
    }

    // Repeat for src code variables
    val sourceLinkElements = variableNames.map { varName =>
      mkLinkElement(
        elemType = "identifier",
        source = grfn("source").arr.head.str,
        content = varName,
        contentType = "null"
      )
    }

    // Repeat for text variables
    val textLinkElements = textDefinitionMentions.map { mention =>
      mkLinkElement(
        elemType = "text_span",
        source = mention.document.id.getOrElse("unk_text_file"), // fixme
        content = mention.text, //todo add the relevant parts of the metnion var + def as a string --> smth readable,
        contentType = "null"
      )
    }

    // Repeat for Eqn Variables
    val equationLinkElements = equationChunksAndSource.map { case (chunk, orig) =>
      mkLinkElement(
        elemType = "equation_span",
        source = orig,
        content = chunk,
        contentType = "null"
      )
    }

    // =============================================
    //         CREATE JSON LINK HYPOTHESES
    // =============================================

    // Store them all here
    val hypotheses = new ArrayBuffer[ujson.Obj]()

    // Comment -> Text
    for (topK <- topKCommentToText) {
      for (alignment <- topK) {
        val commentLinkElement = commentLinkElems(alignment.src)
        val textLinkElement = textLinkElements(alignment.dst)
        val score = alignment.score
        val hypothesis = mkHypothesis(commentLinkElement, textLinkElement, score)
        hypotheses.append(hypothesis)
      }
    }

    // Src Variable -> Comment
    for (topK <- top1SourceToComment) {
      for (alignment <- topK) {
        val variableLinkElement = sourceLinkElements(alignment.src)
        val commentLinkElement = commentLinkElems(alignment.dst)
        val score = alignment.score
        val hypothesis = mkHypothesis(variableLinkElement, commentLinkElement, score)
        hypotheses.append(hypothesis)
      }
    }

    // Equation -> Text
    for (topK <- topKEquationToText) {
      for (alignment <- topK) {
        val equationLinkElement = equationLinkElements(alignment.src)
        val textLinkElement = textLinkElements(alignment.dst)
        val score = alignment.score
        val hypothesis = mkHypothesis(equationLinkElement, textLinkElement, score)
        hypotheses.append(hypothesis)
      }
    }

    // =============================================
    //                    EXPORT
    // =============================================

    // Add the grounding links to the GrFN
    grfn("grounding") = hypotheses.toList

    // Export
    val outputDir = config[String]("apps.outputDirectory")
    val grfnBaseName = new File(grfnPath).getBaseName()
    val grfnWriter = new PrintWriter(s"$outputDir/${grfnBaseName}_with_groundings.json")
    ujson.writeTo(grfn, grfnWriter)
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