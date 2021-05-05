package org.clulab.aske.automates.apps

import java.io.{BufferedWriter, File, FileWriter, PrintWriter}

import ai.lum.common.ConfigUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.aske.automates.data.{DataLoader, TextRouter}
import org.clulab.aske.automates.OdinEngine
import org.clulab.aske.automates.attachments.AutomatesAttachment
import org.clulab.aske.automates.serializer.AutomatesJSONSerializer
import org.clulab.utils.{DisplayUtils, FileUtils, Serializer}
import org.clulab.odin.Mention
import org.clulab.odin.serialization.json.JSONSerializer
import org.json4s
import org.json4s.jackson.JsonMethods._

/**
  * App used to extract mentions from files in a directory and produce the desired output format (i.e., serialized
  * mentions or any other format we may need).  The input and output directories as well as the desired export
  * formats are specified in the config file (located in src/main/resources).
  * This makes ONE output file for each of the input files.
  */
object ExtractAndExport extends App {

  def getExporter(exporterString: String, filename: String): Exporter = {
    exporterString match {
      case "serialized" => SerializedExporter(filename)
      case "json" => AutomatesExporter(filename)
      case "tsv" => TSVExporter(filename)
      case _ => throw new NotImplementedError(s"Export mode $exporterString is not supported.")
    }
  }

  val config = ConfigFactory.load()

  val inputDir = "/media/alexeeva/ee9cacfc-30ac-4859-875f-728f0764925c/storage/automates-related/TR-20201013T173400Z-001/TR/chime"
  val outputDir = "/media/alexeeva/ee9cacfc-30ac-4859-875f-728f0764925c/storage/automates-related/TR-20201013T173400Z-001/TR/chime/mentions"
  val inputType = config[String]("apps.inputType")
  val dataLoader = DataLoader.selectLoader(inputType) // pdf, txt or json are supported, and we assume json == science parse json
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
    // 2. Get the input file contents
    // note: for science parse format, each text is a section
    val texts = dataLoader.loadFile(file)
    // 3. Extract causal mentions from the texts
    // todo: here I am choosing to pass each text/section through separately -- this may result in a difficult coref problem
    val mentions = texts.flatMap(reader.extractFromText(_, filename = Some(file.getName)))
    //The version of mention that includes routing between text vs. comment
//    val mentions = texts.flatMap(text => textRouter.route(text).extractFromText(text, filename = Some(file.getName))).seq
//    for (m <- mentions) {
//      println("----------------")
//      println(m.text)
//
//      if (m.arguments.nonEmpty) {
//        for (arg <- m.arguments) {
//          println("arg: " + arg._1 + ": " + m.arguments(arg._1).head.text)
//        }
//      }
//
//    }
    val descrMentions = mentions.filter(_ matches "Description")

    println("Description mentions: ")
    for (dm <- descrMentions) {
      println("----------------")
      println(dm.text)
//      println(dm.foundBy)
      for (arg <- dm.arguments) {
        println(arg._1 + ": " + dm.arguments(arg._1).head.text)
      }
      if (dm.attachments.nonEmpty) {
        for (att <- dm.attachments) println("att: " + att.asInstanceOf[AutomatesAttachment].toUJson)
      }
    }
    val paramSettingMentions = mentions.filter(_ matches "ParameterSetting")



    println("\nParam setting mentions: ")
    for (m <- paramSettingMentions) {
      println("----------------")
      println(m.text)
//      println(m.foundBy)
      for (arg <- m.arguments) {
        println(arg._1 + ": " + m.arguments(arg._1).head.text)
      }
    }
    val unitMentions = mentions.filter(_ matches "UnitRelation")
    println("Unit setting mentions: ")
    for (m <- unitMentions) {
      println("----------------")
      println(m.text)
//      println(m.foundBy)
      for (arg <- m.arguments) {
        println(arg._1 + ": " + m.arguments(arg._1).head.text)
      }
    }

    // 4. Export to all desired formats
    exportAs.foreach { format =>
        val exporter = getExporter(format, s"$outputDir/${file.getName}")
        exporter.export(mentions)
        exporter.close() // close the file when you're done
    }
  }
}

trait Exporter {
  def export(mentions: Seq[Mention]): Unit
  def close(): Unit // for closing the file, if needed
}


case class SerializedExporter(filename: String) extends Exporter {
  override def export(mentions: Seq[Mention]): Unit = {
    Serializer.save[SerializedMentions](new SerializedMentions(mentions), filename + ".serialized")
  }

  override def close(): Unit = ()
}

case class JSONExporter(filename: String) extends Exporter {
  override def export(mentions: Seq[Mention]): Unit = {
    val ast = JSONSerializer.jsonAST(mentions)
    val text = compact(render(ast))
    val file = new File(filename + ".json")
    val bw = new BufferedWriter(new FileWriter(file))
    bw.write(text)
    bw.close()
  }

  override def close(): Unit = ()
}

case class AutomatesExporter(filename: String) extends Exporter {
  override def export(mentions: Seq[Mention]): Unit = {
    val serialized = ujson.write(AutomatesJSONSerializer.serializeMentions(mentions))
//    val groundingsJson4s = json4s.jackson.prettyJson(json4s.jackson.parseJson(serialized))
    val file = new File(filename)
    val bw = new BufferedWriter(new FileWriter(file))
    bw.write(serialized)
    bw.close()
  }

  override def close(): Unit = ()
}


// used to produce tsv files with extracted mentions; add 'tsv' to the list of foramats under apps.exportAs in application.conf; change m.label filtering to whatever type of event you are interested in.
case class TSVExporter(filename: String) extends Exporter {
  override def export(mentions: Seq[Mention]): Unit = {
    val pw = new PrintWriter(new File(filename.toString().replace(".json", "_mentions.tsv") ))
    val contentMentions = mentions.filter(m => (m.label matches "Description") || (m.label matches "ParameterSetting") || (m.label matches "IntervalParameterSetting"))
    for (m <- contentMentions) {
      pw.write(m.label + "\t" + m.text.trim())
      for (arg <- m.arguments) pw.write("\t" + arg._1 + ": " + arg._2.head.text.trim())
      pw.write("\n")
    }
    pw.close()
  }

  override def close(): Unit = ()
}

// Helper Class to facilitate serializing the mentions
@SerialVersionUID(1L)
class SerializedMentions(val mentions: Seq[Mention]) extends Serializable {}
object SerializedMentions {
  def load(file: File): Seq[Mention] = Serializer.load[SerializedMentions](file).mentions
  def load(filename: String): Seq[Mention] = Serializer.load[SerializedMentions](filename).mentions
}


object ExporterUtils {

  def removeTabAndNewline(s: String) = s.replaceAll("(\\n|\\t)", " ")
}
