package org.clulab.grounding

import java.io.File
import com.typesafe.config.{Config, ConfigFactory}
import upickle.default._
import org.apache.commons.text.similarity.LevenshteinDistance
import org.clulab.odin.{Attachment, Mention, SynPath}

import scala.collection.mutable.ArrayBuffer
import scala.sys.process.Process
import scala.collection.mutable
import upickle.default.{ReadWriter, macroRW}
import ai.lum.common.ConfigUtils._
import org.clulab.aske.automates.apps.ExtractAndAlign
import org.clulab.aske.automates.grfn.GrFNParser
import org.clulab.embeddings.word2vec.Word2Vec
import org.clulab.grounding.SVOGrounder.groundDescriptionsToSVO
import org.clulab.utils.AlignmentJsonUtils.SeqOfGlobalVariables
import org.clulab.utils.FileUtils
// get a serializer for groundings
// have option to load previously stored groundings
// todo: how to write a query that will return the closest string, e.g., time for time
// todo: is the query not deterministic? time was time one time but then that one disappeared
//todo: pass the python query file from configs
//todo: document in wiki
// todo: add wikidata id, link?, and text to global var
// todo: return only groundings over threshold
// but what is the threshold? longest term with wiki concept edit distance?
// can return multiple concepts; possibly both compounds AND components; structured? compound: seq[Grounding], singleton: seq[Grounding]
// grounding: {
// id,
// text,
// link,
// score
//}
// todo: results of from all terms need to be combined and top n returned - already doing it
// todo: make a case class for groups of wiki groundings---the map is unusable - no need, just simplified what the grounding and ranking method returns
// todo: exclude verbs from terms?
// todo: tests for the grounder
// todo: cache results to avoid regrounding what we already know
// todo: read in groundings as a map and use them while creating global vars; add path to groundings in the payload and read them during arg reading
// alt labels should be a seq of strings, not a string: alternativeLabel
case class sparqlWikiResult(searchTerm: String, conceptID: String, conceptLabel: String, conceptDescription: Option[String], alternativeLabel: Option[String], score: Option[Double], source: String = "Wikidata")

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

// fixme: rename to capital letter
object wikidataGrounder {

  val config: Config = ConfigFactory.load()
  val sparqlDir: String = config[String]("grounding.sparqlDir")
  val stopWords = FileUtils.loadFromOneColumnTSV("src/main/resources/stopWords.tsv")
//  val currentDir: String = System.getProperty("user.dir")
def groundTermsToWikidataRanked(variable: String, terms_with_underscores: Seq[String], sentence: Seq[String], w2v: Word2Vec, k: Int): Option[Seq[sparqlWikiResult]] = {

  //todo: can I pass mentions here? that way can compare the whole sentence to the definition and alt labels instead of just the term list. although the terms come from elements and those are already missing mention info; can I store sentence along with the terms? maybe as the final element of the term list and then just do terms [:-1]
  // can I ground while creating global vars?
  if (terms_with_underscores.nonEmpty) {
    val terms = terms_with_underscores.map(_.replace("_", " "))
    val resultsFromAllTerms = new ArrayBuffer[sparqlWikiResult]()


    for (term <- terms) {
      //case class sparqlWikiResult(searchTerm: String, conceptID: String, conceptLabel: String, conceptDescription: Option[String], alternativeLabel: Option[String], score: Option[Double], source: String = "Wikidata")
      val term_list = terms.filter(_==term)
      //    val term = "air temperature"
      //    val term_list = List("temperature", "air temperature")
      val result = wikidataGrounder.runSparqlQuery(term, wikidataGrounder.sparqlDir)
      val allSparqlWikiResults = new ArrayBuffer[sparqlWikiResult]()
      if (result.nonEmpty) {
        val lineResults = new ArrayBuffer[sparqlWikiResult]()
        val resultLines = result.split("\n")
        println("TERM: " + term)
        println(resultLines.mkString("\n"))
        for (line <- resultLines) {
//          println("line: "+ line)
          val splitLine = line.trim().split("\t")

//          println("split line: "+ splitLine.mkString("|"))
          val conceptId = splitLine(1)
//          println("concept id: "+ conceptId)
          val conceptLabel = splitLine(2)
//          println("concept label: "+ conceptLabel)
          val conceptDescription = if (splitLine.length > 3) Some(splitLine(3)) else None
//          println("conc descr: "+ conceptDescription)
          val altLabel = if (splitLine.length > 4) Some(splitLine(4)) else None
//          println("alt label: "+ altLabel)
          val textWordList = (sentence ++ term_list ++ List(variable)).distinct.filter(w => !stopWords.contains(w))
          println("text: " + textWordList.mkString("::"))
          val wikidataWordList = conceptDescription.getOrElse("").split(" ") ++ altLabel.getOrElse("").replace(", ", " ").replace("\\(|\\)", "").split(" ").filter(_.length > 0) :+ conceptLabel.toLowerCase()
          println("wiki: " + wikidataWordList.mkString("::"))


//          val score = 1 - 1/(editDistanceNormalized(conceptLabel, term) + w2v.avgSimilarity(textWordList,  wikidataWordList)+ wordOverlap(textWordList, wikidataWordList) + 1)
          // as good a score as I could get to align val text = "I went to get a haircut and the barber gave me a crop."
          //    val sent = proc.annotate(text)
          //    val grounder = wikidataGrounder
          //    val wikiGroundings = grounder.groundTermsToWikidataRanked("Cr", Seq("crop"), sent.sentences.head.words, w2v, 10).getOrElse("No groundings")
          val score = editDistanceNormalized(conceptLabel, term) + editDistanceNormalized(textWordList.mkString(" "),  wikidataWordList.mkString(" ")) + w2v.maxSimilarity(textWordList,  wikidataWordList) + wordOverlap(textWordList, wikidataWordList)
//          val score = w2v.avgSimilarity(textWordList,  wikidataWordList)
          println("score: " + score)
          print("score components: " + editDistanceNormalized(conceptLabel, term) + " " + editDistanceNormalized(textWordList.mkString(" "),  wikidataWordList.mkString(" ")) + " " + w2v.avgSimilarity(textWordList,  wikidataWordList) + " "+ w2v.maxSimilarity(textWordList,  wikidataWordList) + " " + wordOverlap(textWordList, wikidataWordList)  + "\n")
          val lineResult = new sparqlWikiResult(term, conceptId, conceptLabel, conceptDescription, altLabel, Some(score), "wikidata")
          println("line result: ", lineResult)
          lineResults += lineResult

        }


        val allLabels = lineResults.map(res => res.conceptLabel)
//                println("all labels: " + allLabels.mkString("|"))
        val duplicates = allLabels.groupBy(identity).collect { case (x, ys) if ys.lengthCompare(1) > 0 => x }.toList
        //
//         for (d <- duplicates) println("dup: " + d)
        //
        val (uniqueLabelResLines, nonUniqLabelResLines) = lineResults.partition(res => !duplicates.contains(res.conceptLabel))
        //
        allSparqlWikiResults ++= uniqueLabelResLines
        //out of the items with the same label, e.g., crop (grown and harvested plant or animal product) vs. crop (hairstyle), choose the one with the highest score based on similarity of the wikidata description and alternative label to the sentence and search term the search term from
//        println("non unique: " + nonUniqLabelResLines.sortBy(_.score).reverse)
        if (nonUniqLabelResLines.nonEmpty) {
          allSparqlWikiResults += nonUniqLabelResLines.maxBy(_.score)
        }


      } else println("Result empty")
      println("\nallSparqlWikiResults inside the loop : " + allSparqlWikiResults + "\n")

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
    //todo: currently, the sparql query returns up to 9 results to avoid overloading the server; this is currently defined
    //in the query in sparqlWrapper.py, but should be passed as a var.
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
    val globalVars = ExtractAndAlign.getGlobalVars(mentions, Some(Map.empty))
    val groundings = SeqOfWikiGroundings(globalVars.map(gv => WikiGrounding(gv.identifier, gv.groundings.getOrElse(Seq.empty))))
    write(groundings, indent = 4)
  }

}
