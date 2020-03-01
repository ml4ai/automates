package org.clulab.grounding

import java.io.File

import upickle.default._
import org.apache.commons.text.similarity.LevenshteinDistance
import org.clulab.odin.{Attachment, Mention, SynPath}
import scala.collection.mutable.ArrayBuffer
import scala.sys.process.Process
import scala.collection.mutable
import upickle.default.{ReadWriter, macroRW}


//todo: produce a json for groundString
//todo: clean the code
//todo: pass the python query file from configs
//todo: add source for the grounding
//todo: check how this works with Seq[Mention]
//todo: document in wiki

case class sparqlResult(searchTerm: String, osvTerm: String, className: String, score: Option[Double], source: String = "OSV")

object sparqlResult {
  implicit val rw: ReadWriter[sparqlResult] = macroRW

}

case class Grounding(variable: String, gr: Seq[sparqlResult])
object Grounding {
  implicit val rw: ReadWriter[Grounding] = macroRW
}

case class SeqOfGroundings(groundings: Seq[Grounding])
object SeqOfGroundings {
  implicit val rw: ReadWriter[SeqOfGroundings] = macroRW
}

object SVOGrounder {

  // =====================================================
  // grounding using the ontology API (not currently used)
  // =====================================================

  /* grounding using the ontology API (not currently used) */
  def groundWithAPI(term: String) = {
    val url = "http://34.73.227.230:8000/match_phrase/" + term + "/"
    scala.io.Source.fromURL(url)
  }

  def groundMentionWithAPI(mention: Mention) = {
    for (word <- mention.words) {
      println(groundWithAPI(word).mkString(""))
    }
  }
  // ======================================================

  /* return a sequence of groundings for the given mention*/
  def groundMentionWithSparql(mention: Mention, k: Int): Seq[sparqlResult] = {

    val terms = getTerms(mention) //get terms gets nouns, verbs, and adjs, and also returns reasonable collocations, e.g., syntactic head of the mention + >compound
    if (terms.nonEmpty) {
      val resultsFromAllTerms = new ArrayBuffer[sparqlResult]()
      for (word <- terms.get) {
        val result = runSparqlQuery(word, "/home/alexeeva/Repos/automates/text_reading/sparql") //todo: pass through configs
        println("term: " + word + "\nresult: " + result.mkString(""))
        println("end of result")
        if (result.nonEmpty) {
          //each line in the result is a separate entry returned by the query:
          val resultLines = result.split(("\n"))
          //represent each returned entry/line as a sparqlResult and sort those by edit distance score (lower score is better)
          val sparqlResults = resultLines.map(rl => new sparqlResult(rl.split("\t")(0), rl.split("\t")(1), rl.split("\t")(2), Some(editDistance(rl.split("\t")(1), word)), "SVO")).sortBy(sr => sr.score)
          for (result <- sparqlResults) {
            println("==>" + result.searchTerm + " " + result.osvTerm + " " + result.className + " " + result.score)
          }
          for (sr <- sparqlResults) resultsFromAllTerms += sr
        }
       resultsFromAllTerms.toArray
      }

      //getting all the results with same (minimal) score
      val onlyMinScoreResults = resultsFromAllTerms.filter(res => res.score == resultsFromAllTerms.map(r => r.score).min).toArray.distinct

      //the results where search term contains "_" should be ranked higher since those are collocations instead of separate words
      val (collocation, singleWord) = onlyMinScoreResults.partition(r => r.searchTerm.contains("_"))
      //this is the best result based on score and whether or not it's a collocation
      val finalResult = if (collocation.nonEmpty) collocation else singleWord

      //return the best result first, then only the min score ones, and then all the rest; some may overlap thus distinct
      //todo: there has to be a more efficient way
      val allResults = finalResult ++ onlyMinScoreResults ++ resultsFromAllTerms
      getTopK(allResults.distinct, k)
    } else Array(new sparqlResult("None", "None", "None", None))
  }

  def getTopK(results: Seq[sparqlResult], k: Int): Seq[sparqlResult] = {
    if (k < results.length) {
      val kResults = for (i <- 1 to k) yield results(i)
      kResults
    } else {
      results
    }
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

  def getTerms(str: String): Seq[String] = {
    val terms = new ArrayBuffer[String]()
    //todo: get lemmas? is it worth it running the processors?
    val termCandidates = str.split(" ")
    termCandidates
  }

  /*get collocations from the mention*/
  def getCompounds(mention: Mention): Option[String] = {

    val headWord = mention.synHeadLemma
    //todo: do we want terms other than syntactic head?
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

  def groundMentionsWithSparql(mentions: Seq[Mention], k: Int): Map[String, Seq[sparqlResult]] = {
    val groundings = mutable.Map[String, Seq[sparqlResult]]()
    for (m <- mentions) {
      groundings += (m.arguments("variable").head.text -> groundMentionWithSparql(m, k))
    }
    groundings.toMap
  }


  //todo: curl requests for strings
  def groundString(text:String): String = {
    val terms = getTerms(text)
    val resultsFromAllTerms = new ArrayBuffer[sparqlResult]()
    for (word <- terms) {

      val result = runSparqlQuery(word, "/home/alexeeva/Repos/automates/text_reading/sparql")
//      println("term: " + word + "\nresult: " + result.mkString(""))
//      println("end of result")
      if (result.nonEmpty) {
        //each line in the result is a separate entry returned by the query:
        val resultLines = result.split(("\n"))
        //represent each returned entry/line as a sparqlResult and sort those by edit distance score (lower score is better)
        //todo: if several highest score and are the same 'osvTerm', return the class that is the lowest node in the ontology
        val sparqlResults = resultLines.map(rl => new sparqlResult(rl.split("\t")(0), rl.split("\t")(1), rl.split("\t")(2), Some(editDistance(rl.split("\t")(1), word)))).sortBy(sr => sr.score)
        for (result <- sparqlResults) {
          println("==>" + result.searchTerm + " " + result.osvTerm + " " + result.className + " " + result.score)
        }

        resultsFromAllTerms += sparqlResults.head

      }
    }
    resultsFromAllTerms.mkString("")
  }

  def groundDefinitions(mentions: Seq[Mention], k: Int): String = {
    //sanity check to make sure all the passed mentions are def mentions
    val (defMentions, other) = mentions.partition(m => m matches "Definition")
    val groundings = groundMentionsWithSparql(defMentions, k)

    val groundingsObj =
        for {
          gr <- groundings

        } yield Grounding(gr._1, gr._2)

    val seqOfGroundings = SeqOfGroundings(groundingsObj.toSeq)
    write(seqOfGroundings, indent = 4)
    }


}
