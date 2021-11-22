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
import org.clulab.utils.{FileUtils, Serializer}
import org.clulab.odin.{EventMention, Mention}
import org.clulab.odin.serialization.json.JSONSerializer
import org.clulab.utils.AlignmentJsonUtils.GlobalVariable
import org.json4s.jackson.JsonMethods._

import scala.collection.mutable.ArrayBuffer

/**
  * App used to extract mentions from files in a directory and produce the desired output format (i.e., serialized
  * mentions or any other format we may need).  The input and output directories as well as the desired export
  * formats are specified in the config file (located in src/main/resources).
  * This makes ONE output file for each of the input files.
  */
object ExtractAndAssembleMentionEvents extends App {

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

  def getMentionsWithoutLocations(texts: Seq[String], file: File): Seq[Mention] = {
    // this is for science parse
    texts.flatMap(t => reader.extractFromText(t, filename = Some(file.getName)))
  }

  def getMentionsWithLocations(texts: Seq[String], file: File): Seq[Mention] = {
    // this is for cosmos jsons
    val textsAndFilenames = texts.map(_.split("<::>").slice(0,2).mkString("<::>"))
    val locations = texts.map(_.split("<::>").takeRight(2).mkString("<::>")) //location = pageNum::blockIdx
    val mentions = for (tf <- textsAndFilenames) yield {
      val Array(text, filename) = tf.split("<::>")
      reader.extractFromText(text, keepText = true, Some(filename))
    }
    // store location information from cosmos as an attachment for each mention
    val menWInd = mentions.zipWithIndex
    val mentionsWithLocations = new ArrayBuffer[Mention]()
    for (tuple <- menWInd) {
      // get page and block index for each block; cosmos location information will be the same for all the mentions within one block
      val menInTextBlocks = tuple._1
      val id = tuple._2
      val location = locations(id).split("<::>").map(loc => loc.split(",").map(_.toInt)) //(_.toDouble.toInt)
      val pageNum = location.head
      val blockIdx = location.last

      for (m <- menInTextBlocks) {
        val newAttachment = new MentionLocationAttachment(file.getName, pageNum, blockIdx, "MentionLocation")
        val newMen = m match {
          case m: CrossSentenceEventMention => m.asInstanceOf[CrossSentenceEventMention].newWithAttachment(newAttachment)
          case _ => m.withAttachment(newAttachment)
        }
        mentionsWithLocations.append(newMen)
      }
    }
    mentionsWithLocations
  }

  files.par.foreach { file =>
    // 1. Open corresponding output file and make all desired exporters
    println(s"Extracting from ${file.getName}")
    // 2. Get the input file contents
    // note: for science parse format, each text is a section
    val texts = dataLoader.loadFile(file)


    // todo: make a json with things like "models": [{name: Blah, descr: Blah}], countries: {}, dates: {can I also get the event here? maybe with my new found previously found mention as a trigger power?}, params: {vars from units, param settings, and descriptions}, model_info: {model descr, model limitation, etc}, param settings and units --- method to combine units and param setting based on var overlap
    val obj = ujson.Obj()
    obj("file_name") = file.getName
    // 3. Extract causal mentions from the texts
    val mentions = if (file.getName.contains("COSMOS")) {
      // cosmos json
      getMentionsWithLocations(texts, file)
    } else {
      // other file types---those don't have locations
      getMentionsWithoutLocations(texts, file)
    }

    val groupedByLabel = mentions.groupBy(_.label)//.filter(_._1 == "Location")
    for (g <- groupedByLabel) {
      println(g._1.toUpperCase)
      for (m <- g._2) {
        println(m.text + " " + m.label + " " + m.foundBy + " " + m.attachments)
      }
    }

    for (g <- groupedByLabel) {
      g._1 match {
        case "ModelDescr" => {
          val modelObjs = new ArrayBuffer[ujson.Value]()
          for (m <- g._2) {
            val trigger = m match {
              case csem: CrossSentenceEventMention => csem.trigger.text
              case em: EventMention => em.trigger.text
              case _ => null
            }

            def getSource(m: Mention, filename: String): ujson.Value = {
              val source = returnAttachmentOfAGivenTypeOption(m.attachments, "MentionLocation")
              println("SOURCE: " + source)
              val sourceJson = ujson.Obj()
              if (source.isDefined) {
                val sourceAsJson = source.get.toUJson
                sourceJson("page") = sourceAsJson("pageNum")
                sourceJson("blockIdx") = sourceAsJson("blockIdx")
              }
              sourceJson("filename") = filename
              sourceJson
            }
            val source = getSource(m, file.getName)
            val oneModel = ujson.Obj(
              "name" -> m.arguments("modelName").head.text,
              "description" -> m.arguments("modelDescr").head.text,
              "trigger" -> trigger,
              "source" -> source
            )
            modelObjs.append(oneModel)
          }
          obj("models") = ujson.Obj("descriptions" -> modelObjs)
        }
        case "ModelLimitation" => {
          val modelObjs = new ArrayBuffer[ujson.Value]()
          for (m <- g._2) {
            val trigger = m match {
              case csem: CrossSentenceEventMention => csem.trigger.text
              case em: EventMention => em.trigger.text
              case _ => null
            }
            val oneModel = ujson.Obj(
              "name" -> m.arguments("modelName").head.text,
              "limitation" -> m.arguments("modelDescr").head.text,
              "trigger" -> trigger

            )
            modelObjs.append(oneModel)
          }
          obj("models")("limitations") = modelObjs
        }
        case "ParamAndUnit" => {
          val paramUnitObjs = new ArrayBuffer[ujson.Value]()
          for (m <- g._2) {
            println("men: " + m.text + " " + m.label)
            if (m.arguments.keys.toList.contains("value") & m.arguments.keys.toList.contains("unit")) {
//              println("m: " + m.text + " " + m.label)
//              println("args: " + m.arguments.keys.mkString("|"))
              val oneVar = ujson.Obj(
                "variable" -> m.arguments("variable").head.text,
                "value" -> m.arguments("value").head.text,
                "unit" -> m.arguments("unit").head.text
              )
              paramUnitObjs.append(oneVar)
            }

          }
          obj("paramSettingsAndUnits") = paramUnitObjs
        }

        case "UnitRelation" => {
          val paramUnitObjs = new ArrayBuffer[ujson.Value]()
          for (m <- g._2) {
//            println("men: " + m.text + " " + m.label)
//              println("m: " + m.text + " " + m.label)
//              println("args: " + m.arguments.keys.mkString("|"))
              val oneVar = ujson.Obj(
                "variable" -> m.arguments("variable").head.text,
//                "value" -> m.arguments("value").head.text,
                "unit" -> m.arguments("unit").head.text
              )
              paramUnitObjs.append(oneVar)


          }
          obj("units") = paramUnitObjs
        }

        case "DateEvent" => {
          val dateEventObjs = new ArrayBuffer[ujson.Value]()
          for (m <- g._2) {
            //            println("men: " + m.text + " " + m.label)
            //              println("m: " + m.text + " " + m.label)
            //              println("args: " + m.arguments.keys.mkString("|"))
            val event = m.arguments("subj").head.text + " " + m.arguments("verb").head.text
            val oneVar = ujson.Obj(
              "date" -> m.asInstanceOf[EventMention].trigger.text,
              //                "value" -> m.arguments("value").head.text,
              "event" -> event
            )
            dateEventObjs.append(oneVar)


          }
          obj("dateEvents") = dateEventObjs
        }
        case "Location" => {
          val locations = g._2.map(_.text).distinct.sorted
          obj("locations") = locations
        }
        case "Date" => {
          val dates = g._2.map(_.text).distinct.sorted
          obj("dates") = dates
        }
        case "Parameter" => {
          val modelComps = g._2.map(_.text).distinct.sorted
          obj("parameters") = modelComps
        }
        case "ParameterSetting" => {
          val paramSetObjs = new ArrayBuffer[ujson.Value]()

          for (m <- g._2) {
            //            println("men: " + m.text + " " + m.label)
            //              println("m: " + m.text + " " + m.label)
            //              println("args: " + m.arguments.keys.mkString("|"))
            val oneVar = ujson.Obj(
              "variable" -> m.arguments("variable").head.text,
              //                "value" -> m.arguments("value").head.text,
              "value" -> m.arguments("value").head.text
            )
            paramSetObjs.append(oneVar)


          }
          obj("paramSettings") = paramSetObjs
        }
        case _ => println("Other")
      }
    }

    println("OBJECT: " + obj)

    val json = ujson.write(obj, indent = 2)
    val outputDir = "/Users/alexeeva/Desktop/automates-related/MentionAssemblyDebug/mentions/"
    val pw = new PrintWriter(new File(outputDir + file.getName.replace(".json", "-assembled-mentions.json")))
    pw.write(json)
    pw.close()
    val labels = mentions.map(_.label).distinct.mkString("||")
    println("Labels: " + labels)

//    val modelComp = mentions.filter(_.label contains "ModelComponent")
//    val func = mentions.filter(_.label contains "Function")
//    for (g <- descr) {
//      print(g.text + "\n")
//      val texts = g.arguments.flatMap(_._2).map(_.text)
//      for (t <- texts)
//        print(t + "\n")
//      println("======")
//    }

//    for (g <- modelComp) {
//      println("MC: " + g.text + " " + g.label)
//    }
//    for (g <- func) {
//      print(g.text + "\n")
//      for (arg <- g.arguments) {
//        println(arg._1)
//        for (a <- arg._2) {
//          println("-> " + a.text)
//        }
//      }
//      println("======")
//    }
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
//    val descrMentions = mentions.filter(_ matches "Description")
//
//    val exportGlobalVars = false
//    if (exportGlobalVars) {
//      val exporter = GlobalVarTSVExporter(file.getAbsolutePath, numOfWikiGroundings)
//      val globalVars = getGlobalVars(descrMentions, None, true)
//
//      exporter.export(globalVars)
//    }
//
//
//    println("Description mentions: ")
//    for (dm <- descrMentions) {
//      println("----------------")
//      println(dm.text)
//      //      println(dm.foundBy)
//      for (arg <- dm.arguments) {
//        println(arg._1 + ": " + dm.arguments(arg._1).map(_.text).mkString("||"))
//      }
//      if (dm.attachments.nonEmpty) {
//        for (att <- dm.attachments) println("att: " + att.asInstanceOf[AutomatesAttachment].toUJson)
//      }
//    }
//    val paramSettingMentions = mentions.filter(_ matches "ParameterSetting")
//
//
//
//    println("\nParam setting mentions: ")
//    for (m <- paramSettingMentions) {
//      println("----------------")
//      println(m.text)
//      //      println(m.foundBy)
//      for (arg <- m.arguments) {
//        println(arg._1 + ": " + m.arguments(arg._1).head.text)
//      }
//    }
//    val unitMentions = mentions.filter(_ matches "UnitRelation")
//    println("Unit mentions: ")
//    for (m <- unitMentions) {
//      println("----------------")
//      println(m.text)
//      //      println(m.foundBy)
//      for (arg <- m.arguments) {
//        println(arg._1 + ": " + m.arguments(arg._1).head.text)
//      }
//    }
//
//
//    val contextMentions = mentions.filter(_ matches "Context")
//    println("Context setting mentions: ")
//    for (m <- contextMentions) {
//      println("----------------")
//      println(m.text)
//      //      println(m.foundBy)
//      for (arg <- m.arguments) {
//        println(arg._1 + ": " + m.arguments(arg._1).head.text)
//      }
//    }

    // 4. Export to all desired formats
//    exportAs.foreach { format =>
//      val exporter = getExporter(format, s"$outputDir/${file.getName.replace("." + inputType, s"_mentions.${format}")}")
//      exporter.export(mentions)
//      exporter.close() // close the file when you're done
//    }
  }
}
