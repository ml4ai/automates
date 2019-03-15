package org.clulab.aske.automates.apps

import ai.lum.common.ConfigUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.aske.automates.alignment.Aligner
import org.clulab.aske.automates.{DataLoader, OdinEngine}
import org.clulab.processors.Document
import org.clulab.processors.fastnlp.FastNLPProcessor
import org.clulab.utils.FileUtils


import scala.io.Source

object ExtractAndAlign {

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

    // Instantiate the comment reader
    val commentReader = OdinEngine.fromConfig(config[Config]("CommentEngine"))

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
      val texts = dataLoader.loadFile(file)
      println("TEXTS: " + texts.length)
      // Parse the comment texts
      // todo!!
      val docs = texts.map(parseCommentText(_, filename = Some(file.getName)))
      docs.flatMap(commentReader.extractFrom)
    }

    // Align
    val aligner = Aligner.fromConfig(config[Config]("alignment"))
    val alignments = aligner.alignMentions(textMentions.seq, commentMentions.seq)

    // Export alignment
    val outputDir = config[String]("apps.outputDirectory")
    // todo

  }
}
