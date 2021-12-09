package org.clulab.aske.automates.apps

import java.io.{File, PrintWriter}
import ai.lum.common.ConfigUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.aske.automates.data.{CosmosJsonDataLoader, DataLoader, TextRouter}
import org.clulab.aske.automates.OdinEngine
import org.clulab.aske.automates.apps.ExtractAndAlign.{getGlobalVars, returnAttachmentOfAGivenTypeOption}
import org.clulab.aske.automates.attachments.MentionLocationAttachment
import org.clulab.aske.automates.mentions.CrossSentenceEventMention
import org.clulab.utils.{FileUtils, Serializer}
import org.clulab.odin.{EventMention, Mention}

import scala.collection.mutable.ArrayBuffer


//TODOs:
// make a method to include annotation if needed
// reduce redundant code in the assembly method
/**
  * App used to extract mentions from paper jsons and readmes
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
  val mdfiles = FileUtils.findFiles(inputDir, "md")
  val includeAnnotationField: Boolean = config[Boolean]("apps.includeAnnotationField")


  def getMentionsWithoutLocations(texts: Seq[String], file: File, reader: OdinEngine): Seq[Mention] = {
    // this is for science parse
    val mentions = texts.flatMap(t => reader.extractFromText(t, filename = Some(file.getName)))
    // most fields here will be null, but there will be a filename field; doing this so that all mentions, regardless of whether they have dtailed location (in the document) can be processed the same way
    val mentionsWithLocations = new ArrayBuffer[Mention]()
    for (m <- mentions) {
      val newAttachment = new MentionLocationAttachment(file.getName, Seq(-1), Seq(-1), "MentionLocation")
      val newMen = m match {
        case m: CrossSentenceEventMention => m.asInstanceOf[CrossSentenceEventMention].newWithAttachment(newAttachment)
        case _ => m.withAttachment(newAttachment)
      }
      mentionsWithLocations.append(newMen)
    }
    mentionsWithLocations
  }

  def getMentionsWithLocations(texts: Seq[String], file: File, reader: OdinEngine): Seq[Mention] = {
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

  val textMentions = new ArrayBuffer[Mention]()
  val mdMentions = new ArrayBuffer[Mention]()
  val allFiles = files ++ mdfiles
  allFiles.par.foreach { file =>
    val fileExt = file.toString.split("\\.").last
    val reader = fileExt match {
      case "json" => OdinEngine.fromConfig(config[Config]("TextEngine"))
      case "md" => OdinEngine.fromConfig(config[Config]("MarkdownEngine"))
      case _ => ???
    }
    val dataLoader = fileExt match {
      case "json" => DataLoader.selectLoader("json")
      case "md" => DataLoader.selectLoader("md")
      case _ => ???
    }
    // 1. Open corresponding output file and make all desired exporters
    println(s"Extracting from ${file.getName}")
    // 2. Get the input file contents
    // note: for science parse format, each text is a section
    val texts = dataLoader.loadFile(file)
    val mentions = if (file.getName.contains("COSMOS")) {
      // cosmos json
      getMentionsWithLocations(texts, file, reader)
    } else {
      // other file types---those don't have locations
      getMentionsWithoutLocations(texts, file, reader)
    }

    fileExt match {
      case "json" => textMentions.appendAll(mentions)
      case "md" => mdMentions.appendAll(mentions)
      case _ => ???
    }


  }

  def distinctByText(mentions: Seq[Mention]): Seq[Mention] = {
    val toReturn = new ArrayBuffer[Mention]()

    val groupedByLabel = mentions.groupBy(_.label)
    for (gr <- groupedByLabel) {
      val groupedByText = gr._2.groupBy(_.text)
      for (g <- groupedByText) {
        val distinctInGroup = g._2.head
        toReturn.append(distinctInGroup)
      }

    }
    toReturn

  }

  val distinctTextMention = distinctByText(textMentions.distinct)
  val distinctMdMentions = distinctByText(mdMentions.distinct)
  val obj = assembleMentions(distinctTextMention, distinctMdMentions)

  writeJsonToFile(obj, outputDir, "assembledMentions.json")


  def writeJsonToFile(obj: ujson.Value, outputDir: String, outputFileName: String): Unit = {

    val json = ujson.write(obj, indent = 2)
    val pw = new PrintWriter(new File(outputDir + outputFileName))
    pw.write(json)
    pw.close()

  }

  def getSource(m: Mention): ujson.Value = {
    val source = returnAttachmentOfAGivenTypeOption(m.attachments, "MentionLocation")
    val sourceJson = ujson.Obj()
    if (source.isDefined) {
      val sourceAsJson = source.get.toUJson
      sourceJson("page") = sourceAsJson("pageNum")
      sourceJson("blockIdx") = sourceAsJson("blockIdx")
      sourceJson("filename") = sourceAsJson("filename")
    }
    sourceJson
  }

  def assembleMentions(textMentions: Seq[Mention], mdMentions: Seq[Mention]): ujson.Value = {
    val obj = ujson.Obj()
    val groupedByLabel = (textMentions++mdMentions).groupBy(_.label)
    val annotationFields = ujson.Obj(
      "match" -> 0,
      "acceptable" -> 1,
      "dojo-entry" -> ujson.Arr("")
    )
    for (g <- groupedByLabel) {
      g._1 match {

        case "CommandSequence" => {
          val modelObjs = new ArrayBuffer[ujson.Value]()
          for (m <- g._2) {
            val trigger = m match {
              case csem: CrossSentenceEventMention => csem.trigger.text
              case em: EventMention => em.trigger.text
              case _ => null
            }


            val source = getSource(m)
            val oneModel = ujson.Obj(
              "text" -> m.text,
              "source" -> source,
              "sentence" -> m.sentenceObj.getSentenceText,
              "command" -> trigger
            )
            if (includeAnnotationField) oneModel("annotations") = annotationFields
            val commandArgs = ujson.Obj()

            val (paramValueParArgs, other) = m.arguments.partition(_._1 == "commandLineParamValuePair")
            // don't include comm line param separately in the output
            val (_, theRest) = other.partition(_._1 == "commLineParameter")
            val (allCommandArgs, remaining) = theRest.partition(_._1 == "commandArgs")
            commandArgs("allArgs") = allCommandArgs.head._2.head.text
            val argComponents = ujson.Obj()//new ArrayBuffer[ujson.Value]()

            for (arg <- remaining) {
              // for each arg type, create a "arg_type": [Str] json
              val argTypeObj = new ArrayBuffer[String]()
              for (v <- arg._2) {
                argTypeObj.append(v.text)

              }
              argComponents(arg._1) = argTypeObj
            }

            val paramValuePairs = new ArrayBuffer[ujson.Value]()
            if (paramValueParArgs.nonEmpty) {
              for (arg <- paramValueParArgs) {

                // for every arg mention
                for (v <- arg._2) {
                  // need to create another nested obj with two keys: parameter and value
                  val oneArgObj = ujson.Obj(
                    "parameter" -> v.arguments("parameter").head.text,
                    "value" -> v.arguments("value").head.text
                  )
                  //                commandArgs.append(oneArgObj)
                  paramValuePairs.append(oneArgObj)
                }
              }
            }
            if (paramValuePairs.nonEmpty) argComponents("paramValuePairs") = paramValuePairs
            commandArgs("components") = argComponents
            oneModel("commandArgs") = commandArgs
            modelObjs.append(oneModel)
          }
          obj("commandSequences") = modelObjs
        }
        case "ModelDescr" => {
          val modelObjs = new ArrayBuffer[ujson.Value]()
          for (m <- g._2) {
            val trigger = m match {
              case csem: CrossSentenceEventMention => csem.trigger.text
              case em: EventMention => em.trigger.text
              case _ => null
            }


            val source = getSource(m)
            val oneModel = ujson.Obj(
              "name" -> m.arguments("modelName").head.text,
              "description" -> m.arguments("modelDescr").head.text,
              "trigger" -> trigger,
              "source" -> source,
               "sentence" -> m.sentenceObj.getSentenceText
            )
            if (includeAnnotationField) oneModel("annotations") = annotationFields
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
            val source = getSource(m)
            val oneModel = ujson.Obj(
              "name" -> m.arguments("modelName").head.text,
              "limitation" -> m.arguments("modelDescr").head.text,
              "trigger" -> trigger,
              "source" -> source,
              "sentence" -> m.sentenceObj.getSentenceText

            )
            if (includeAnnotationField) oneModel("annotations") = annotationFields
            modelObjs.append(oneModel)
          }
          obj("models")("limitations") = modelObjs
        }

        case "Model" => {
          //          val locations = g._2.map(_.text).distinct.sorted
          //          obj("locations") = locations

          val locations = new ArrayBuffer[ujson.Value]()
          for (m <- g._2) {
            val paramObj = ujson.Obj()
            val source = getSource(m)
            paramObj("text") = m.text
            if (includeAnnotationField) paramObj("annotations") = annotationFields
            paramObj("source") = source
            paramObj("sentence") = m.sentenceObj.getSentenceText
            locations.append(paramObj)
          }
          //          g._2.map(_.text).distinct.sorted
          obj("model_names") = locations

        }

        case "Repository" => {
          val locations = new ArrayBuffer[ujson.Value]()
          for (m <- g._2) {
            val paramObj = ujson.Obj()
            val source = getSource(m)
            paramObj("text") = m.text
            if (includeAnnotationField) paramObj("annotations") = annotationFields
            paramObj("source") = source
            paramObj("sentence") = m.sentenceObj.getSentenceText
            locations.append(paramObj)
          }
          //          g._2.map(_.text).distinct.sorted
          obj("repos") = locations

        }
        case "ParamAndUnit" => {
          val paramUnitObjs = new ArrayBuffer[ujson.Value]()
          for (m <- g._2) {
            if (m.arguments.keys.toList.contains("value") & m.arguments.keys.toList.contains("unit")) {
              val source = getSource(m)
              val oneVar = ujson.Obj(
                "variable" -> m.arguments("variable").head.text,
                "value" -> m.arguments("value").head.text,
                "unit" -> m.arguments("unit").head.text,
                "source" -> source,
                "sentence" -> m.sentenceObj.getSentenceText
              )
              if (includeAnnotationField) oneVar("annotations") = annotationFields
              paramUnitObjs.append(oneVar)
            }

          }
          obj("paramSettingsAndUnits") = paramUnitObjs

        }

        case "UnitRelation" => {
          val paramUnitObjs = new ArrayBuffer[ujson.Value]()
          for (m <- g._2) {
            val source = getSource(m)
            val oneVar = ujson.Obj(
              "variable" -> m.arguments("variable").head.text,
              "unit" -> m.arguments("unit").head.text,
              "source" -> source,
              "sentence" -> m.sentenceObj.getSentenceText
            )
            if (includeAnnotationField) oneVar("annotations") = annotationFields
            paramUnitObjs.append(oneVar)


          }
          obj("units") = paramUnitObjs
        }

        case "DateEvent" => {
          val dateEventObjs = new ArrayBuffer[ujson.Value]()
          for (m <- g._2) {
            val event = m.arguments("subj").head.text + " " + m.arguments("verb").head.text
            val source = getSource(m)
            val oneVar = ujson.Obj(
              "date" -> m.asInstanceOf[EventMention].trigger.text,
              "event" -> event,
              "source" -> source,
              "sentence" -> m.sentenceObj.getSentenceText
            )
            if (includeAnnotationField) oneVar("annotations") = annotationFields
            dateEventObjs.append(oneVar)


          }
          obj("dateEvents") = dateEventObjs
        }
        case "Location" => {

          val locations = new ArrayBuffer[ujson.Value]()
          for (m <- g._2) {
            val paramObj = ujson.Obj()
            val source = getSource(m)
            paramObj("text") = m.text
            if (includeAnnotationField) paramObj("annotations") = annotationFields
            paramObj("source") = source
            paramObj("sentence") = m.sentenceObj.getSentenceText
            locations.append(paramObj)
          }
          obj("locations") = locations

        }
        case "Date" => {
          val dates = new ArrayBuffer[ujson.Value]()
          for (m <- g._2) {
            val paramObj = ujson.Obj()
            val source = getSource(m)
            paramObj("text") = m.text
            if (includeAnnotationField) paramObj("annotations") = annotationFields
            paramObj("context") = m.sentenceObj.getSentenceText
            paramObj("source") = source
            paramObj("sentence") = m.sentenceObj.getSentenceText
            dates.append(paramObj)
          }
          obj("dates") = dates
        }
        case "Parameter" => {

          val modelComps = new ArrayBuffer[ujson.Value]()
          for (m <- g._2) {
            val paramObj = ujson.Obj()
            val source = getSource(m)
            paramObj("text") = m.text
            if (includeAnnotationField) paramObj("annotations") = annotationFields
            paramObj("source") = source
            paramObj("sentence") = m.sentenceObj.getSentenceText
            modelComps.append(paramObj)
          }
          obj("parameters") = modelComps.distinct
        }
        case "ParameterSetting" => {
          val paramSetObjs = new ArrayBuffer[ujson.Value]()

          for (m <- g._2) {
            val source = getSource(m)
            val oneVar = ujson.Obj(
              "variable" -> m.arguments("variable").head.text,
              "value" -> m.arguments("value").head.text,
              "source" -> source,
              "sentence" -> m.sentenceObj.getSentenceText
            )
            if (includeAnnotationField) oneVar("annotations") = annotationFields
            paramSetObjs.append(oneVar)


          }
          obj("paramSettings") = paramSetObjs
        }
        case _ =>
      }
    }
    obj
  }
}
