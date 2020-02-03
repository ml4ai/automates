package org.clulab.grounding

import java.io.File

import ai.lum.common.ConfigUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.apache.commons.text.similarity.LevenshteinDistance
import org.clulab.aske.automates.OdinEngine

import org.clulab.odin.Mention

import scala.collection.mutable.ArrayBuffer
import scala.sys.process.Process
import scala.util.parsing.json.JSON


case class sparqlResult(searchTerm: String, name: String, className: String, score: Option[Double])

object SVOGrounder {

  def main(args: Array[String]): Unit = {

    def groundWithAPI(term: String) = {
      val url = "http://34.73.227.230:8000/match_phrase/" + term + "/"
      scala.io.Source.fromURL(url)
    }

    def groundMentionWithAPI(mention: Mention) = {

      for (word <- mention.words) {
        println("USING GROUNDMENTION:")
        println(groundWithAPI(word).mkString(""))
      }
    }




    def groundMentionWithSparql(mention: Mention) = {
      //todo: should probably return a mention with attachment
      val terms = getTerms(mention) //todo: this should already have gotten rid of stop word and also returned reasonable collocations, e.g., head word + >compound
      if (terms.nonEmpty) {
        for (word <- terms.get) {

          println("USING ENDPOINT:")
          val result = runSparqlQuery(word, "/home/alexeeva/Repos/automates/text_reading/sparql")
          println("term: " + word + "\nresult: " + result.mkString(""))
          println("end of result")
          if (result.nonEmpty) {
            val resultLines = result.split(("\n"))
            val resultNames = resultLines.map(rl => rl.split("\t")(1))
            println("BBBBB")
            for (name <- resultNames) {
              println("name: " + name + " score: " + editDistance(name, word))
            }

            //todo:
            //val nameWithScores = resultNames.map(rn => (name, editDistance(rn, word)
            //get indices of names with max scores
            //get the lines with those indices and turn those into
            //sparql results

//            println(withSimilarityScores.mkString(" -|||- "))
//            val grounding = new sparqlResult(splitResult(0), splitResult(1), splitResult(2), None)
//            println("=>>>" + grounding)
          }
        }
      }
    }

    def getTerms(mention: Mention): Option[Seq[String]] = {
      println(mention.text)
      //todo: will depend on type of mention, e.g., for definitions, only look at the words in the definition arg, not var itself
      if (mention matches "Definition") {
        val terms = new ArrayBuffer[String]()
        val lemmas = mention.arguments("definition").head.lemmas.get
        val tags = mention.arguments("definition").head.tags.get
        for (i <- 0 to lemmas.length-1) {
          if (tags(i).startsWith("N") || tags(i).startsWith("J") || tags(i).startsWith("V")) {
            terms += lemmas(i)
          }
        }
        //the API takes word separated by underscores
        val compound = getCompounds(mention.arguments("definition").head)
        if (compound.nonEmpty) {
          terms += compound.get
        }

        Some(terms)
      } else None

    }

    def getCompounds(mention: Mention): Option[String] = {

      println("==>" + mention.text)
      val headWord = mention.synHeadLemma
      println("syn head: " + headWord)
      val outgoing = mention.sentenceObj.dependencies.head.getOutgoingEdges(mention.synHead.get)
      println("all deps from syntactic head: " + outgoing.mkString(" "))
      //get index of the leftmost word of the compound
      if (outgoing.exists(tuple => tuple._2 == "compound")) {
        val indexOfCompoundToken = mention.sentenceObj.dependencies.head.getOutgoingEdges(mention.synHead.get).filter(tuple => tuple._2 == "compound").map(tuple => tuple._1).min
        //count as compound the tokens between the leftmost word with relation 'compound' and the syntactic head of the mention
        val compoundWord = mention.sentenceObj.words.slice(indexOfCompoundToken, mention.synHead.get + 1).mkString(" ")
        println(compoundWord)
        val semHead = mention.semHeadLemma
        println("sem head: " + semHead)
        return Some(compoundWord.replace(" ", "_"))
      } else None

    }



    def runSparqlQuery(term: String, scriptDir: String): String = {
      val command = Seq("python", s"$scriptDir/sparqlWrapper.py", term)
      val process = Process(command, new File(s"$scriptDir"))
      process.!!
    }

    def editDistance(s1: String, s2: String): Double = {
      println("000000")
      val dist = LevenshteinDistance.getDefaultInstance().apply(s1, s2).toDouble
      println("AAAAA")
      dist
    }

    def groundMentionsWithSparql(mentions: Seq[Mention]): Seq[Mention] = {
      //ground a seq of mentions using groundMentionWithSparql on each
      ???

    }


//    val result = runSparqlQuery("word", "/home/alexeeva/Repos/automates/text_reading/sparql")
//    println(result)

    val text = "where Kcbmin is the minimum radius"
    println(text + "<<--")
    val config = ConfigFactory.load()
    val textConfig: Config = config[Config]("TextEngine")
    val textReader = OdinEngine.fromConfig(textConfig)
    val defMentions = textReader.extractFromText(text, filename = Some("whatever")).filter(m => m matches "Definition")
    for (dm <- defMentions) {
      println("CCCCC")
      //todo: this is temp to see if things work, should have a menthod
      //that does this on all the found mentions
      groundMentionWithSparql(dm)
    }

  }


}
