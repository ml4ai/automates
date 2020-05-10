package org.clulab.aske.automates.apps

import java.io.{File, PrintWriter}

import ai.lum.common.ConfigUtils._
import ai.lum.common.FileUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.aske.automates.data.{DataLoader, TextRouter, TokenizedLatexDataLoader}
import org.clulab.aske.automates.alignment.{Aligner, Alignment, AlignmentHandler, VariableEditDistanceAligner}
import org.clulab.aske.automates.grfn.GrFNParser.{mkHypothesis, mkLinkElement, mkTextLinkElement}
import org.clulab.aske.automates.OdinEngine
import org.clulab.aske.automates.apps.AlignmentBaseline.{word2greekDict, greek2wordDict}
import org.clulab.aske.automates.entities.GrFNEntityFinder
import org.clulab.aske.automates.grfn.GrFNParser
import org.clulab.odin.Mention
import org.clulab.utils.{AlignmentJsonUtils, DisplayUtils, FileUtils}
import org.slf4j.LoggerFactory
import ujson.{Obj, Value}
import org.clulab.grounding
import org.clulab.grounding.{SVOGrounder, SVOGrounding, SeqOfGroundings, sparqlResult}
import org.clulab.odin.serialization.json.JSONSerializer
import org.json4s

import scala.collection.mutable.ArrayBuffer

case class alignmentArguments(json: Value, variableNames: Option[Seq[String]], variableShortNames: Option[Seq[String]], commentDefinitionMentions: Option[Seq[Mention]], definitionMentions: Option[Seq[Mention]], equationChunksAndSource: Option[Seq[(String, String)]], svoGroundings: Option[Map[String, Seq[sparqlResult]]])

object ExtractAndAlign {
  val COMMENT = "comment"
  val TEXT = "text"
  val TEXT_VAR = "text_var"
  val SOURCE = "source"
  val EQUATION = "equation"
  val SVO_GROUNDING = "SVOgrounding"
  val SRC_TO_COMMENT = "sourceToComment"
  val EQN_TO_TEXT = "equationToText"
  val COMMENT_TO_TEXT = "commentToText"
  val TEXT_TO_SVO = "textToSVO"
  val DEFINITION = "definition"
  val VARIABLE = "variable"
  val DEF_LABEL = "Definition"

  val logger = LoggerFactory.getLogger(this.getClass())

  def groundMentions(
                      grfn: Value,
                      variableNames: Option[Seq[String]],
                      variableShortNames: Option[Seq[String]],
                      definitionMentions: Option[Seq[Mention]],
                      commentDefinitionMentions: Option[Seq[Mention]],
                      equationChunksAndSource: Option[Seq[(String, String)]],
                      SVOgroundings: Option[Map[String, Seq[sparqlResult]]],
                      groundToSVO: Boolean,
                      maxSVOgroundingsPerVar: Int,
                      alignmentHandler: AlignmentHandler,
                      numAlignments: Option[Int],
                      numAlignmentsSrcToComment: Option[Int],
                      scoreThreshold: Double = 0.0,
                      appendToGrFN: Boolean
    ): Value = {

    // =============================================
    // Alignment
    // =============================================
    // add in SVO

    val alignments = alignElements(
      alignmentHandler,
      definitionMentions, //fixme: here and in get linkElements---pass all mentions, only definition mentions, other types?
      equationChunksAndSource,
      commentDefinitionMentions,
      variableShortNames,
      numAlignments,
      numAlignmentsSrcToComment,
      scoreThreshold
    )

    val linkElements = getLinkElements(grfn, definitionMentions, commentDefinitionMentions, equationChunksAndSource, variableNames)

    var hypotheses = getLinkHypotheses(linkElements, alignments)


    if (groundToSVO) {
      if (SVOgroundings.isDefined) {
        logger.info("Making Text-variable/SVO link hypotheses")
        //this means they have been read in from json during getArgsForAlignment
        val svo_hypotheses = mkLinkHypotheses(SVOgroundings.get)
        hypotheses = hypotheses ++ svo_hypotheses
      } else {
        logger.warn("No svo groundings provided in json; querying the SVO ontology with Sparql")
        //query svo here
        val groundings = SVOGrounder.groundHypothesesToSVO(hypotheses, maxSVOgroundingsPerVar)
        if (groundings.isDefined) {
          hypotheses = hypotheses ++ mkLinkHypotheses(groundings.get)
        }

      }
    } else logger.warn("SVO grounding is disabled")


    // the produced hypotheses can be either appended to the input file as "groundings" or returned as a separate ujson object
    if (appendToGrFN) {
      // Add the grounding links to the GrFN
      GrFNParser.addHypotheses(grfn, hypotheses)
    } else hypotheses

  }

  def hasRequiredArgs(m: Mention): Boolean = m.arguments.contains(VARIABLE) && m.arguments.contains(DEFINITION)

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
    val pdfAlignDir = "/home/alexeeva/Repos/automates/src/apps/pdfalign"
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
      .filter(cand => is_balanced(cand))
      .map(c => AlignmentBaseline.replaceWordWithGreek(c, word2greekDict.toMap)) //before filtering out latex control sequences, change greek letters from latex control spelling; it will be switch back to word while creating the link element
      .filter(chunk => !chunk.matches("&?\\\\\\w+&?")) //to eliminate standalone latex control sequences, e.g., \\times (they can have ampersands on each side)
  }

  def getTextDefinitionMentions(textReader: OdinEngine, dataLoader: DataLoader, textRouter: TextRouter, files: Seq[File]): Seq[Mention] = {
    val textMentions = files.par.flatMap { file =>
      logger.info(s"Extracting from ${file.getName}")
      val texts: Seq[String] = dataLoader.loadFile(file)
      // Route text based on the amount of sentence punctuation and the # of numbers (too many numbers = non-prose from the paper)
      texts.flatMap(text => textRouter.route(text).extractFromText(text, filename = Some(file.getName)))
    }
    logger.info(s"Extracted ${textMentions.length} text mentions")

    textMentions.seq.filter(_ matches DEF_LABEL)
  }

  def getCommentDefinitionMentions(commentReader: OdinEngine, alignmentInputFile: Value, variableShortNames: Option[Seq[String]], source: Option[String]): Seq[Mention] = {
    val commentDocs = if (alignmentInputFile.obj.get("source_code").isDefined) {
      AlignmentJsonUtils.getCommentDocs(alignmentInputFile, source)
    } else GrFNParser.getCommentDocs(alignmentInputFile)

//    for (cd <- commentDocs) println("comm doc: " + cd.text)
    // Iterate through the docs and find the mentions; eliminate duplicates
    val commentMentions = commentDocs.flatMap(doc => commentReader.extractFrom(doc)).distinct

//    for (cm <- commentMentions) println("com mention: " + cm.text)
    val definitions = commentMentions.seq.filter(_ matches DEF_LABEL)
//    for (cm <- definitions) println("com def mention: " + cm.text)
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
    equationChunksAndSource: Option[Seq[(String, String)]],
    commentDefinitionMentions: Option[Seq[Mention]],
    variableShortNames: Option[Seq[String]],
    numAlignments: Option[Int],
    numAlignmentsSrcToComment: Option[Int],
    scoreThreshold: Double): Map[String, Seq[Seq[Alignment]]] = {


    val alignments = scala.collection.mutable.HashMap[String, Seq[Seq[Alignment]]]()

    if (commentDefinitionMentions.isDefined && variableShortNames.isDefined) {
      val varNameAlignments = alignmentHandler.editDistance.alignTexts(variableShortNames.get.map(_.toLowerCase), commentDefinitionMentions.get.map(Aligner.getRelevantText(_, Set("variable"))).map(_.toLowerCase()))
      // group by src idx, and keep only top k (src, dst, score) for each src idx, here k = 1
      alignments(SRC_TO_COMMENT) = Aligner.topKBySrc(varNameAlignments, numAlignmentsSrcToComment.get)
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
  ): Map[String, Seq[Obj]] = {
    // Make Comment Spans from the comment variable mentions
    val linkElements = scala.collection.mutable.HashMap[String, Seq[Obj]]()

    if (commentDefinitionMentions.isDefined) {
      linkElements(COMMENT) = commentDefinitionMentions.get.map { commentMention =>
        mkLinkElement(
          elemType = "comment_span",
          source = commentMention.document.id.getOrElse("unk_file"),
          content = commentMention.arguments(DEFINITION).head.text,
          contentType = "null"
        )
      }
    }


    // Repeat for src code variables
    if (variableNames.isDefined) {
      linkElements(SOURCE) = variableNames.get.map { varName =>
        mkLinkElement(
          elemType = "identifier",
          source = varName.split("::")(1),
          content = varName,
          contentType = "null"
        )
      }
    }


    // Repeat for text variables
    if (textDefinitionMentions.isDefined) {
      linkElements(TEXT) = textDefinitionMentions.get.map { mention =>
        val docId = mention.document.id.getOrElse("unk_text_file")
        val sent = mention.sentence
        val offsets = mention.tokenInterval.toString()
        mkLinkElement(
          elemType = "text_span",
          source = s"${docId}_sent${sent}_$offsets",
          content = mention.arguments(DEFINITION).head.text,
          contentType = "null"
        )
      }
    }

    if (textDefinitionMentions.isDefined) {
      linkElements(TEXT_VAR) = textDefinitionMentions.get.map { mention =>
        val docId = mention.document.id.getOrElse("unk_text_file")
        val sent = mention.sentence
        val offsets = mention.tokenInterval.toString()
        mkTextLinkElement(
          elemType = "text_var",
          source = s"${docId}_sent${sent}_$offsets",
          content = mention.arguments(VARIABLE).head.text,
          contentType = "null",
          svoQueryTerms = SVOGrounder.getTerms(mention).getOrElse(Seq.empty)
        )
      }
    }


    // Repeat for Eqn Variables
    if (equationChunksAndSource.isDefined) {
      linkElements(EQUATION) = equationChunksAndSource.get.map { case (chunk, orig) =>
        mkLinkElement(
          elemType = "equation_span",
          source = orig,
          content = AlignmentBaseline.replaceGreekWithWord(chunk, greek2wordDict.toMap),
          contentType = "null"
        )
      }
    }


    linkElements.toMap
  }

  def mkLinkHypothesisTextVarDef(variables: Seq[Obj], definitions: Seq[Obj]): Seq[Obj] = {
    assert(variables.length == definitions.length)
    for {
      i <- variables.indices
    } yield mkHypothesis(variables(i), definitions(i), 1.0)
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

  def mkLinkHypotheses(groundings: Map[String, Seq[sparqlResult]]): Seq[Obj] = {

    //todo: groundings with Nones should not make it here
    logger.info("Making link hypotheses for svo groundings")
    println("groundings length: " + groundings.keys.toList.length)
    println(s"groundings inside mkling hypotheses: $groundings")
    val groundingObjects = for {
      //each grounding is a mapping from text variable to seq of possible svo groundings (as sparqlResults)
      v <- groundings.keys //variable
      gr <- groundings(v)
      //text link element//text link element
      srcLinkElement = mkLinkElement(
        elemType = "text_var",
        source = v match {
          case v if v.contains("::") => v.split("::").last
          case _ => "text_pdf"
        },
        content = v match {
          case v if v.contains("::") => v.split("::").head
          case _ => v
        }, //the variable associated with the definition that we used for grounding; if we get the variable from other link hypotheses, it also includes the name of the pdf it came from in this format <variable_name>::<source_pdf>; todo: include that info in the svo grounding endpoint? or is it already there?
        contentType = "null"
      )
      dstLinkElement = GrFNParser.mkSVOElement(gr)

    } yield mkHypothesis(srcLinkElement, dstLinkElement, gr.score.get)

//    println(s"grounding objects: ${groundingObjects.mkString(" || ")}")
    groundingObjects.toSeq
  }

  def getLinkHypotheses(linkElements: Map[String, Seq[Obj]], alignments: Map[String, Seq[Seq[Alignment]]]): Seq[Obj] = {//, SVOGroungings: Map[String, Seq[sparqlResult]]): Seq[Obj] = {

    // Store them all here
    val hypotheses = new ArrayBuffer[ujson.Obj]()
    val linkElKeys = linkElements.keys
    // Comment -> Text
    if (linkElKeys.toSeq.contains(COMMENT) && linkElKeys.toSeq.contains(TEXT)) {
      hypotheses.appendAll(mkLinkHypothesis(linkElements(COMMENT), linkElements(TEXT), alignments(COMMENT_TO_TEXT)))
    }

    // Src Variable -> Comment
    if (linkElKeys.toSeq.contains(SOURCE) && linkElKeys.toSeq.contains(COMMENT)) {
      hypotheses.appendAll(mkLinkHypothesis(linkElements(SOURCE), linkElements(COMMENT), alignments(SRC_TO_COMMENT)))
    }


    // Equation -> Text
    if (linkElKeys.toSeq.contains(EQUATION) && linkElKeys.toSeq.contains(TEXT)) {
      hypotheses.appendAll(mkLinkHypothesis(linkElements(EQUATION), linkElements(TEXT), alignments(EQN_TO_TEXT)))
    }

    // TextVar -> TextDef (text_span)
    if (linkElKeys.toSeq.contains(TEXT_VAR) && linkElKeys.toSeq.contains(TEXT)) {
      hypotheses.appendAll(mkLinkHypothesisTextVarDef(linkElements(TEXT_VAR), linkElements(TEXT)))
    }

    // Text -> SVO grounding
    // hypotheses.appendAll(mkLinkHypothesis(SVOGroungings))


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

    val textDefinitionMentions = if (loadMentions) {
      val mentionsFile = config[String]("apps.mentionsFile")
    JSONSerializer.toMentions(new File(mentionsFile)).filter(_.label matches "Definition")
    } else {
      val inputDir = config[String]("apps.inputDirectory")
      val inputType = config[String]("apps.inputType")
      val dataLoader = DataLoader.selectLoader(inputType) // txt, json (from science parse), pdf supported
      val files = FileUtils.findFiles(inputDir, dataLoader.extension)
      getTextDefinitionMentions(textReader, dataLoader, textRouter, files)
  //    val source = scala.io.Source.fromFile()
  //    val mentionsJson4s = json4s.jackson.parseJson(source.getLines().toArray.mkString(" "))
  //    source.close()

    }
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
      Some(commentDefinitionMentions),
      equationChunksAndSource,
      None, //not passing svo groundings from grfn
      groundToSVO: Boolean,
      maxSVOgroundingsPerVar: Int,
      alignmentHandler,
      Some(numAlignments),
      Some(numAlignments),
      scoreThreshold,
      appendToGrFN
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
