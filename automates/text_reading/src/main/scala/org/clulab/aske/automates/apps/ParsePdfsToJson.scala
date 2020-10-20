package org.clulab.aske.automates.apps

import java.io.File
import ai.lum.common.FileUtils._
import org.clulab.aske.automates.scienceparse.ScienceParseClient

object ParsePdfsToJson {

  def main(args: Array[String]): Unit = {

    // check arguments are correct
    if (args.length != 2) {
      sys.error("usage: program inputdir outputdir")
    }

    // parse arguments
    val inputDirectory = new File(args(0))
    val outputDirectory = new File(args(1))
    // FIXME read from somewhere
    val domain = "localhost"
    val port = "8080"

    // make output directory if needed
    if (!outputDirectory.exists()) {
      outputDirectory.mkdirs()
    }

    // connect to science-parse server
    val client = new ScienceParseClient(domain, port)

    // save json for each pdf file in input dir
    for (pdf <- inputDirectory.listFilesByWildcard("*.pdf")) {
      val json = client.parsePdfToJson(pdf)
      val basename = pdf.getBaseName()
      val outputFile = new File(outputDirectory, basename + ".json")
      outputFile.writeString(json)
    }

  }

}
