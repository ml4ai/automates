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




object SVOGrounder {


  //grounding using the ontology API
  def groundWithAPI(term: String) = {
    val url = "http://34.73.227.230:8000/match_phrase/" + term + "/"
    scala.io.Source.fromURL(url)
  }

  def groundMentionWithAPI(mention: Mention) = {

    for (word <- mention.words) {
      println(groundWithAPI(word).mkString(""))
    }
  }



  /* return mention with a grounding attachment*/
  def groundMentionWithSparql(mention: Mention): Mention = {

    val terms = getTerms(mention) //get terms gets nouns, verbs, and adjs, and also returns reasonable collocations, e.g., syntactic head of the mention + >compound
    if (terms.nonEmpty) {
      val resultsFromAllTerms = new ArrayBuffer[sparqlResult]()
      for (word <- terms.get) {
        val result = runSparqlQuery(word, "/home/alexeeva/Repos/automates/text_reading/sparql")
        println("term: " + word + "\nresult: " + result.mkString(""))
        println("end of result")
        if (result.nonEmpty) {
          //each line in the result is a separate entry returned by the query:
          val resultLines = result.split(("\n"))
          //represent each returned entry/line as a sparqlResult and sort those by edit distance score (lower score is better)
          //todo: if several highest score and are the same 'name', return the class that is the lowest node in the ontology
          val sparqlResults = resultLines.map(rl => new sparqlResult(rl.split("\t")(0), rl.split("\t")(1), rl.split("\t")(2), Some(editDistance(rl.split("\t")(1), word)))).sortBy(sr => sr.score)
          for (result <- sparqlResults) {
            println("==>" + result.searchTerm + " " + result.name + " " + result.className + " " + result.score)
          }

          resultsFromAllTerms += sparqlResults.head

        }
      }

      //getting all the results with same (minimal) score
      val onlyMinScoreResults = resultsFromAllTerms.filter(res => res.score == resultsFromAllTerms.map(r => r.score).min)

      //the results where search term contains "_" should be ranked higher since those are collocations instead of separate words
      val (collocation, singleWord) = onlyMinScoreResults.partition(r => r.searchTerm.contains("_"))
      val finalResult = if (collocation.nonEmpty) collocation.head else singleWord.head


      println("results from all terms, head: search term: " + finalResult.searchTerm + " name: " + finalResult.name + " className: " + finalResult.className + " score: " + finalResult.score)

      val attachment = new groundingAttachment(finalResult.searchTerm, finalResult.name, finalResult.className, finalResult.score)
      val newMention = mention.withAttachment(attachment)

      println("new mention: " + newMention.label + " " + newMention.text + " " + newMention.attachments.mkString(" "))
      return newMention
    } else mention
  }

  /*get the terms from the mention to run sparql queries with*/
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

  /*get collocations from the mention*/
  def getCompounds(mention: Mention): Option[String] = {

    println("==>" + mention.text)
    val headWord = mention.synHeadLemma
    //      println("syn head: " + headWord)
    val outgoing = mention.sentenceObj.dependencies.head.getOutgoingEdges(mention.synHead.get)
    //      println("all deps from syntactic head: " + outgoing.mkString(" "))
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
    val grounded = mentions.map(m => groundMentionWithSparql(m))
    grounded
  }



  def groundDefinitions(mentions: Seq[Mention]): Seq[Mention] = {

    val (defMentions, other) = mentions.partition(m => m matches "Definition")
    val groundedDefMentions = groundMentionsWithSparql(defMentions)
    groundedDefMentions ++ other
    }


}
