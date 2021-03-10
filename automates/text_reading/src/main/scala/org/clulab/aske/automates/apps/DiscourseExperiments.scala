package org.clulab.aske.automates.apps

import java.io.{BufferedWriter, File, FileWriter, PrintWriter}

import ai.lum.common.ConfigUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.aske.automates.data.{DataLoader, TextRouter}
import org.clulab.aske.automates.OdinEngine
import org.clulab.aske.automates.attachments.AutomatesAttachment
import org.clulab.discourse.rstparser.DiscourseTree
import org.clulab.utils.{DisplayUtils, FileUtils, Serializer}

object DiscourseExperiments extends App {


  val config = ConfigFactory.load()

  val inputDir = "/media/alexeeva/ee9cacfc-30ac-4859-875f-728f0764925c/storage/discourse-related/data/mitre_data/txt_with_per"
  val outputDir = "/media/alexeeva/ee9cacfc-30ac-4859-875f-728f0764925c/storage/discourse-related/data/mitre_data/output"
  val inputType = "txt"
  val dataLoader = DataLoader.selectLoader(inputType) // pdf, txt or json are supported, and we assume json == science parse json
  val exportAs: List[String] = config[List[String]]("apps.exportAs")
  val files = FileUtils.findFiles(inputDir, dataLoader.extension)
  val reader = OdinEngine.fromConfig(config[Config]("TextEngine"))


  files.par.foreach { file =>
    // 1. Open corresponding output file and make all desired exporters
    println(s"Extracting from ${file.getName}")

    // 2. Get the input file contents
    // note: for science parse format, each text is a section
    val texts = dataLoader.loadFile(file)
    // 3. Extract causal mentions from the texts
    // todo: here I am choosing to pass each text/section through separately -- this may result in a difficult coref problem
    val mentions = texts.flatMap(reader.extractFromText(_, filename = Some(file.getName)))

    val doc = reader.annotate(texts.mkString(" "))
//    println(doc.discourseTree.getOrElse("No tree"))
//
    val tree = doc.discourseTree.get

   println(tree)
    val causal = mentions.filter(_ matches "Causal")

    for (m <- causal) {
      println("causalRel: " + m.text + m.startOffset + m.endOffset)
    }

//    for (m <- mentions) println(m.text + " " + m.label)
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


//    val defMentions = mentions.filter(_ matches "Definition")

//    println("Definition mentions: ")
//    for (dm <- defMentions) {
//      println("----------------")
//      println(dm.text)
//      //      println(dm.foundBy)
//      for (arg <- dm.arguments) {
//        println(arg._1 + ": " + dm.arguments(arg._1).head.text)
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
//    println("Unit setting mentions: ")
//    for (m <- unitMentions) {
//      println("----------------")
//      println(m.text)
//      //      println(m.foundBy)
//      for (arg <- m.arguments) {
//        println(arg._1 + ": " + m.arguments(arg._1).head.text)
//      }
//    }

  }
}