package org.clulab.aske.automates.apps

import java.io.{BufferedWriter, File, FileWriter, PrintWriter}
import ai.lum.common.ConfigUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.aske.automates.data.{CosmosJsonDataLoader, DataLoader, TextRouter}
import org.clulab.aske.automates.OdinEngine
import org.clulab.aske.automates.apps.ExtractAndAlign.{getGlobalVars, returnAttachmentOfAGivenTypeOption}
import org.clulab.aske.automates.attachments.{AutomatesAttachment, MentionLocationAttachment}
import org.clulab.aske.automates.cosmosjson.CosmosJsonProcessor
import org.clulab.aske.automates.mentions.CrossSentenceEventMention
import org.clulab.aske.automates.serializer.AutomatesJSONSerializer
import org.clulab.utils.{DisplayUtils, FileUtils, Serializer}
import org.clulab.odin.Mention
import org.clulab.odin.serialization.json.JSONSerializer
import org.clulab.utils.AlignmentJsonUtils.GlobalVariable
import org.clulab.utils.MentionUtils.{getMentionsWithLocations, getMentionsWithoutLocations}
import org.json4s.jackson.JsonMethods._

import scala.collection.mutable.ArrayBuffer

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

  val numOfWikiGroundings: Int = config[Int]("apps.numOfWikiGroundings")
  val inputDir: String = config[String]("apps.inputDirectory")
  val outputDir: String = config[String]("apps.outputDirectory")
  val inputType: String = config[String]("apps.inputType")
  val dataLoader = DataLoader.selectLoader(inputType) // pdf, txt or json are supported, and we assume json == cosmos json; to use science parse. comment out this line and uncomment the next one
  //  val dataLoader = new ScienceParsedDataLoader
  val exportAs: List[String] = config[List[String]]("apps.exportAs")
  val files = FileUtils.findFiles(inputDir, dataLoader.extension)
  val readerType: String = config[String]("ReaderType")
  val reader = OdinEngine.fromConfig(config[Config](readerType))

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
    val mentions = if (file.getName.contains("COSMOS")) {
      // cosmos json
      getMentionsWithLocations(texts, file, reader)
    } else {
      // other file types---those don't have locations
      getMentionsWithoutLocations(texts, file, reader)
    }
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

    val exportGlobalVars = false
    if (exportGlobalVars) {
      val exporter = GlobalVarTSVExporter(file.getAbsolutePath, numOfWikiGroundings)
      val globalVars = getGlobalVars(descrMentions, None, true)

      exporter.export(globalVars)
    }


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
    println("Unit mentions: ")
    for (m <- unitMentions) {
      println("----------------")
      println(m.text)
      //      println(m.foundBy)
      for (arg <- m.arguments) {
        println(arg._1 + ": " + m.arguments(arg._1).head.text)
      }
    }


    val contextMentions = mentions.filter(_ matches "Context")
    println("Context setting mentions: ")
    for (m <- contextMentions) {
      println("----------------")
      println(m.text)
      //      println(m.foundBy)
      for (arg <- m.arguments) {
        println(arg._1 + ": " + m.arguments(arg._1).head.text)
      }
    }

    // 4. Export to all desired formats
    exportAs.foreach { format =>
      val exporter = getExporter(format, s"$outputDir/${file.getName.replace("." + inputType, s"_mentions.${format}")}")
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
    val pw = new PrintWriter(new File(filename.toString()))
    pw.write("filename\tsentence\tmention type\tfound by\tmention text\tlocation in the pdf\targs in all next columns\n")
    val contentMentions = mentions.filter(m => (m.label matches "Description") || (m.label matches "ParameterSetting") || (m.label matches "IntervalParameterSetting") || (m.label matches "UnitRelation") || (m.label matches "Command") || (m.label matches "Date") || (m.label matches "Location") || m.label.contains("Model")) //|| (m.label matches "Context"))

    for (m <- contentMentions) {
      val locationMention = returnAttachmentOfAGivenTypeOption(m.attachments, "MentionLocation").get.toUJson.obj
      pw.write(contentMentions.head.document.id.getOrElse("unk_file") + "\t")
      pw.write(m.sentenceObj.words.mkString(" ").replace("\t", "").replace("\n","") + "\t" + 
        m.label + "\t" + m.foundBy + "\t" + m.text.trim().replace("\t", "").replace("\n","") + "\t" + "page:" + locationMention("pageNum").arr.mkString(",") + " block:" +  locationMention("blockIdx").arr.mkString(","))
      for (arg <- m.arguments) {
        if (arg._2.nonEmpty) {
          pw.write("\t" + arg._1 + ": " + arg._2.map(_.text.trim().replace("\t", "").replace("\n","")).mkString("::"))
        }
      }
      pw.write("\n")
    }
    pw.close()
  }

  override def close(): Unit = ()
}

case class GlobalVarTSVExporter(filename: String, numOfWikiGroundings: Int){
  def export(glvars: Seq[GlobalVariable]): Unit = {
    val pw = new PrintWriter(new File(filename.toString().replace(".json", "_descr_mentions_with_wiki_groundings.tsv") ))
    pw.write("variable\tdescriptions")
    for (i <- 0 to numOfWikiGroundings) {
      pw.write("\tgrounding\tsubclassOf")
    }
    pw.write("\n")

    for (m <- glvars) {
      pw.write(m.identifier + "\t" + m.textFromAllDescrs.mkString("::"))
      if (m.groundings.isDefined && m.groundings.get.nonEmpty) {
        for (g <- m.groundings.get) {
          pw.write("\t" + g.conceptID + "::" + g.conceptLabel)
          pw.write("\t" + g.subClassOf.getOrElse("No subclass"))
        }
      }
      pw.write("\n")

    }
    pw.close()
  }

  def close(): Unit = ()
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