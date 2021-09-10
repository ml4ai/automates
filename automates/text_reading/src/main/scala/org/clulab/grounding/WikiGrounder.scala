package org.clulab.grounding

import java.io.File
import com.typesafe.config.{Config, ConfigFactory}
import upickle.default._
import org.apache.commons.text.similarity.LevenshteinDistance
import org.clulab.odin.{Attachment, Mention, SynPath}

import scala.collection.mutable.ArrayBuffer
import scala.sys.process.Process
import upickle.default.{ReadWriter, macroRW}
import ai.lum.common.ConfigUtils._
import com.github.blemale.scaffeine.{Cache, Scaffeine}
import org.clulab.aske.automates.apps.ExtractAndAlign
import org.clulab.embeddings.word2vec.Word2Vec
import org.clulab.utils.FileUtils

import scala.concurrent.duration.DurationInt

// todo before pr: figure out paths when deserializing (add path to groundings in the payload and read them during arg reading)
//todo: pass the python query file from configs
//todo: document in wiki
// todo: return only groundings over threshold
// lower priority now
// todo: cache results to avoid regrounding what we already know
// alt labels should be a seq of strings, not a string: alternativeLabel
case class sparqlWikiResult(searchTerm: String, conceptID: String, conceptLabel: String, conceptDescription: Option[String], alternativeLabel: Option[String], subClassOf: Option[String], score: Option[Double], source: String = "Wikidata")

object sparqlWikiResult {
  implicit val rw: ReadWriter[sparqlWikiResult] = macroRW
}

case class WikiGrounding(variable: String, groundings: Seq[sparqlWikiResult])
object WikiGrounding {
  implicit val rw: ReadWriter[WikiGrounding] = macroRW
}

case class SeqOfWikiGroundings(wikiGroundings: Seq[WikiGrounding])

object SeqOfWikiGroundings {
  implicit val rw: ReadWriter[SeqOfWikiGroundings] = macroRW
}

object WikidataGrounder {

  val config: Config = ConfigFactory.load()
  val sparqlDir: String = config[String]("grounding.sparqlDir")
  val stopWords = FileUtils.loadFromOneColumnTSV("src/main/resources/stopWords.tsv")
//  val currentDir: String = System.getProperty("user.dir")

  val cache: Cache[String, String] = Scaffeine()
    .recordStats()
    .expireAfterWrite(1.hour)
    .maximumSize(500)
    .build[String, String]()


def groundTermsToWikidataRanked(variable: String, terms_with_underscores: Seq[String], sentence: Seq[String], w2v: Word2Vec, k: Int): Option[Seq[sparqlWikiResult]] = {

  if (terms_with_underscores.nonEmpty) {
    val terms = terms_with_underscores.map(_.replace("_", " "))
    val resultsFromAllTerms = new ArrayBuffer[sparqlWikiResult]()


    for (term <- terms) {

      println("term: " + term)
      val term_list = terms.filter(_==term)
      println(cache.getIfPresent(term) +"<<<<")
      var result = "-1"
//      val result = try {
//        cache.getIfPresent(term).get
//      } catch {
//        case e: Any => WikidataGrounder.runSparqlQuery(term, WikidataGrounder.sparqlDir)
//      }
//      println("result: " + result)
      if (cache.getIfPresent(term).isDefined) {
        println(cache.getIfPresent(term).get + "<<<<")
        result = cache.getIfPresent(term).get
      } else {
        println(WikidataGrounder.runSparqlQuery(term, WikidataGrounder.sparqlDir) + "<==")
        result = WikidataGrounder.runSparqlQuery(term, WikidataGrounder.sparqlDir)
      }
      cache.put(term, result)
      val allSparqlWikiResults = new ArrayBuffer[sparqlWikiResult]()
      if (result.nonEmpty) {
        val lineResults = new ArrayBuffer[sparqlWikiResult]()
        val resultLines = result.split("\n")
//        println("TERM: " + term)
//        println(">>" + resultLines.mkString("\n"))
        for (line <- resultLines) {
//          println("line: "+ line)
          val splitLine = line.trim().split("\t")

//          println("split line: "+ splitLine.mkString("|"))
          val conceptId = splitLine(1)
//          println("concept id: "+ conceptId)
          val conceptLabel = splitLine(2)
//          println("concept label: "+ conceptLabel)
          val conceptDescription = Some(splitLine(3))
//          println("conc descr: "+ conceptDescription)
          val altLabel =  Some(splitLine(4))
          val subClassOf = Some(splitLine(5))
          //          println("alt label: "+ altLabel)
          val textWordList = (sentence ++ term_list ++ List(variable)).distinct.filter(w => !stopWords.contains(w))
//          println("text: " + textWordList.mkString("::"))
          val wikidataWordList = conceptDescription.getOrElse("").split(" ") ++ altLabel.getOrElse("").replace(", ", " ").replace("\\(|\\)", "").split(" ").filter(_.length > 0) :+ conceptLabel.toLowerCase()
//          println("wiki: " + wikidataWordList.mkString("::"))

          val score = editDistanceNormalized(conceptLabel, term) + editDistanceNormalized(textWordList.mkString(" "),  wikidataWordList.mkString(" ")) + w2v.maxSimilarity(textWordList,  wikidataWordList) + wordOverlap(textWordList, wikidataWordList)
//          val score = w2v.avgSimilarity(textWordList,  wikidataWordList)
//          println("score: " + score)
//          print("score components: " + editDistanceNormalized(conceptLabel, term) + " " + editDistanceNormalized(textWordList.mkString(" "),  wikidataWordList.mkString(" ")) + " " + w2v.avgSimilarity(textWordList,  wikidataWordList) + " "+ w2v.maxSimilarity(textWordList,  wikidataWordList) + " " + wordOverlap(textWordList, wikidataWordList)  + "\n")
          val lineResult = new sparqlWikiResult(term, conceptId, conceptLabel, conceptDescription, altLabel, subClassOf, Some(score), "wikidata")
//          println("line result: ", lineResult)
          lineResults += lineResult

        }

        // when there are multiple subclassOf per wikidata entry, each returned separately, so we need to make one new wiki result object with all of the subclass entries
        val grouped = lineResults.groupBy(_.conceptID)
        val newLineResults = new ArrayBuffer[sparqlWikiResult]()
        for (g <- grouped) {
//          println("start group")
          if (g._2.length > 1) {

            val allClassOf = Some(g._2.map(_.subClassOf.getOrElse("NA")).mkString(","))
            val oneResultInGroup = g._2.head
            newLineResults.append(new sparqlWikiResult(oneResultInGroup.searchTerm, oneResultInGroup.conceptID, oneResultInGroup.conceptLabel, oneResultInGroup.conceptDescription, oneResultInGroup.alternativeLabel, allClassOf, oneResultInGroup.score, oneResultInGroup.source))
          } else newLineResults.append(g._2.head)
        }


        val allLabels = newLineResults.map(res => res.conceptLabel)
//                println("all labels: " + allLabels.mkString("|"))
        val duplicates = allLabels.groupBy(identity).collect { case (x, ys) if ys.lengthCompare(1) > 0 => x }.toList
        //
//         for (d <- duplicates) println("dup: " + d)
        //
        val (uniqueLabelResLines, nonUniqLabelResLines) = newLineResults.partition(res => !duplicates.contains(res.conceptLabel))
        //
        allSparqlWikiResults ++= uniqueLabelResLines
        //out of the items with the same label, e.g., crop (grown and harvested plant or animal product) vs. crop (hairstyle), choose the one with the highest score based on similarity of the wikidata description and alternative label to the sentence and search term the search term from
//        println("non unique: " + nonUniqLabelResLines.sortBy(_.score).reverse)
        if (nonUniqLabelResLines.nonEmpty) {
          allSparqlWikiResults += nonUniqLabelResLines.maxBy(_.score)
        }


      } else println("Result empty")
//      println("\nallSparqlWikiResults inside the loop : " + allSparqlWikiResults + "\n")

      resultsFromAllTerms ++= allSparqlWikiResults

    }

    Some(getTopKWiki(resultsFromAllTerms.toList.distinct.sortBy(_.score).reverse, k))


  } else None

}

  def getTopK(results: Seq[sparqlResult], k: Int): Seq[sparqlResult] = {
    if (k < results.length) {
      results.slice(0,k)
    } else {
      results
    }
  }

  def getTopKWiki(results: Seq[sparqlWikiResult], k: Int): Seq[sparqlWikiResult] = {
    if (k < results.length) {
      results.slice(0,k)
    } else {
      results
    }
  }

  def runSparqlQuery(term: String, scriptDir: String): String = {
    val command = Seq("python", s"$sparqlDir/sparqlWikiWrapper.py", term)
    val process = Process(command, new File(s"$scriptDir"))
    process.!!
  }

  def editDistance(s1: String, s2: String): Double = {
    val dist = LevenshteinDistance.getDefaultInstance().apply(s1, s2).toDouble
    dist
  }

  def editDistanceNormalized(s1: String, s2: String): Double = {
    val maxLength = math.max(s1.length, s2.length)
    val levenshteinDist = LevenshteinDistance.getDefaultInstance().apply(s1, s2).toDouble
    val normalizedDist = (maxLength - levenshteinDist) / maxLength
    normalizedDist
  }

  def wordOverlap(list1: Seq[String], list2: Seq[String]): Double = {
    list1.union(list2).length/(list1 ++ list2).length
  }


  /** Grounding a sequence of mentions and return a pretty-printable json string*/
  def mentionsToGlobalVarsWithWikidataGroundings(mentions: Seq[Mention]): String = {
    val globalVars = ExtractAndAlign.getGlobalVars(mentions, Some(Map.empty), true)
    val groundings = SeqOfWikiGroundings(globalVars.map(gv => WikiGrounding(gv.identifier, gv.groundings.getOrElse(Seq.empty))))
    write(groundings, indent = 4)
  }

}
