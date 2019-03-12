package org.clulab.aske.automates.apps

import ai.lum.common.ConfigUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.aske.automates.{DataLoader, OdinEngine}
import org.clulab.processors.Document
import org.clulab.utils.FileUtils

object ExtractAndAlign {

  def parseCommentText(text: String, filename: Option[String] = None): Document = {
    // todo: make sure that the filename gets stored as the doc.id
    ???
  }


  def main(args: Array[String]): Unit = {
    val config = ConfigFactory.load("automates")

    // Instantiate the text reader
    val textReader = OdinEngine.fromConfig(config[Config]("TextEngine"))

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
      // Parse the comment texts
      // todo!!
      val docs = texts.map(parseCommentText(_, filename = Some(file.getName)))
      docs.flatMap(textReader.extractFrom)
    }

//    // Align
//    // todo
//    val aligner = Aligner.fromConfig(config[Config]("alignment"))
//    val alignment = aligner.alignSources(textMentions.seq, commentMentions.seq)
//
//    // Export alignment
//    val outputDir = config[String]("apps.outputDirectory")
//    // todo

  }
}
