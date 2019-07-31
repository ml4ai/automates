package org.clulab.aske.automates.apps

import java.io.{File, PrintWriter}

import ai.lum.common.ConfigUtils._
import ai.lum.common.FileUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.aske.automates.data.{DataLoader, TextRouter}
import org.clulab.aske.automates.alignment.{Aligner, Alignment, VariableEditDistanceAligner}
import org.clulab.aske.automates.entities.StringMatchEntityFinder
import org.clulab.aske.automates.grfn._
import org.clulab.aske.automates.OdinEngine
import org.clulab.processors.Document
import org.clulab.processors.fastnlp.FastNLPProcessor
import org.clulab.utils.{DisplayUtils, FileUtils}
import org.slf4j.LoggerFactory
import upickle.default._

import scala.io.Source

object ExtractAndAlign {

  val logger = LoggerFactory.getLogger(this.getClass())

  def ltrim(s: String): String = s.replaceAll("^\\s*[C!]?[-=]*\\s{0,5}", "")

  def parseCommentText(text: String, filename: Option[String] = None): Document = {
    val proc = new FastNLPProcessor()
    //val Docs = Source.fromFile(filename).getLines().mkString("\n")
    val lines = for (sent <- text.split("\n") if ltrim(sent).length > 1) yield ltrim(sent)
    var lines_combined = Array[String]()
    // which lines we want to ignore (for now, may change later)
    val ignoredLines = "(^Function:|^Calculates|^Calls:|^Called by:|([\\d\\?]{1,2}\\/[\\d\\?]{1,2}\\/[\\d\\?]{4})|REVISION|head:|neck:|foot:|SUBROUTINE|Subroutine|VARIABLES)".r

    for (line <- lines if ignoredLines.findAllIn(line).isEmpty) {
      if (line.startsWith(" ")) {
        var prevLine = lines(lines.indexOf(line)-1)
        if (lines_combined.contains(prevLine)) {
          prevLine = prevLine + " " + ltrim(line)
          lines_combined = lines_combined.slice(0, lines_combined.length-1)
          lines_combined = lines_combined :+ prevLine
        }
      }
      else {
        if (!lines_combined.contains(line)) {
          lines_combined = lines_combined :+ line
        }
      }
    }
    for (line <- lines_combined) {
      println(line)
    }
    println("-->" + lines_combined.length)
    val doc = proc.annotateFromSentences(lines_combined, keepText = true)
    doc.id = filename
    doc
  }


  def main(args: Array[String]): Unit = {
    val config: Config = ConfigFactory.load("automates")

    // Instantiate the text reader
    val textconfig: Config = config[Config]("TextEngine")
    val textReader = OdinEngine.fromConfig(textconfig)
    // Instantiate the comment reader
    val commentReader = OdinEngine.fromConfig(config[Config]("CommentEngine"))
    // todo: future readers
//    val glossaryReader = OdinEngine.fromConfig(config[Config]("GlossaryEngine"))
//    val tocReader = OdinEngine.fromConfig(config[Config]("TableOfContentsEngine"))
    val textRouter = new TextRouter(Map(TextRouter.TEXT_ENGINE -> textReader, TextRouter.COMMENT_ENGINE -> commentReader))

    // Load text input from directory
    val inputDir = config[String]("apps.inputDirectory")
    val inputType = config[String]("apps.inputType")
    val dataLoader = DataLoader.selectLoader(inputType) // txt, json (science parse) supported
    val files = FileUtils.findFiles(inputDir, dataLoader.extension)

    // Read the text
    val textMentions = files.par.flatMap { file =>
      // Open corresponding output file and make all desired exporters
      println(s"Extracting from ${file.getName}")
      // Get the input file contents, note: for science parse format, each text is a section
      val texts: Seq[String] = dataLoader.loadFile(file)
      // Route text based on the amount of sentence punctuation and the # of numbers (too many numbers = non-prose from the paper)
      texts.flatMap(text => textRouter.route(text).extractFromText(text, filename = Some(file.getName)))
    }
    println(s"Extracted ${textMentions.length} text mentions")


    // todo: We probably want a separate comment reader for each model....? i.e. PETPT vs PETASCE



    // Load the comment input from directory/file
    val commentInputDir = config[String]("apps.commentInputDirectory")
    val commentInputType = config[String]("apps.commentInputType")
    val commentDataLoader = DataLoader.selectLoader(commentInputType) // txt, json (science parse) supported
    val commentFiles = FileUtils.findFiles(commentInputDir, commentDataLoader.extension)

    // Read the comments
    val commentMentions = commentFiles.par.flatMap { file =>
      // Open corresponding output file and make all desired exporters
      println(s"Extracting from ${file.getName}")
      // Get the input file contents, note: for science parse format, each text is a section
      val texts = commentDataLoader.loadFile(file)
      // Parse the comment texts
      val docs = texts.map(parseCommentText(_, filename = Some(file.getName)))

      // Iterate through the docs and find the mentions
      val mentions = docs.map(doc => commentReader.extractFrom(doc))

      mentions.flatten
    }

    // Grfn
    val grfnFile: String = config[String]("apps.grfnFile") // fixme (Becky): extend to a dir later?
    val grfn = GrFNParser.mkDocument(new File(grfnFile))
    val grfnVars = GrFNDocument.getVariables(grfn)
    val variableNames = grfnVars.map(_.name.toUpperCase) // fixme: are all the variables uppercase?

    // Align the comment definitions to the GrFN variables
    val numAlignments = config[Int]("apps.numAlignments")
    val commentDefinitionMentions = commentMentions.seq.filter(_ matches "Definition")
    val variableNameAligner = new VariableEditDistanceAligner(Set("variable"))

    val varNameAlignments = variableNameAligner.alignTexts(variableNames, commentDefinitionMentions.map(Aligner.getRelevantText(_, Set("variable"))))
    val top1ByVariableName = Aligner.topKBySrc(varNameAlignments, 1)


    // Align the comment definitions to the text definitions
    val w2vAligner = Aligner.fromConfig(config[Config]("alignment"))
    val textDefinitionMentions = textMentions.seq.filter(_ matches "Definition")

    // ----------------------------------
    // Debug:
//    val pw = new PrintWriter("./output/definitions.txt")  ///../../../../../../../../ExtractAndAlign.scala
//    for (m <- textDefinitionMentions) {
//      pw.println("**************************************************")
//      pw.println(m.sentenceObj.getSentenceText)
//      DisplayUtils.printMention(m, pw)
//      pw.println("")
//    }
//    pw.close()
    // ----------------------------------
    // Generates (src idx, dst idx, score tuples) -- exhaustive
    val commentToTextAlignments: Seq[Alignment] = w2vAligner.alignMentions(commentDefinitionMentions, textDefinitionMentions)
    val scoreThreshold = config[Double]("apps.commentTextAlignmentScoreThreshold")
    // group by src idx, and keep only top k (src, dst, score) for each src idx
    val topKAlignments: Seq[Seq[Alignment]] = Aligner.topKBySrc(commentToTextAlignments, numAlignments, scoreThreshold)


    // ----------------------------------
    // Debug:
    topKAlignments.foreach { aa =>
      println("====================================================================")
      println(s"              SRC VAR: ${commentDefinitionMentions(aa.head.src).arguments("variable").head.text}")
      println("====================================================================")
      aa.foreach { topK =>
        val v1Text = commentDefinitionMentions(topK.src).text
        val v2Text = textDefinitionMentions(topK.dst).text
        println(s"aligned variable (comment): ${commentDefinitionMentions(topK.src).arguments("variable").head.text}")
        println(s"aligned variable (text): ${textDefinitionMentions(topK.dst).arguments("variable").head.text}")
        println(s"comment: ${v1Text}")
        println(s"text: ${v2Text}")
        println(s"score: ${topK.score}\n")
      }
    }
    // ----------------------------------

    // Export alignment:
    val outputDir = config[String]("apps.outputDirectory")

    // Map the Comment Variables (from Definition Mentions) to a Seq[GrFNVariable]
    val commentGrFNVars = commentDefinitionMentions.map{ commentDef =>
      val name = commentDef.arguments("variable").head.text + "_COMMENT"
      val domain = "COMMENT"
      val definition = commentDef.arguments("definition").head.text
      val provenance = GrFNProvenance(definition, commentDef.document.id.getOrElse("COMMENT-UNK"), commentDef.sentence)
      GrFNVariable(name, domain, Some(provenance))
    }
    // Map the Text Variables (from Definition Mentions) to a Seq[GrFNVariable]
    val textGrFNVars = textDefinitionMentions.map{ textDef =>
      val name = textDef.arguments("variable").head.text + "_TEXT"
      val domain = "TEXT"
      val definition = textDef.arguments("definition").head.text
      val provenance = GrFNProvenance(definition, textDef.document.id.getOrElse("TEXT-UNK"), textDef.sentence)
      GrFNVariable(name, domain, Some(provenance))
    }
    // All final GrFN variables
    val topLevelVariables = grfnVars ++ commentGrFNVars ++ textGrFNVars

    // Gather the alignments from src variable to comment definition
    // srcSet is the sorted group of alignments for a particular src variable
    val srcVarToCommentGrFNAlignments = top1ByVariableName.flatMap { srcSet =>
      srcSet.map(a => mkGrFNAlignment(a, grfnVars, commentGrFNVars))
    }
    // Gather the alignments from comment definition to text definition
    // srcSet is the sorted group of alignments for a particular src variable
    val commentToTextGrFNAlignments = topKAlignments.flatMap { srcSet =>
      srcSet.map(a => mkGrFNAlignment(a, commentGrFNVars, textGrFNVars))
    }
    // All final alignments
    val topLevelAlignments = srcVarToCommentGrFNAlignments ++ commentToTextGrFNAlignments

    val grfnToExport = GrFNDocument(grfn.functions, grfn.start, grfn.name, grfn.dateCreated, Some(topLevelVariables), Some(topLevelAlignments))
    val grfnBaseName = new File(grfnFile).getBaseName()
    val grfnWriter = new PrintWriter(s"$outputDir/${grfnBaseName}_with_alignments.json")
    grfnWriter.println(write(grfnToExport))
    grfnWriter.close()
  }

  def mkGrFNAlignment(a: Alignment, srcs: Seq[GrFNVariable], dsts: Seq[GrFNVariable]): GrFNAlignment = {
    val srcVar = srcs(a.src).name
    val dstVar = dsts(a.dst).name
    val score = a.score
    GrFNAlignment(srcVar, dstVar, score)
  }
}
