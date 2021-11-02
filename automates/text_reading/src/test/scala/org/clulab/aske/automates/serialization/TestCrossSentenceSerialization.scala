package org.clulab.aske.automates.serialization

import org.clulab.serialization.json._

import java.io.File
import java.io.FileWriter
import java.io.BufferedWriter
import org.clulab.processors.fastnlp.FastNLPProcessor
import ai.lum.common.ConfigUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.aske.automates.OdinEngine
import org.clulab.aske.automates.TestUtils.{ExtractionTest, Somebody}
import org.clulab.aske.automates.apps.AutomatesShell.ieSystem
import org.clulab.aske.automates.apps.{Exporter, JSONDocExporter, JSONExporter, SerializedExporter}
import org.clulab.aske.automates.data.DataLoader
import org.clulab.aske.automates.mentions.CrossSentenceEventMention
import org.clulab.aske.automates.serializer.AutomatesJSONSerializer
import org.clulab.odin.serialization.json.MentionOps
import org.clulab.odin.{EventMention, Mention, TextBoundMention}
import org.clulab.utils.FileUtils
import org.clulab.serialization.DocumentSerializer

   // first, let's make crossSentenceMentions to export to JSON file

  class TestCrossSentenceSerialization extends ExtractionTest {

    val textToTest = "Rn depends on RS, but also on T and RH. The only additional parameter appearing in the suggested formula is the extraterrestrial radiation, RA."
//    val textToTest = "LAI is leaf area index"
    passingTest should s"serialize and deserialize the mention successfully: ${textToTest}" taggedAs (Somebody) in {
      val mentions = extractMentions(textToTest)
      // why is what extracted cross sentence mentions?
      val crossSentenceMentions = mentions.filter(m => m.isInstanceOf[CrossSentenceEventMention]).distinct
//      val crossSentenceMentions = mentions.filter(m => m.isInstanceOf[EventMention]).distinct
      for (m <- crossSentenceMentions) {
        println(m + " " + m.text + " " + m.label + " " + m.asInstanceOf[CrossSentenceEventMention].sentences.mkString("|"))
      }

      val value = mentions.filter(m => m.isInstanceOf[TextBoundMention])
      val uJson = AutomatesJSONSerializer.serializeMentions(crossSentenceMentions)
      println(uJson)
      // next, let's try to export the mentions to JSON file (how can I use export method??)
      val deserializedMentions = AutomatesJSONSerializer.toMentions(uJson)
      for (m <- deserializedMentions) println(">>" + m.text + " " + m.label + " " + m.asInstanceOf[CrossSentenceEventMention].sentences.mkString("|"))
//      deserializedMentions should have size 1
      deserializedMentions.head.document.equivalenceHash should equal (crossSentenceMentions.head.document.equivalenceHash)

      deserializedMentions should have size (crossSentenceMentions.size)

      deserializedMentions.head.text should equal(crossSentenceMentions.head.text)
      deserializedMentions.head.asInstanceOf[CrossSentenceEventMention].sentences should equal(crossSentenceMentions.head.asInstanceOf[CrossSentenceEventMention].sentences)

      for (m <- deserializedMentions) println("dm: " + m)
      val hashesDeser = deserializedMentions.map(m =>   m.equivalenceHash).toSet
      val hashesOrig = crossSentenceMentions.map(_.equivalenceHash).toSet
      hashesDeser should equal(hashesOrig)

//      deserializedMentions.head.id should equal(crossSentenceMentions.head.id)

//      assert(crossSentenceMentions == deserializedMentions)
    }
    //    def textToCrossSentenceMentions(text: String): Seq[Mention] = {
    //      val Mentions = extractMentions(text)
    //      val CrossSentenceMentions = Mentions.filter(m => m.isInstanceOf[CrossSentenceEventMention])
    //      CrossSentenceMentions
    //    }


//    for (m <- crossSentenceMentions) {
//      println(f"${m.text} ${m.asInstanceOf[CrossSentenceEventMention].}")
//    }
  }

//
//    object Export extends App {
//      def getExporter(exporterString: String, filename: String): Exporter = {
//        exporterString match {
//          case "serialized" => SerializedExporter(filename)
//          case "json" => JSONExporter(filename)
//          case _ => throw new NotImplementedError(s"Export mode $exporterString is not supported.")
//        }
//      }
//
//      //      val config = ConfigFactory.load()
//      //      val inputDir = config[String]("apps.inputDirectory")
//      //      val outputDir = config[String]("apps.outputDirectory")
//      //      val inputType = config[String]("apps.inputType")
//      //      val dataLoader = DataLoader.selectLoader(inputType) // pdf, txt or json are supported, and we assume json == science parse json
//      //      val exportAs: List[String] = config[List[String]]("apps.exportAs")
//      //      val files = FileUtils.findFiles(inputDir, dataLoader.extension)
//      //      val reader = OdinEngine.fromConfig(config[Config]("TextEngine"))
//      val proc = new FastNLPProcessor()
//      //      val serializer = new DocumentSerializer
//      val exporter = new JSONDocExporter()
//      val document = proc.annotate(textToTest)
//      val json = document.json(pretty = true)
//      exporter.export(json, "testFile.json")
//    }
//
//  }
//
//    // next, let's make cross sentence mentions back from the JSON file (DataLoader??)
//
//    // compare the newly made mentions and original cross sentence mentions (how...?)
//
//
////
////      // For each file in the input directory:
////      files.foreach { file =>
////        // 1. Open corresponding output file and make all desired exporters
////        println(s"Extracting from ${file.getName}")
////        // 2. Get the input file contents
////        //here, for the science parse texts, we join all the sections to produce the Document of the whole paper
////        val text = dataLoader.loadFile(file).mkString(" ")
////        val document = proc.annotate(text)
////        //jsonify the Document
////        val json = document.json(pretty = true)
////        //replace the file name with the name that indicates it has been serialized; todo: need a better way to indictae the target dir
////        val newFileName = file.toString().replace(".json", "_seralizedDoc")
////        exporter.export(json, newFileName)
////    }
////  }
//
//
////    def extractFromText(text: String, keepText: Boolean = false, filename: Option[String]): Seq[Mention] = {
////      val doc = cleanAndAnnotate(text, keepText, filename)
////      val odinMentions = extractFrom(doc)  // CTM: runs the Odin grammar
////      odinMentions  // CTM: collection of mentions ; to be converted to some form (json)
////    }
//
////
////class TestCrossSentenceSerialization extends FlatSpec with Matchers {
////
////  val finder = StringMatchEntityFinder.fromStrings(Seq("MATCH", "OTHER"), "Matched", "testTaxonomy.yml")
////
////  it should "not find mentions when no string match" in {
////
////    // Text: "This should have no match."
////    val doc = jsonStringToDocument("{\"sentences\":[{\"words\":[\"This\",\"should\",\"have\",\"no\",\"match\",\".\"],\"startOffsets\":[0,5,12,17,20,25],\"endOffsets\":[4,11,16,19,25,26],\"raw\":[\"This\",\"should\",\"have\",\"no\",\"match\",\".\"],\"graphs\":{}}]}")
////    val ms = finder.extract(doc)
////    ms.length should be (0)
////  }
////
////  ignore should "find one mention match when sting matches one place" in {
////    // Text: "This should MATCH for sure!"
////    val doc = jsonStringToDocument("{\"sentences\":[{\"words\":[\"This\",\"should\",\"MATCH\",\"for\",\"sure\",\"!\"],\"startOffsets\":[0,5,12,18,22,26],\"endOffsets\":[4,11,17,21,26,27],\"raw\":[\"This\",\"should\",\"MATCH\",\"for\",\"sure\",\"!\"],\"graphs\":{}}]}")
////    val ms = finder.extract(doc)
////    ms.length should be (1)
////    val m = ms.head
////    m.text should be ("MATCH")
////    m.label should be ("Matched")
////  }
////
////  ignore should "match several instances of same string" in {
////    // Text; "This should MATCH twice, because of the second MATCH."
////    val doc = jsonStringToDocument("{\"sentences\":[{\"words\":[\"This\",\"should\",\"MATCH\",\"twice\",\",\",\"because\",\"of\",\"the\",\"second\",\"MATCH\",\".\"],\"startOffsets\":[0,5,12,18,23,25,33,36,40,47,52],\"endOffsets\":[4,11,17,23,24,32,35,39,46,52,53],\"raw\":[\"This\",\"should\",\"MATCH\",\"twice\",\",\",\"because\",\"of\",\"the\",\"second\",\"MATCH\",\".\"],\"graphs\":{}}]}")
////    val ms = finder.extract(doc)
////    ms.length should be (2)
////    ms foreach { m =>
////      m.text should be ("MATCH")
////      m.label should be ("Matched")
////    }
////
////  }
////
////  ignore should "match more than one string" in {
////    // Text: "This should MATCH twice, since OTHER is also here."
////    val doc = jsonStringToDocument("{\"sentences\":[{\"words\":[\"This\",\"should\",\"MATCH\",\"twice\",\",\",\"since\",\"OTHER\",\"is\",\"also\",\"here\",\".\"],\"startOffsets\":[0,5,12,18,23,25,31,37,40,45,49],\"endOffsets\":[4,11,17,23,24,30,36,39,44,49,50],\"raw\":[\"This\",\"should\",\"MATCH\",\"twice\",\",\",\"since\",\"OTHER\",\"is\",\"also\",\"here\",\".\"],\"graphs\":{}}]}")
////    val ms = finder.extract(doc)
////    ms.length should be (2)
////    ms.exists(m => m.text == "MATCH" && m.label == "Matched") should be (true)
////    ms.exists(m => m.text == "OTHER" && m.label == "Matched") should be (true)
////  }
////}
