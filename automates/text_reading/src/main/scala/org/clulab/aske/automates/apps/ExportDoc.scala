package org.clulab.aske.automates.apps
import org.clulab.serialization.json._
import java.io.File
import java.io.FileWriter
import java.io.BufferedWriter
import org.clulab.processors.fastnlp.FastNLPProcessor

import ai.lum.common.ConfigUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.aske.automates.data.DataLoader
import org.clulab.aske.automates.OdinEngine
import org.clulab.utils.FileUtils

import org.clulab.serialization.DocumentSerializer

/**
  * App used to create and export serialized json file of the processors Document
  * todo: pass file names from config
  * This makes ONE output file for each of the input files.
  */
object ExportDoc extends App {

  def getExporter(exporterString: String, filename: String): Exporter = {
    exporterString match {
      case "serialized" => SerializedExporter(filename)
      case "json" => JSONExporter(filename)
      case _ => throw new NotImplementedError(s"Export mode $exporterString is not supported.")
    }
  }

  val config = ConfigFactory.load()
  val inputDir = config[String]("apps.inputDirectory")
  val outputDir = config[String]("apps.outputDirectory")
  val inputType = config[String]("apps.inputType")
  val dataLoader = DataLoader.selectLoader(inputType) // pdf, txt or json are supported, and we assume json == science parse json
  val exportAs: List[String] = config[List[String]]("apps.exportAs")
  val files = FileUtils.findFiles(inputDir, dataLoader.extension)
  val reader = OdinEngine.fromConfig(config[Config]("TextEngine"))
  val proc = new FastNLPProcessor()
  val serializer = new DocumentSerializer
  val exporter = new JSONDocExporter()


  // For each file in the input directory:
  files.foreach { file =>
    // 1. Open corresponding output file and make all desired exporters
    println(s"Extracting from ${file.getName}")
    // 2. Get the input file contents
    //here, for the science parse texts, we join all the sections to produce the Document of the whole paper
    val text = dataLoader.loadFile(file).mkString(" ")
    val document = proc.annotate(text)
    //jsonify the Document
    val json = document.json(pretty = true)
    //replace the file name with the name that indicates it has been serialized; todo: need a better way to indictae the target dir
    val newFileName = file.toString().replace(".json", "_seralizedDoc")
    exporter.export(json, newFileName)


  }
}

case class JSONDocExporter()  {
  def export(str: String, filename: String): Unit = {

    val file = new File(filename + ".json")
    val bw = new BufferedWriter(new FileWriter(file))
    bw.write(str)
    bw.close()
  }

  def close(): Unit = ()
}