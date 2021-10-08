package org.clulab.aske.automates.apps

import ai.lum.common.ConfigUtils._
import com.github.tomtung.latex2unicode._
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.aske.automates.OdinEngine
import org.clulab.aske.automates.data.{CosmosJsonDataLoader, PlainTextDataLoader}
import org.clulab.utils.FileUtils

import java.io.PrintWriter
import scala.collection.mutable
import scala.collection.mutable.ArrayBuffer
import scala.collection.immutable.ListMap
import scala.util.control._

/**
  * App used to extract mentions from files in a directory and produce the desired output format (i.e., serialized
  * mentions or any other format we may need).  The input and output directories as well as the desired export
  * formats are specified in the config file (located in src/main/resources).
  * This makes ONE output file for each of the input files.
  */
object modelTermFrequency extends App {

  val config = ConfigFactory.load()

  val inputDir: String = "/Users/alexeeva/Desktop/automates-related/SuperMaaS-sept2021/cosmos-jsons-beautified"
  //  val inputDir = "/Users/alexeeva/Desktop/subscripts/texfiles"
//  val outputDir: String = "/Users/alexeeva/Desktop/automates-related/arxiv/tex_dir/anotherSample/output"
  val inputType = config[String]("apps.inputType")
  // if using science parse doc, uncomment next line and...
  //  val dataLoader = DataLoader.selectLoader(inputType) // pdf, txt or json are supported, and we assume json == science parse json
  //..comment out this line:
  val dataLoader = new CosmosJsonDataLoader
  val exportAs: List[String] = config[List[String]]("apps.exportAs")

  import java.io.File


  val files = FileUtils.findFiles(inputDir, "json")

  val reader = OdinEngine.fromConfig(config[Config]("TextEngine"))
  val loop = new Breaks

  def isBalanced(string: String, openDelim: String, close_delim: String): Boolean = {

    var n_open = 0
    for (ch <- string) {
      if (ch == openDelim.head) {
        n_open += 1
      } else if (ch == close_delim.head) {
        n_open -= 1
      }
      if (n_open < 0) return false
    }
    n_open == 0
  }

  //uncomment these for using the text/comment router
  //  val commentReader = OdinEngine.fromConfig(config[Config]("CommentEngine"))
  //  val textRouter = new TextRouter(Map(TextRouter.TEXT_ENGINE -> reader, TextRouter.COMMENT_ENGINE -> commentReader))
  // For each file in the input directory:


  //  pw.write("MAsha")
  files.foreach { file =>
    println("file: " + file)
    try {
//    val pw = new PrintWriter(new File(outputDir + file.getName.replace(".tex", "") + "subscripts_data_sample.txt"))
    //    println("FILE NAME" + file)
    // 1. Open corresponding output file and make all desired exporters
    //    println(s"Extracting from ${file.getName}")
    // 2. Get the input file contents
    // note: for science parse format, each text is a section
    val texts = dataLoader.loadFile(file)
      // terms in doc
      val terms = new ArrayBuffer[String]()
      for (t <- texts) {
        val justText = t.split("::").head
        val annotated = reader.annotate(justText).sentences

        for (s <- annotated)  {
          for (l <- s.lemmas.get) {
            terms.append(l)
          }
        }
      }

      val groupedWithCounts = terms.groupBy(identity).mapValues(_.size)
      val sorted = ListMap(groupedWithCounts.toSeq.sortBy(_._2):_*)
      println("=============\n")
      for ((k, v) <- sorted) {
        println(k + " " + v.toDouble )
      }


  } catch {
      case _ : Throwable => println("can't process file: " + file.getName)
    }
}

}


