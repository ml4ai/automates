package org.clulab.grounding

import java.io.File

import ai.lum.common.ConfigUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.apache.commons.text.similarity.LevenshteinDistance
import org.clulab.aske.automates.{OdinActions, OdinEngine}
import org.clulab.odin.{Attachment, Mention, SynPath}
import org.clulab.processors.Document
import org.clulab.struct.Interval

import scala.collection.mutable.ArrayBuffer
import scala.sys.process.Process
import scala.util.parsing.json.JSON


case class sparqlResult(searchTerm: String, name: String, className: String, score: Option[Double])

abstract class AutomatesAttachment extends Attachment

class groundingAttachment(searchTerm: String, name: String, className: String, score: Option[Double]) extends  AutomatesAttachment

//object groundingAttachment extends Attachment {
//  def asGroundingAttachment(sparql: sparqlResult): groundingAttachment =
//    sparql.asInstanceOf[groundingAttachment]
//}

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




    def groundMentionWithSparql(mention: Mention): Mention = {
      //todo: should probably return a mention with attachment
      val terms = getTerms(mention) //todo: this should already have gotten rid of stop word and also returned reasonable collocations, e.g., head word + >compound
      if (terms.nonEmpty) {
        val resultsFromAllTerms = new ArrayBuffer[sparqlResult]()
        for (word <- terms.get) {

          println("USING ENDPOINT:")
          val result = runSparqlQuery(word, "/home/alexeeva/Repos/automates/text_reading/sparql")
          println("term: " + word + "\nresult: " + result.mkString(""))
          println("end of result")
          if (result.nonEmpty) {
            val resultLines = result.split(("\n"))
            val sparqlResults = resultLines.map(rl => new sparqlResult(rl.split("\t")(0), rl.split("\t")(1), rl.split("\t")(2), Some(editDistance(rl.split("\t")(1), word)))).sortBy(sr => sr.score)
            resultsFromAllTerms += sparqlResults.head

          }
        }

        println("results from all terms, head: search term: " + resultsFromAllTerms.head.searchTerm + " name: " + resultsFromAllTerms.head.name + " className: " + resultsFromAllTerms.head.className + " score: " + resultsFromAllTerms.head.score)
        val newMention = new Mention {
          override def labels: Seq[String] = mention.labels

          override def tokenInterval: Interval = mention.tokenInterval

          override def sentence: Int = mention.sentence

          override def document: Document = mention.document

          override def keep: Boolean = mention.keep

          override val arguments: Map[String, Seq[Mention]] = mention.arguments
          override val attachments: Set[Attachment] = Set(new groundingAttachment(resultsFromAllTerms.head.searchTerm, resultsFromAllTerms.head.name, resultsFromAllTerms.head.className, resultsFromAllTerms.head.score)) //todo: change this to some meaningful check, e.g., the result that contains "_" in the search term---found something with a collocation, not just one term
          override val paths: Map[String, Map[Mention, SynPath]] = mention.paths

          override def foundBy: String = mention.foundBy + "_grounder"
        }
        return newMention
      } else mention
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
      val dist = LevenshteinDistance.getDefaultInstance().apply(s1, s2).toDouble
      dist
    }

    def groundMentionsWithSparql(mentions: Seq[Mention]): Seq[Mention] = {
      //ground a seq of mentions using groundMentionWithSparql on each
      mentions.map(m => groundMentionWithSparql(m))

    }


//    val result = runSparqlQuery("word", "/home/alexeeva/Repos/automates/text_reading/sparql")
//    println(result)

    val text = "where Kcbmin is the crop canopy"
    println(text + "<<--")
    val config = ConfigFactory.load()
    val textConfig: Config = config[Config]("TextEngine")
    val textReader = OdinEngine.fromConfig(textConfig)
    val defMentions = textReader.extractFromText(text, filename = Some("whatever")).filter(m => m matches "Definition")
//    for (dm <- defMentions) {
//      println("CCCCC")
//      //todo: this is temp to see if things work, should have a menthod
//      //that does this on all the found mentions
//      groundMentionWithSparql(dm)
//    }
    val groundedMentions = groundMentionsWithSparql(defMentions)

    for (m <- groundedMentions) {
      println(m.text + " grounding: " + m.attachments.head)
    }

  }


}
