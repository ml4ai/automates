package org.clulab.grounding

import ai.lum.common.ConfigUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.aske.automates.OdinEngine

import scala.util.parsing.json.JSON



object SVOGrounder {

  def main(args: Array[String]): Unit = {



    def ground(term: String) = {
      val url = "http://34.73.227.230:8000/match_phrase/" + term + "/"
      scala.io.Source.fromURL(url)
    }

    val text = "where Kcbmin is the minimum basal crop coefficient"
    val config = ConfigFactory.load()
    val textConfig: Config = config[Config]("TextEngine")
    val textReader = OdinEngine.fromConfig(textConfig)
    val defMentions = textReader.extractFromText(text, filename = Some("whatever")).filter(m => m matches "Definition")
    for (dm <- defMentions) {
//      println(dm.arguments("variable").head.text)
//      println(dm.arguments("definition").head.text)
//      println(dm.arguments("definition").head.semHeadLemma)
//      println(dm.arguments("definition").head.synHeadLemma)
      for (lemma <- dm.arguments("definition").head.lemmas.get) {
        print(lemma + "\n")
//        print(ground(lemma) + "\n")
        val result = ground(lemma)

        println(JSON.parseFull(result.mkString))

      }
    }




//    print(ground(request))
  }


}
