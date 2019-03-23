package org.clulab.aske.automates.apps

import java.io.{File, PrintWriter}

import ai.lum.common.ConfigUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.aske.automates.alignment.Aligner
import org.clulab.aske.automates.entities.StringMatchEntityFinder
import org.clulab.aske.automates.grfn.{GrFNDocument, GrFNParser}
import org.clulab.aske.automates.{DataLoader, OdinEngine}
import org.clulab.processors.Document
import org.clulab.processors.fastnlp.FastNLPProcessor
import org.clulab.utils.{DisplayUtils, FileUtils}
import org.slf4j.LoggerFactory

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
    val doc = proc.annotate(lines_combined.mkString(". "), keepText = true)
    doc.id = filename
    doc
  }


  def main(args: Array[String]): Unit = {
    val config: Config = ConfigFactory.load("automates")

    // Instantiate the text reader
    val textconfig: Config = config[Config]("TextEngine")
    val textReader = OdinEngine.fromConfig(textconfig)

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
      val texts = dataLoader.loadFile(file)
      texts.flatMap(textReader.extractFromText(_, filename = Some(file.getName)))
    }
    println(s"Extracted ${textMentions.length} text mentions")

    // Instantiate the comment reader
    val commentReader = OdinEngine.fromConfig(config[Config]("CommentEngine"))

    // Load the comment input from directory/file
    val commentInputDir = config[String]("apps.commentInputDirectory")
    val commentInputType = config[String]("apps.commentInputType")
    val commentDataLoader = DataLoader.selectLoader(commentInputType) // txt, json (science parse) supported
    val commentFiles = FileUtils.findFiles(commentInputDir, commentDataLoader.extension)


    // Get the Variable names from the GrFn
    val grfnFile: String = config[String]("apps.grfnFile") // fixme (Becky): extend to a dir later
    val grfn = GrFNParser.mkDocument(new File(grfnFile))
    val grfnVars = GrFNDocument.getVariables(grfn)
    val variableNames = grfnVars.map(_.name.toUpperCase) // fixme: are all the variables uppercase?
    logger.info(s"Found GrFN Variables: ${variableNames.mkString(", ")}")

    // Make a StringMatchEF based on the variable names
    val stringMatcher = StringMatchEntityFinder.fromStrings(variableNames, "Variable") // todo: GrFNVariable?


    // Read the comments
    // todo: not parallel because I am resetting the initial state... I could have one reader per thread though...?
    val commentMentions = commentFiles.flatMap { file =>
      // Open corresponding output file and make all desired exporters
      println(s"Extracting from ${file.getName}")
      // Get the input file contents, note: for science parse format, each text is a section
      val texts = commentDataLoader.loadFile(file)
      //println("TEXTS: " + texts.length)
      // Parse the comment texts
      // todo!!
      val docs = texts.map(parseCommentText(_, filename = Some(file.getName)))
      // Iterate through the docs and find the mentions
      val mentions = for {
        doc <- docs
        // Find occurrences of the GrFN Variables
        foundGrFNVars = stringMatcher.extract(doc)
      } yield commentReader.extractFrom(doc, foundGrFNVars)
//      for (m <- mentions) {
//        println("-->", m.mkString(" "))
//      }

      mentions.flatten
    }

    // Align
    val aligner = Aligner.fromConfig(config[Config]("alignment"))
    val variableMentions = textMentions.seq.filter(_ matches "Definition")
    // ----------------------------------
    val pw = new PrintWriter("./output/definitions.txt")  ///../../../../../../../../ExtractAndAlign.scala
    for (m <- variableMentions) {
      pw.println("**************************************************")
      pw.println("count: " + variableMentions.indexOf(m))
      pw.println(m.sentenceObj.getSentenceText)
      DisplayUtils.printMention(m, pw)
      pw.println("")
    }
    pw.close()

    // ----------------------------------
    val alignments = aligner.alignMentions(variableMentions, commentMentions)
    alignments.foreach{ a =>
      val v1Text = variableMentions(a.src).text
      val v2Text = commentMentions(a.dst).text
      println(s"text: ${v1Text}")
      println(s"comment: ${v2Text}")
      println(s"score: ${a.score}\n")
    }

    // Export alignment
    val outputDir = config[String]("apps.outputDirectory")
    // todo

  }
}
