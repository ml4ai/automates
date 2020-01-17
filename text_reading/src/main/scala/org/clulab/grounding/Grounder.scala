package org.clulab.grounding

import java.io.File

import ai.lum.common.ConfigUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.aske.automates.OdinEngine
import org.clulab.odin.Mention

import scala.sys.process.Process
import scala.util.parsing.json.JSON



object SVOGrounder {

  def main(args: Array[String]): Unit = {



    def ground(term: String) = {
      val url = "http://34.73.227.230:8000/match_phrase/" + term + "/"
      scala.io.Source.fromURL(url)
    }

    def groundMention(mention: Mention) = {

      ???

    }

    def getTermsFromDefinition(mention: Mention): Option[Seq[String]] = {
      println(mention.text)
      if (mention matches "Definition") {
        for (m <- mention.arguments("definition").head.lemmas) println(m)
        mention.arguments("definition").head.lemmas
      } else None

    }


    def runSparqlQuery(term: String, scriptDir: String): String = {
      val command = Seq("python", s"$scriptDir/sparql.py")
      val process = Process(command, new File(s"$scriptDir"))
      process.!!
    }


    runSparqlQuery("word", "/home/alexeeva/Repos/automates/text_reading/sparql")

//    val text = "where Kcbmin is the minimum basal crop coefficient"
//    val config = ConfigFactory.load()
//    val textConfig: Config = config[Config]("TextEngine")
//    val textReader = OdinEngine.fromConfig(textConfig)
//    val defMentions = textReader.extractFromText(text, filename = Some("whatever")).filter(m => m matches "Definition")
//    for (dm <- defMentions) {
////      println(dm.arguments("variable").head.text)
////      println(dm.arguments("definition").head.text)
////      println(dm.arguments("definition").head.semHeadLemma)
////      println(dm.arguments("definition").head.synHeadLemma)
//      val terms = getTermsFromDefinition(dm)
//      println("terms: " + terms)
//      if (terms.nonEmpty) {
//        for (term <- terms.get) {
//          println(term + "\n")
//          //        print(ground(lemma) + "\n")
//          val result = ground(term)
//
//          println(JSON.parseFull(result.mkString))
//
//        }
//      }
//
//    }




//    print(ground(request))
  }


}
