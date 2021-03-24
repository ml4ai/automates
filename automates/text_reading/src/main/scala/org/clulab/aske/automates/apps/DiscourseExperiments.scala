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

  val inputDir = "/media/alexeeva/ee9cacfc-30ac-4859-875f-728f0764925c/storage/discourse-related/data/mitre_data/sample"
  val outputDir = "/media/alexeeva/ee9cacfc-30ac-4859-875f-728f0764925c/storage/discourse-related/data/mitre_data/output"
  val inputType = "txt"
  val dataLoader = DataLoader.selectLoader(inputType) // pdf, txt or json are supported, and we assume json == science parse json
  val exportAs: List[String] = config[List[String]]("apps.exportAs")
  val files = FileUtils.findFiles(inputDir, dataLoader.extension)
  val reader = OdinEngine.fromConfig(config[Config]("TextEngine"))
  val pw = new PrintWriter(new File("/media/alexeeva/ee9cacfc-30ac-4859-875f-728f0764925c/storage/discourse-related/data/mitre_data/output/text_pairs_paragraph_sample.txt" ))

  val discExplorer = new DiscourseExplorer

  files.foreach { file =>
    // 1. Open corresponding output file and make all desired exporters
    println(s"Extracting from ${file.getName}")

    // 2. Get the input file contents
    // make one text, split on blank linke, remove \n's within each text
    val texts = dataLoader.loadFile(file).mkString(" ").split("\n\n").map(_.replace("\n", ""))

//    println("-->" + file)
//    for (t <- texts) println("text -> " + t.replace("\n", ""))



    // full doc annotation
//    val doc = reader.annotate(texts.mkString(" "))
//    val tree = doc.discourseTree.get//.visualizerJSON()
//    pw.write(tree.toString() + "\n============\n")
////

    // paragraph annotation
    for (text <- texts) {
//      println("->" + text)
      val doc = reader.annotate(text)
//      println("-->" + doc.discourseTree.get)
      val tree = doc.discourseTree.get
      println(tree.charOffsets + "<")
      for (tuple <- discExplorer.findRootPairs(tree) )
        println("->" + tuple.nucText + " " + tuple.relation + " " + tuple.satText.mkString(" ") + " " + tuple.offset)
      pw.write(tree.toString() + "\n===========\n")
    }


//    // MENTIONS - shouldn't matter if it's full text or paragraphs
//    val mentions = texts.flatMap(reader.extractFromText(_, filename = Some(file.getName)))
//    val causal = mentions.filter(_ matches "Causal")
//    for (m <- causal) {
//      pw.write("causalRel: " + m.text + m.startOffset + m.endOffset + "\n")
//    }

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
  pw.close()
}