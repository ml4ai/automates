package org.clulab.aske.automates.apps

import java.io.{File, PrintWriter}
import ai.lum.common.ConfigUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.aske.automates.data.{CosmosJsonDataLoader, DataLoader, TextRouter}
import org.clulab.aske.automates.OdinEngine
import org.clulab.aske.automates.apps.ExtractAndAlign.{getGlobalVars, returnAttachmentOfAGivenTypeOption}
import org.clulab.aske.automates.attachments.{MentionLocationAttachment, ParamSettingIntAttachment}
import org.clulab.aske.automates.mentions.CrossSentenceEventMention
import org.clulab.utils.{FileUtils, Serializer}
import org.clulab.odin.{EventMention, Mention}
import org.clulab.utils.MentionUtils.{distinctByText, getMentionsWithLocations, getMentionsWithoutLocations, getTriggerText}

import scala.collection.mutable.ArrayBuffer


/**
  * App used to extract mentions from paper jsons and readmes related to one model and writing them to a json
  */
object ExtractAndAssembleMentionEvents extends App {

  val config = ConfigFactory.load()
  val numOfWikiGroundings: Int = config[Int]("apps.numOfWikiGroundings")
  val inputDir: String = config[String]("apps.inputDirectory")
  val outputDir: String = config[String]("apps.outputDirectory")
  val inputType: String = config[String]("apps.inputType")
  val dataLoader = DataLoader.selectLoader(inputType) // pdf, txt or json are supported, and we assume json == cosmos json; to use science parse. comment out this line and uncomment the next one
  //  val dataLoader = new ScienceParsedDataLoader
  val exportAs: List[String] = config[List[String]]("apps.exportAs")
  val includeAnnotationField: Boolean = config[Boolean]("apps.includeAnnotationField")
  val files = FileUtils.findFiles(inputDir, dataLoader.extension)
  val mdfiles = FileUtils.findFiles(inputDir, "md")
  val textMentions = new ArrayBuffer[Mention]()
  val mdMentions = new ArrayBuffer[Mention]()
  val allFiles = files ++ mdfiles
  allFiles.par.foreach { file =>
    val fileExt = file.toString.split("\\.").last
    val reader = fileExt match {
      case "json" => OdinEngine.fromConfig(config[Config]("TextEngine"))
      case "md" => OdinEngine.fromConfig(config[Config]("MarkdownEngine"))
      case "txt" => OdinEngine.fromConfig(config[Config]("TextEngine"))
      case _ => ???
    }
    val dataLoader = fileExt match {
      case "json" => DataLoader.selectLoader("json")
      case "md" => DataLoader.selectLoader("md")
      case "txt" => DataLoader.selectLoader("txt")
      case _ => ???
    }
    // 1. Open corresponding output file and make all desired exporters
    println(s"Extracting from ${file.getName}")
    // 2. Get the input file contents
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
      case "txt" => textMentions.appendAll(mentions)
      case _ => ???
    }
  }

  val distinctTextMention = distinctByText(textMentions.distinct)
  val distinctMdMentions = distinctByText(mdMentions.distinct)
  val obj = assembleMentions(distinctTextMention, distinctMdMentions)

  writeJsonToFile(obj, outputDir, "assembledMentions.json")


  // Support methods
  def assembleMentions(textMentions: Seq[Mention], mdMentions: Seq[Mention]): ujson.Value = {
    val obj = ujson.Obj()
    val groupedByLabel = (textMentions++mdMentions).groupBy(_.label)
    for (g <- groupedByLabel) {
      g._1 match {

        case "CommandSequence" => {
          val modelObjs = new ArrayBuffer[ujson.Value]()
          for (m <- g._2) {
            val trigger = getTriggerText(m)
            val oneModel = ujson.Obj(
              "text" -> m.text,
              "command" -> trigger
            )
            val commandArgs = ujson.Obj()
            val (paramValueParArgs, other) = m.arguments.partition(_._1 == "commandLineParamValuePair")
            // don't include comm line param separately in the output
            val (_, theRest) = other.partition(_._1 == "commLineParameter")
            val (allCommandArgs, remaining) = theRest.partition(_._1 == "commandArgs")
            commandArgs("allArgs") = allCommandArgs.head._2.head.text
            val argComponents = ujson.Obj()
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
                  paramValuePairs.append(oneArgObj)
                }
              }
            }
            if (paramValuePairs.nonEmpty) argComponents("paramValuePairs") = paramValuePairs
            commandArgs("components") = argComponents
            oneModel("commandArgs") = commandArgs
            modelObjs.append(addSharedFields(m, oneModel))
          }
          obj("commandSequences") = modelObjs
        }
        case "ModelDescr" => {
          val modelObjs = new ArrayBuffer[ujson.Value]()
          for (m <- g._2) {
            val trigger = getTriggerText(m)
            val oneModel = ujson.Obj(
              "name" -> m.arguments("modelName").head.text,
              "description" -> m.arguments("modelDescr").head.text,
              "trigger" -> trigger
            )
            modelObjs.append(addSharedFields(m, oneModel))
          }
          obj("models") = ujson.Obj("descriptions" -> modelObjs)
        }
        case "ModelLimitation" => {
          val modelObjs = new ArrayBuffer[ujson.Value]()
          for (m <- g._2) {
            val trigger = getTriggerText(m)
            val oneModel = ujson.Obj(
              "name" -> m.arguments("modelName").head.text,
              "limitation" -> m.arguments("modelDescr").head.text,
              "trigger" -> trigger
            )
            modelObjs.append(addSharedFields(m, oneModel))
          }
          obj("models")("limitations") = modelObjs
        }

        case "Model" => {
          val locations = new ArrayBuffer[ujson.Value]()
          for (m <- g._2) {
            val paramObj = ujson.Obj(
              "text" -> m.text
            )
            locations.append(addSharedFields(m, paramObj))
          }
          obj("model_names") = locations
        }

        case "Repository" => {
          val repos = new ArrayBuffer[ujson.Value]()
          for (m <- g._2) {
            val oneRepoObj = ujson.Obj(
              "text" -> m.text
            )
            repos.append(addSharedFields(m, oneRepoObj))
          }
          obj("repos") = repos
        }
        case "ParamAndUnit" => {
          val paramUnitObjs = new ArrayBuffer[ujson.Value]()
          for (m <- g._2) {
            if (m.arguments.keys.toList.contains("value") & m.arguments.keys.toList.contains("unit")) {
              val oneVar = ujson.Obj(
                "variable" -> m.arguments("variable").head.text,
                "value" -> m.arguments("value").head.text,
                "unit" -> m.arguments("unit").head.text
              )
              paramUnitObjs.append(addSharedFields(m, oneVar))
            }
          }
          obj("paramSettingsAndUnits") = paramUnitObjs
        }

        case "UnitRelation" => {
          val paramUnitObjs = new ArrayBuffer[ujson.Value]()
          for (m <- g._2) {
            val oneVar = ujson.Obj(
              "variable" -> m.arguments("variable").head.text,
              "unit" -> m.arguments("unit").head.text
            )
            paramUnitObjs.append(addSharedFields(m, oneVar))
          }
          obj("units") = paramUnitObjs
        }

        case "DateEvent" => {
          val dateEventObjs = new ArrayBuffer[ujson.Value]()
          for (m <- g._2) {
            val event = m.arguments("subj").head.text + " " + m.arguments("verb").head.text
            val oneDateEvent = ujson.Obj(
              "date" -> m.asInstanceOf[EventMention].trigger.text,
              "event" -> event
            )
            dateEventObjs.append(addSharedFields(m, oneDateEvent))


          }
          obj("dateEvents") = dateEventObjs
        }
        case "Location" => {
          val locations = new ArrayBuffer[ujson.Value]()
          for (m <- g._2) {
            val oneLocation = ujson.Obj(
              "text" -> m.text
            )
            locations.append(addSharedFields(m, oneLocation))
          }
          obj("locations") = locations
        }
        case "Date" => {
          val dates = new ArrayBuffer[ujson.Value]()
          for (m <- g._2) {
            val oneDate = ujson.Obj(
              "text" -> m.text
            )
            val source = getSource(m)
            dates.append(addSharedFields(m, oneDate))
          }
          obj("dates") = dates
        }
        case "Parameter" => {
          val parameterObjs = new ArrayBuffer[ujson.Value]()
          for (m <- g._2) {
            val paramObj = ujson.Obj(
              "text" -> m.text
            )
            parameterObjs.append(addSharedFields(m, paramObj))
          }
          obj("parameters") = parameterObjs.distinct
        }
        case "ParameterSetting" => {
          val paramSetObjs = new ArrayBuffer[ujson.Value]()

          for (m <- g._2) {
            val oneVar = ujson.Obj(
              "variable" -> m.arguments("variable").head.text,
              "value" -> m.arguments("value").head.text
            )
            paramSetObjs.append(addSharedFields(m, oneVar))
          }
          obj("paramSettings") = paramSetObjs
        }
        case "IntervalParameterSetting" => {
          val paramSetObjs = new ArrayBuffer[ujson.Value]()
          for (m <- g._2) {
            val oneVar = ujson.Obj()
            for (arg <- m.arguments) {
              oneVar(arg._1) = arg._2.head.text
            }
            val attachment = returnAttachmentOfAGivenTypeOption(m.attachments, "ParamSettingIntervalAtt")
            if (attachment.isDefined) {
              val paramSetAttJson = attachment.get.asInstanceOf[ParamSettingIntAttachment].toUJson.obj
              val inclLower = paramSetAttJson("inclusiveLower")
              val inclUpper = paramSetAttJson("inclusiveUpper")
              if (!inclLower.isNull) oneVar("inclusiveLower") = paramSetAttJson("inclusiveLower").bool
              if (!inclUpper.isNull) oneVar("inclusiveUpper") = paramSetAttJson("inclusiveUpper").bool
            }
            paramSetObjs.append(addSharedFields(m, oneVar))
          }
          obj("paramSettingsInterval") = paramSetObjs
        }
        case _ =>
      }
    }
    obj
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

  def addSharedFields(m: Mention, currentFields: ujson.Value): ujson.Value = {
    val source = getSource(m)
    currentFields("source") = source
    currentFields("sentence") = m.sentenceObj.getSentenceText
    val annotationFields = ujson.Obj(
      "match" -> 0,
      "acceptable" -> 1,
      "dojo-entry" -> ujson.Arr("")
    )
    if (includeAnnotationField) currentFields("annotations") = annotationFields
    currentFields
  }


  def writeJsonToFile(obj: ujson.Value, outputDir: String, outputFileName: String): Unit = {

    val json = ujson.write(obj, indent = 2)
    val pw = new PrintWriter(new File(outputDir + outputFileName))
    pw.write(json)
    pw.close()

  }

  def getExporter(exporterString: String, filename: String): Exporter = {
    exporterString match {
      case "serialized" => SerializedExporter(filename)
      case "json" => AutomatesExporter(filename)
      case "tsv" => TSVExporter(filename)
      case _ => throw new NotImplementedError(s"Export mode $exporterString is not supported.")
    }
  }

}
