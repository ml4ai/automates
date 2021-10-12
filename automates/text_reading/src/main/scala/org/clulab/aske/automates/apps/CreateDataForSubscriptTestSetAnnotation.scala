package org.clulab.aske.automates.apps

import java.io.{BufferedWriter, File, FileWriter, PrintWriter}
import ai.lum.common.ConfigUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.aske.automates.data.{CosmosJsonDataLoader, DataLoader, TextRouter}
import org.clulab.aske.automates.OdinEngine
import org.clulab.aske.automates.apps.Subscripts.reader
import org.clulab.aske.automates.attachments.AutomatesAttachment
import org.clulab.aske.automates.serializer.AutomatesJSONSerializer
import org.clulab.utils.{FileUtils, Serializer}
import org.clulab.odin.Mention
import org.clulab.odin.serialization.json.JSONSerializer
import org.json4s.jackson.JsonMethods._

import scala.collection.mutable.ArrayBuffer

/**
  * App used to extract mentions from files in a directory and produce the desired output format (i.e., serialized
  * mentions or any other format we may need).  The input and output directories as well as the desired export
  * formats are specified in the config file (located in src/main/resources).
  * This makes ONE output file for each of the input files.
  */
object CreateDataForSubscriptTestSetAnnotation extends App {

  def getExporter(exporterString: String, filename: String): Exporter = {
    exporterString match {
      case "serialized" => SerializedExporter(filename)
      case "json" => AutomatesExporter(filename)
      case "tsv" => TSVExporter(filename)
      case _ => throw new NotImplementedError(s"Export mode $exporterString is not supported.")
    }
  }

  val config = ConfigFactory.load()

  val inputDir: String = "/Users/alexeeva/Desktop/automates-related/SuperMaaS-sept2021/cosmos-jsons-beautified"
  val outputDir: String = "/Users/alexeeva/Desktop/automates-related/subscriptsTestData/"
  val inputType = "json" //config[String]("apps.inputType")
  // if using science parse doc, uncomment next line and...
  //  val dataLoader = DataLoader.selectLoader(inputType) // pdf, txt or json are supported, and we assume json == science parse json
  //..comment out this line:
  val dataLoader = new CosmosJsonDataLoader
  val exportAs: List[String] = config[List[String]]("apps.exportAs")
  val files = FileUtils.findFiles(inputDir, dataLoader.extension)
  val reader = OdinEngine.fromConfig(config[Config]("TextEngine"))

  //uncomment these for using the text/comment router
//  val commentReader = OdinEngine.fromConfig(config[Config]("CommentEngine"))
//  val textRouter = new TextRouter(Map(TextRouter.TEXT_ENGINE -> reader, TextRouter.COMMENT_ENGINE -> commentReader))
  // For each file in the input directory:
  files.par.foreach { file =>
    // 1. Open corresponding output file and make all desired exporters
    println(s"Extracting from ${file.getName}")

    val pw = new PrintWriter(new File(outputDir + file.getName.replace(".json", "") + "_subscript_test_data.txt"))
    // 2. Get the input file contents
    // note: for science parse format, each text is a section
    val texts = dataLoader.loadFile(file).map(_.split("::").head)
    val sentences = new ArrayBuffer[String]()

    for (t <- texts) {
      val annotated = reader.annotate(t).sentences

      for (s <- annotated) {
        for (w <- s.words) {
          pw.write(w + "\t" + "O" + "\n")
        }
        pw.write("\n\n")
      }
    }



    pw.close()
  }
}
