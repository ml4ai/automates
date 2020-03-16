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

//todo: pass the python query file from configs
//todo: document in wiki

case class sparqlResult(searchTerm: String, osvTerm: String, className: String, score: Option[Double], source: String = "OSV")

object sparqlResult {
  implicit val rw: ReadWriter[sparqlResult] = macroRW

}

case class Grounding(variable: String, groundings: Seq[sparqlResult])
object Grounding {
  implicit val rw: ReadWriter[Grounding] = macroRW
}

case class SeqOfGroundings(groundings: Seq[Grounding])
object SeqOfGroundings {
  implicit val rw: ReadWriter[SeqOfGroundings] = macroRW
}

object SVOGrounder {

  val config: Config = ConfigFactory.load()
  val sparqlDir: String = config[String]("grounding.sparqlDir")
  val currentDir: String = System.getProperty("user.dir")
  // ==============================================================================
  // QUERYING THE SCIENTIFIC VARIABLE ONTOLOGY (http://www.geoscienceontology.org/)
  // ==============================================================================

  def runSparqlQuery(term: String, scriptDir: String): String = {
    //todo: currently, the sparql query returns up to 9 results to avoid overloading the server; this is currently defined
    //in the query in sparqlWrapper.py, but should be passed as a var.
    val command = Seq("python", s"$currentDir/$scriptDir/sparqlWrapper.py", term)
    val process = Process(command, new File(s"$scriptDir"))
    process.!!
  }

  /* grounding using the ontology API (not currently used) */
  def groundWithAPI(term: String) = {
    val url = "http://34.73.227.230:8000/match_phrase/" + term + "/"
    scala.io.Source.fromURL(url)
  }
  /* grounding using the ontology API (not currently used) */
  def groundMentionWithAPI(mention: Mention) = {
    for (word <- mention.words) {
      println(groundWithAPI(word).mkString(""))
    }
  }

  // ======================================================
  //            GROUNDING METHODS
  // ======================================================

  /* grounds a seq of mentions and returns the var to grounding mapping */
  def groundMentionsWithSparql(mentions: Seq[Mention], k: Int): Map[String, Seq[sparqlResult]] = {
//    val groundings = mutable.Map[String, Seq[sparqlResult]]()
    val groundings = mentions.flatMap(m => groundOneMentionWithSparql(m, k))
    groundings.toMap
  }

  /* Grounding a sequence of mentions and return a pretty-printable json string*/
  def mentionsToGroundingsJson(mentions: Seq[Mention], k: Int): String = {
    val seqOfGroundings = SeqOfGroundings(groundDefinitions(mentions, k))
    write(seqOfGroundings, indent = 4)
  }

  /* grounding one mention; return a map from the name if the variable from the mention to its svo grounding */
  def groundOneMentionWithSparql(mention: Mention, k: Int): Map[String, Seq[sparqlResult]] = {

    val terms = getTerms(mention) //get terms gets nouns, verbs, and adjs, and also returns reasonable collocations (multi-word combinations), e.g., syntactic head of the mention + (>compound | >amod)
    if (terms.nonEmpty) {
      val resultsFromAllTerms = new ArrayBuffer[sparqlResult]()
      for (word <- terms.get) {
        val result = runSparqlQuery(word, sparqlDir)
        if (result.nonEmpty) {
          //each line in the result is a separate entry returned by the query:
          val resultLines = result.split("\n")
          //represent each returned entry/line as a sparqlResult and sort those by edit distance score (lower score is better)
          val sparqlResults = resultLines.map(rl => new sparqlResult(rl.split("\t")(0), rl.split("\t")(1), rl.split("\t")(2), Some(editDistance(rl.split("\t")(1), word)), "SVO")).sortBy(sr => sr.score)
          for (sr <- sparqlResults) resultsFromAllTerms += sr
        }
       resultsFromAllTerms.toArray
      }

      //RANKING THE RESULTS (//todo: there has to be a more efficient way)
      //getting all the results with same (minimal) score
      val onlyMinScoreResults = resultsFromAllTerms.filter(res => res.score == resultsFromAllTerms.map(r => r.score).min).toArray.distinct

      //the results where search term contains "_" or "-" should be ranked higher since those are multi-word instead of separate words
      val (multiWord, singleWord) = onlyMinScoreResults.partition(r => r.searchTerm.contains("_") || r.searchTerm.contains("-"))

      //this is the best results based on score and whether or not they are collocations
      val bestResults = if (multiWord.nonEmpty) multiWord else singleWord

      //return the best result first, then only the min score ones, and then all the rest; some may overlap thus distinct

      val allResults = (bestResults ++ onlyMinScoreResults ++ resultsFromAllTerms).distinct
      Map(mention.arguments("variable").head.text -> getTopK(allResults, k))
    } else Map(mention.arguments("variable").head.text -> Array(new sparqlResult("None", "None", "None", None)))
  }

  //ground a string (for API)
  def groundString(text:String): String = {
    val terms = getTerms(text)
    val resultsFromAllTerms = new ArrayBuffer[sparqlResult]()
    for (word <- terms) {
      val result = runSparqlQuery(word, sparqlDir)
      if (result.nonEmpty) {
        //each line in the result is a separate entry returned by the query:
        val resultLines = result.split("\n")
        //represent each returned entry/line as a sparqlResult and sort those by edit distance score (lower score is better)
        val sparqlResults = resultLines.map(rl => new sparqlResult(rl.split("\t")(0), rl.split("\t")(1), rl.split("\t")(2), Some(editDistance(rl.split("\t")(1), word)))).sortBy(sr => sr.score)
        resultsFromAllTerms += sparqlResults.head

      }
    }
    resultsFromAllTerms.mkString("")
  }

  // ======================================================
  //            SUPPORT METHODS
  // ======================================================

  /*takes a series of mentions, maps each variable in the definition mentions (currently the only groundable
  * type of mentions) to a sequence of results from the SVO ontology, and converts these mappings into an object
  * writable with upickle */
  def groundDefinitions(mentions: Seq[Mention], k: Int): Seq[Grounding] = {
    //sanity check to make sure all the passed mentions are def mentions
    val (defMentions, other) = mentions.partition(m => m matches "Definition")
    val groundings = groundMentionsWithSparql(defMentions, k)

    val groundingsObj =
      for {
        gr <- groundings

      } yield Grounding(gr._1, gr._2)

    groundingsObj.toSeq
  }

  def getTopK(results: Seq[sparqlResult], k: Int): Seq[sparqlResult] = {
    if (k < results.length) {
      val kResults = for (i <- 1 to k) yield results(i)
      kResults
    } else {
      results
    }
  }

  /*get the terms (single-and multi-word) from the mention to run sparql queries with;
  * only look at the terms in the definition mentions for now*/
  def getTerms(mention: Mention): Option[Seq[String]] = {
    println(mention.text)
    //todo: will depend on type of mention, e.g., for definitions, only look at the words in the definition arg, not var itself
    if (mention matches "Definition") {
      val terms = new ArrayBuffer[String]()
      val lemmas = mention.arguments("definition").head.lemmas.get
      val tags = mention.arguments("definition").head.tags.get
      for (i <- 0 to lemmas.length-1) {
        //disregard words  other than nouns, adjs, and verbs for now
        if (tags(i).startsWith("N") || tags(i).startsWith("J") || tags(i).startsWith("V")) {
          terms += lemmas(i)
        }
      }
      //the sparql query can't have spaces between words (can take words separated by underscores or dashes, so the compounds will include those)
      val compounds = getCompounds(mention.arguments("definition").head)
      if (compounds.nonEmpty) {
        for (c <- compounds.get) {
          terms += c
        }
      }
      Some(terms)
    } else None

  }

  //with strings, just take each word of the string as term---don't have access to all the ling info a mention has
  def getTerms(str: String): Seq[String] = {
    val terms = new ArrayBuffer[String]()
    //todo: get lemmas? pos? is it worth it running the processors?
    val termCandidates = str.split(" ")
    termCandidates
  }

  /*get multi-word combinations from the mention*/
  def getCompounds(mention: Mention): Option[Array[String]] = {

    val headWord = mention.synHeadLemma
    //todo: do we want terms other than syntactic head?
    val outgoing = mention.sentenceObj.dependencies.head.getOutgoingEdges(mention.synHead.get)
    //get indices of compounds or modifiers to the head word of the mention
    if (outgoing.exists(tuple => tuple._2 == "compound" || tuple._2 == "amod")) {
      val indicesOfCompoundToken = mention.sentenceObj.dependencies.head.getOutgoingEdges(mention.synHead.get).filter(tuple => tuple._2 == "compound" || tuple._2 == "amod").map(tuple => tuple._1)
      val compoundWords = new ArrayBuffer[String]()
      for (idx <- indicesOfCompoundToken) {
        val compoundWord = mention.sentenceObj.words.slice(idx, mention.synHead.get + 1).mkString(" ")
        val semHead = mention.semHeadLemma
        compoundWords.append(compoundWord.replace(" ", "_"))
        compoundWords.append(compoundWord.replace(" ", "-")) //todo: in the ontology, some terms are linked with a dash and some with underscore; should look for both, but find a better place for this (?)
      }

      Some(compoundWords.toArray)
    } else None

  }

  def editDistance(s1: String, s2: String): Double = {
    val dist = LevenshteinDistance.getDefaultInstance().apply(s1, s2).toDouble
    dist
  }

}
