package org.clulab.grounding

import java.io.File
import com.typesafe.config.{Config, ConfigFactory}
import upickle.default._
import org.apache.commons.text.similarity.LevenshteinDistance
import org.clulab.odin.Mention

import scala.collection.mutable.ArrayBuffer
import scala.sys.process.Process
import upickle.default.{ReadWriter, macroRW}
import ai.lum.common.ConfigUtils._
import org.clulab.aske.automates.apps.{ExtractAndAlign, JSONDocExporter}
import org.clulab.embeddings.word2vec.Word2Vec
import org.clulab.utils.FileUtils

import scala.concurrent.duration.DurationInt

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
  val exporter = JSONDocExporter()

def groundTermsToWikidataRanked(variable: String, terms_with_underscores: Seq[String], sentence: Seq[String], w2v: Word2Vec, k: Int): Option[Seq[sparqlWikiResult]] = {

  val cacheFilePath: String = config[String]("grounding.WikiCacheFilePath")
  val file = new File(cacheFilePath)
  val fileCache = if (file.exists()) {
    ujson.read(file)
  } else ujson.Obj()

  if (terms_with_underscores.nonEmpty) {
    val terms = terms_with_underscores.map(_.replace("_", " "))
    val resultsFromAllTerms = new ArrayBuffer[sparqlWikiResult]()

    for (term <- terms) {
      val term_list = terms.filter(_==term)
      val result = new ArrayBuffer[String]()

      if (fileCache.obj.contains(term) && fileCache.obj(term).str.nonEmpty) {
       result.append(fileCache.obj(term).str)
      } else {
        val res = WikidataGrounder.runSparqlQuery(term, WikidataGrounder.sparqlDir)
        result.append(res)
      }
      fileCache(term) = result.head
      val allSparqlWikiResults = new ArrayBuffer[sparqlWikiResult]()
      if (result.head.nonEmpty) {
        val lineResults = new ArrayBuffer[sparqlWikiResult]()
        val resultLines = result.head.split("\n")
        for (line <- resultLines) {
          val splitLine = line.trim().split("\t")
          val conceptId = splitLine(1)
          val conceptLabel = splitLine(2)
          val conceptDescription = Some(splitLine(3))
          val altLabel =  Some(splitLine(4))
          val subClassOf = Some(splitLine(5))
          val textWordList = (sentence ++ term_list ++ List(variable)).distinct.filter(w => !stopWords.contains(w))
          val wikidataWordList = conceptDescription.getOrElse("").split(" ") ++ altLabel.getOrElse("").replace(", ", " ").replace("\\(|\\)", "").split(" ").filter(_.length > 0) :+ conceptLabel.toLowerCase()

          val score = editDistanceNormalized(conceptLabel, term) + editDistanceNormalized(textWordList.mkString(" "),  wikidataWordList.mkString(" ")) + w2v.maxSimilarity(textWordList,  wikidataWordList) + wordOverlap(textWordList, wikidataWordList)

          val lineResult = new sparqlWikiResult(term, conceptId, conceptLabel, conceptDescription, altLabel, subClassOf, Some(score), "wikidata")
          lineResults += lineResult

        }

        // when there are multiple subclassOf per wikidata entry, each returned separately, so we need to make one new wiki result object with all of the subclass entries
        val grouped = lineResults.groupBy(_.conceptID)
        val newLineResults = new ArrayBuffer[sparqlWikiResult]()
        for (g <- grouped) {
          if (g._2.length > 1) {

            val allClassOf = Some(g._2.map(_.subClassOf.getOrElse("NA")).mkString(","))
            val oneResultInGroup = g._2.head
            newLineResults.append(new sparqlWikiResult(oneResultInGroup.searchTerm, oneResultInGroup.conceptID, oneResultInGroup.conceptLabel, oneResultInGroup.conceptDescription, oneResultInGroup.alternativeLabel, allClassOf, oneResultInGroup.score, oneResultInGroup.source))
          } else newLineResults.append(g._2.head)
        }


        val allLabels = newLineResults.map(res => res.conceptLabel)
        val duplicates = allLabels.groupBy(identity).collect { case (x, ys) if ys.lengthCompare(1) > 0 => x }.toList
        val (uniqueLabelResLines, nonUniqLabelResLines) = newLineResults.partition(res => !duplicates.contains(res.conceptLabel))
        allSparqlWikiResults ++= uniqueLabelResLines
        //out of the items with the same label, e.g., crop (grown and harvested plant or animal product) vs. crop (hairstyle), choose the one with the highest score based on similarity of the wikidata description and alternative label to the sentence and search term the search term from
        if (nonUniqLabelResLines.nonEmpty) {
          allSparqlWikiResults += nonUniqLabelResLines.maxBy(_.score)
        }

      }
      resultsFromAllTerms ++= allSparqlWikiResults
      // update `cache` file
      exporter.export(ujson.write(fileCache), cacheFilePath.replace(".json", ""))
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
    val levenshteinDist = editDistance(s1, s2)
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
