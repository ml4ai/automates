package org.clulab.aske.automates.apps

import java.io.{BufferedWriter, File, FileWriter, PrintWriter}

import ai.lum.common.ConfigUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.aske.automates.data.{CosmosJsonDataLoader, DataLoader, TextRouter}
import org.clulab.aske.automates.OdinEngine
import org.clulab.aske.automates.attachments.AutomatesAttachment
import org.clulab.discourse.rstparser.{DiscourseTree, TokenOffset}
import org.clulab.utils.{DisplayUtils, FileUtils, Serializer}

import scala.collection.mutable.ArrayBuffer

object DiscourseExperiments extends App {

//  case class DiscourseTuple(relation:String, nucText:List[String], satText:List[String], start:TokenOffset, end:TokenOffset)

  val config = ConfigFactory.load()
  val inputKind = "science-parse" // or "cosmos"

//  val inputDir = "/media/alexeeva/ee9cacfc-30ac-4859-875f-728f0764925c/storage/discourse-related/data/mitre_data/txt_with_per"
//  val inputDir = "/media/alexeeva/ee9cacfc-30ac-4859-875f-728f0764925c/storage/automates-related/askeDiscourseExperiments/toRunDiscourseParser"
//  val outputDir = "/media/alexeeva/ee9cacfc-30ac-4859-875f-728f0764925c/storage/discourse-related/data/mitre_data/output"

//  val inputDir = "/media/alexeeva/ee9cacfc-30ac-4859-875f-728f0764925c/storage/automates-related/Processed_SuperMaaS_model_documents-20210607T204611Z-001/Processed_SuperMaaS_model_documents/JSON_data"
  val inputDir = "/media/alexeeva/ee9cacfc-30ac-4859-875f-728f0764925c/storage/automates-related/ak-function-files/jsons"

//  val inputType = "txt"
  val inputType = "json"
//  val dataLoader = DataLoader.selectLoader(inputType) // pdf, txt or json are supported, and we assume json == science parse json
  val dataLoader = if (inputKind == "cosmos") new CosmosJsonDataLoader else {
    DataLoader.selectLoader(inputType)
  }
  val exportAs: List[String] = config[List[String]]("apps.exportAs")
  val files = FileUtils.findFiles(inputDir, dataLoader.extension)
  val reader = OdinEngine.fromConfig(config[Config]("TextEngine"))

  // START ANALYZING DISCOURSE PARSER RELATIONS IN ASKE FILES

  val discExplorer = new DiscourseExplorer


  val askeDiscourse = new PrintWriter(new File("/media/alexeeva/ee9cacfc-30ac-4859-875f-728f0764925c/storage/automates-related/ak-function-files/jsons/paragraph_discourse_parses.tsv" ))
  askeDiscourse.write("doc" + "\t" + "relation" + "\t" + "nucleus" + "\t" + "satellite" + "\t" + "start"+ "\t" + "end" + "\n")
  files.foreach { file =>
    val fileName = file.getName()
    val texts = dataLoader.loadFile(file)
    println("filename: " + fileName)
//    println("Texts: " + texts.mkString(" ").slice(0, 1500) + "\n")
    if (texts.nonEmpty)  {
      val paragraphDocs = if (inputKind=="cosmos") {
        texts.map(t => reader.annotate(t.split("::").head)).filter(_.isDefined).map(_.get)
      } else {
        texts.map(t => reader.annotate(t)).filter(_.isDefined).map(_.get)
      }

      val trees = paragraphDocs.map(d => d.discourseTree.get)
      for (t <- trees) {
        //      println("START TREE")
        for (tuple <- discExplorer.findRootPairs(t) ) {
          askeDiscourse.write(file.getName() + "\t" + tuple.relation + "\t" + tuple.nucText.mkString(" ") + "\t" + tuple.satText.mkString(" ") + "\t" + tuple.start + "\t" + tuple.end + "\n")
          //        println("->" + tuple.relation + ": " + tuple.nucText.mkString(" ") + "||" + " " + tuple.satText.mkString(" ") + " || " + tuple.start + " " + tuple.end + "\n")
        }
      }
    }


  }
  askeDiscourse.close()

// START RUN DISC PARSER ON SHORT TEXT
//  val text = "es = saturation vapor pressure at 1.5 to 2.5-m height (kPa), calculated for daily time steps as the average of saturation vapor pressure at maximum and minimum air temperature"
//
//  val discExplorer = new DiscourseExplorer
//  val doc = reader.annotate(text)
//          //      println("-->" + doc.discourseTree.get)
//          val tree = doc.discourseTree.get
//          //      println(tree.firstToken + "<<-")
//          for (tuple <- discExplorer.findRootPairs(tree) ) {
//
//              println("->" + tuple.relation + ": " + tuple.nucText.mkString(" ") + "||" + " " + tuple.satText.mkString(" ") + " || " + tuple.start + " " + tuple.end + "\n")
//            }
  // END RUN DISC PARSER ON SHORT TEXT

  // START EXPERIMENT FOR BSH: OVERLAP BETWEEN CAUSE DISCOURSE RELATIONS AND EIDOS CAUSAL EXTRACTIONS
  // // input for this: val inputDir = "/media/alexeeva/ee9cacfc-30ac-4859-875f-728f0764925c/storage/discourse-related/data/mitre_data/txt_with_per"
//  // to write:
//  val pwCausesStats = new PrintWriter(new File("/media/alexeeva/ee9cacfc-30ac-4859-875f-728f0764925c/storage/discourse-related/data/mitre_data/output/cause_stats.csv" ))
//  pwCausesStats.write("doc" + "\t" + "discourse_full_doc_causes" + "\t" + "discourse_paragraph_causes" + "\t" + "mentions_causes" + "\n")
//  val pwFullTextDiscourse = new PrintWriter(new File("/media/alexeeva/ee9cacfc-30ac-4859-875f-728f0764925c/storage/discourse-related/data/mitre_data/output/full_text_disc.csv" ))
//  pwFullTextDiscourse.write("doc" + "\t" + "token_int" +"\t" + "relation" + "\t" + "nuc_text" + "\t" + "sat_text" + "\n")
//  val pwParagraphDiscourse = new PrintWriter(new File("/media/alexeeva/ee9cacfc-30ac-4859-875f-728f0764925c/storage/discourse-related/data/mitre_data/output/paragraph_disc.csv" ))
//  pwParagraphDiscourse.write("doc" + "\t" + "token_int" +"\t" + "relation" + "\t" + "nuc_text" + "\t" + "sat_text" + "\n")
//  val pwMentions = new PrintWriter(new File("/media/alexeeva/ee9cacfc-30ac-4859-875f-728f0764925c/storage/discourse-related/data/mitre_data/output/event_causes.txt" ))
//  pwMentions.write("doc" + "\t" + "token_int(sent::interval)" +"\t" + "text" + "\n")
//
//  val discExplorer = new DiscourseExplorer
//
//  files.foreach { file =>
//
//
//    val fileName = file.getName()
//
//    // 1. Open corresponding output file and make all desired exporters
//    println(s"Extracting from ${file.getName}")
//
//    // 2. Get the input file contents
//    // make one text, split on blank linke, remove \n's within each text
//    val texts = dataLoader.loadFile(file).mkString(" ").split("\n\n").filter(_.length > 10).map(_.replace("\n", ""))
//
////    println("-->" + file)
////    for (t <- texts) println("text -> " + t.replace("\n", ""))
//
//    // paragraph annotation
//    val paragraphDiscTuples = new ArrayBuffer[DiscourseTuple]()
//    for (text <- texts) {
////      println("->" + text)
//      try {
//        val doc = reader.annotate(text)
//        //      println("-->" + doc.discourseTree.get)
//        val tree = doc.discourseTree.get
//        //      println(tree.firstToken + "<<-")
//        for (tuple <- discExplorer.findRootPairs(tree) )
//          if (tuple.relation.contains("cause")) {
//            paragraphDiscTuples.append(tuple)
//            println("->" + tuple.relation + ": " + tuple.nucText.mkString(" ") + "||" + " " + tuple.satText.mkString(" ") + " || " + tuple.start + " " + tuple.end + "\n")
//          }
//      } catch {
//        case _ => "some unknown error"
//      } finally {
//        println("just keep going")
//      }
//
//
////      pw.write(tree.toString() + "\n===========\n")
//    }
//
//
//    println("par causes: " + paragraphDiscTuples.length)
//    for (tup <- paragraphDiscTuples) pwParagraphDiscourse.write(fileName + "\t" + tup.asInstanceOf[DiscourseTuple].start + "::" + tup.asInstanceOf[DiscourseTuple].end  +"\t" + tup.asInstanceOf[DiscourseTuple].relation + "\t" + tup.asInstanceOf[DiscourseTuple].nucText.mkString(" ") + "\t" + tup.asInstanceOf[DiscourseTuple].satText.mkString(" ") + "\n")
//
//    // full doc annotation
//    val doc = reader.annotate(texts.mkString(" "))
//    println("full doc annotated")
//    val tree = doc.discourseTree.get//.visualizerJSON()
//    val causalTuples = discExplorer.findRootPairs(tree).filter(_.relation.contains("cause"))
//    println("ful doc causes: " + causalTuples.length)
//    for (tup <- causalTuples) pwFullTextDiscourse.write(fileName + "\t" + tup.start + "::" + tup.end  +"\t" + tup.relation + "\t" + tup.nucText.mkString(" ") + "\t" + tup.satText.mkString(" ") + "\n")
////    pw.write(tree.toString() + "\n============\n")
//////
//
//
//
//
////    // MENTIONS - extracting from full doc
//    val mentions = reader.extractFrom(doc)
//    val causal = mentions.filter(_ matches "Causal")
//    println("event causes: " + causal.length)
//    for (m <- causal) pwMentions.write(fileName + "\t" + m.sentence + "::" + m.tokenInterval + "\t" + m.text + "\n")
//
//
//    pwCausesStats.write(file.getName() + "\t" + causalTuples.length + "\t" + paragraphDiscTuples.length + "\t" + causal.length + "\n")
////    for (c <- causal) println(c.sentence + " " + c.tokenInterval)
////    for (m <- causal) {
////      pw.write("causalRel: " + m.text + m.startOffset + m.endOffset + "\n")
////    }
//
////    for (m <- mentions) println(m.text + " " + m.label)
//    //The version of mention that includes routing between text vs. comment
//    //    val mentions = texts.flatMap(text => textRouter.route(text).extractFromText(text, filename = Some(file.getName))).seq
//    //    for (m <- mentions) {
//    //      println("----------------")
//    //      println(m.text)
//    //
//    //      if (m.arguments.nonEmpty) {
//    //        for (arg <- m.arguments) {
//    //          println("arg: " + arg._1 + ": " + m.arguments(arg._1).head.text)
//    //        }
//    //      }
//    //
//    //    }
//
//
////    val defMentions = mentions.filter(_ matches "Definition")
//
////    println("Definition mentions: ")
////    for (dm <- defMentions) {
////      println("----------------")
////      println(dm.text)
////      //      println(dm.foundBy)
////      for (arg <- dm.arguments) {
////        println(arg._1 + ": " + dm.arguments(arg._1).head.text)
////      }
////      if (dm.attachments.nonEmpty) {
////        for (att <- dm.attachments) println("att: " + att.asInstanceOf[AutomatesAttachment].toUJson)
////      }
////    }
////    val paramSettingMentions = mentions.filter(_ matches "ParameterSetting")
////
////
////
////    println("\nParam setting mentions: ")
////    for (m <- paramSettingMentions) {
////      println("----------------")
////      println(m.text)
////      //      println(m.foundBy)
////      for (arg <- m.arguments) {
////        println(arg._1 + ": " + m.arguments(arg._1).head.text)
////      }
////    }
////    val unitMentions = mentions.filter(_ matches "UnitRelation")
////    println("Unit setting mentions: ")
////    for (m <- unitMentions) {
////      println("----------------")
////      println(m.text)
////      //      println(m.foundBy)
////      for (arg <- m.arguments) {
////        println(arg._1 + ": " + m.arguments(arg._1).head.text)
////      }
////    }
//
//  }
//  pwCausesStats.close()
//  pwFullTextDiscourse.close()
//  pwParagraphDiscourse.close()
//  pwMentions.close()
  // END EXPERIMENT FOR BSH: OVERLAP BETWEEN CAUSE DISCOURSE RELATIONS AND EIDOS CAUSAL EXTRACTIONS


}