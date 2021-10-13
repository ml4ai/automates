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
import org.clulab.aske.automates.grfn.GrFNParser
//todo: pass the python query file from configs
//todo: document in wiki

case class sparqlResult(searchTerm: String, osvTerm: String, className: String, score: Option[Double], source: String = "OSV")

object sparqlResult {
  implicit val rw: ReadWriter[sparqlResult] = macroRW

}

case class SVOGrounding(variable: String, groundings: Seq[sparqlResult])
object SVOGrounding {
  implicit val rw: ReadWriter[SVOGrounding] = macroRW
}

case class SeqOfGroundings(groundings: Seq[SVOGrounding])

object SeqOfGroundings {
  implicit val rw: ReadWriter[SeqOfGroundings] = macroRW
}

object SVOGrounder {

  val config: Config = ConfigFactory.load()
  val sparqlDir: String = config[String]("grounding.sparqlDir")
//  val currentDir: String = System.getProperty("user.dir")

  // ==============================================================================
  // QUERYING THE SCIENTIFIC VARIABLE ONTOLOGY (http://www.geoscienceontology.org/)
  // ==============================================================================

  def runSparqlQuery(term: String, scriptDir: String): String = {
    //todo: currently, the sparql query returns up to 9 results to avoid overloading the server; this is currently defined
    //in the query in sparqlWrapper.py, but should be passed as a var.
    val command = Seq("python", s"$sparqlDir/sparqlWrapper.py", term)
    val process = Process(command, new File(s"$scriptDir"))
    process.!!
  }

  //todo: finish the methods if they are to be used
  /** grounding using the ontology API (not currently used) */
  def groundToSVOWithAPI(term: String) = {
    val url = "http://34.73.227.230:8000/match_phrase/" + term + "/"
    scala.io.Source.fromURL(url)
  }
  /** grounding using the ontology API (not currently used) */
  def groundMentionToSVOWithAPI(mention: Mention) = {
    for (word <- mention.words) {
      groundToSVOWithAPI(word)
    }
  }

  // ======================================================
  //            SVO GROUNDING METHODS
  // ======================================================

  /** grounds a seq of mentions and returns the var to grounding mapping */
  def groundMentionsWithSparql(mentions: Seq[Mention], k: Int): Map[String, Seq[sparqlResult]] = {
//    val groundings = mutable.Map[String, Seq[sparqlResult]]()
    val groundings = mentions.flatMap(m => groundOneMentionWithSparql(m, k))

    groundings.toMap
  }

  /** Grounding a sequence of mentions and return a pretty-printable json string*/
  def mentionsToGroundingsJson(mentions: Seq[Mention], k: Int): String = {
    val seqOfGroundings = SeqOfGroundings(groundDescriptionsToSVO(mentions, k))
    write(seqOfGroundings, indent = 4)
  }

  /** produces svo groundings for text_var link elements*/
  def groundHypothesesToSVO(hypotheses: Seq[ujson.Obj], k: Int): Option[Map[String, Seq[sparqlResult]]] = {
    val textVarLinkElements = new ArrayBuffer[ujson.Value]()
    for (hyp <- hypotheses) {
      for (el <- hyp.obj) {
        if (el._1.startsWith("element") && el._2.obj("type").str == "text_var" ) {
          if (el._2.obj("svo_query_terms").arr.nonEmpty) {
            textVarLinkElements.append(el._2)
          }
        }
      }
    }

//    val shorterThingToGroundForDebugging = textVarLinkElements.slice(0, 4)

    //dict mapping a variable with the terms from all the text_var link elements with this variable
    val toGround = mutable.Map[String, Seq[String]]()

    //here, include the pdf name in the variable lest we concat variables from different papers (they may not refer to the same concept)
    for (hyp <- textVarLinkElements.distinct) {
      val variable = hyp.obj("content").str
      val pdfNameRegex = ".*?\\.pdf".r
      val source = hyp.obj("source").str.split("/").last
      val pdfName =  pdfNameRegex.findFirstIn(source).getOrElse("Unknown")
      val terms = hyp.obj("svo_query_terms").arr.map(_.str)
      if (toGround.keys.toArray.contains(variable)) {
        val currentTerms = toGround(variable)
        val updatesTerms =  (currentTerms ++ terms.toList).distinct
        toGround(variable + "::" + pdfName) = updatesTerms
      } else {
        toGround(variable + "::" + pdfName) = terms
      }
    }

    val varGroundings = mutable.Map[String, Seq[sparqlResult]]()

    //ground to svo
    for (varTermTuple <- toGround) {
      val oneHypGrounding = groundVarTermsToSVO(varTermTuple._1, varTermTuple._2, k)
      if (oneHypGrounding.isDefined) {
        oneHypGrounding.get.keys.foreach(key => varGroundings.put(key, oneHypGrounding.get(key)))
      }
    }
    if (varGroundings.nonEmpty) {
      return  Some(varGroundings.toMap)

    } else None
  }

  def groundVarTermsToSVO(variable: String, terms: Seq[String], k: Int):  Option[Map[String, Seq[sparqlResult]]] = {
    // ground terms from one variable
    println(s"grounding variable $variable")


    if (terms.nonEmpty) {
      val resultsFromAllTerms = groundTerms(terms)
      val svoGroundings = rankAndReturnSVOGroundings(variable, k, resultsFromAllTerms)
//      println(s"svo groundings: $svoGroundings")
      if (svoGroundings.isDefined) {
        return svoGroundings
      } else None



    } else None
  }

  def groundTermsToSVOandRank(variable: String, terms: Seq[String], k: Int): ujson.Arr = {
    val resultsFromAllTerms = groundTerms(terms)
    val svoGroundings = rankAndReturnSVOGroundings(variable, k, resultsFromAllTerms)
    if (svoGroundings.isDefined) {
      return ujson.Arr(svoGroundings.get.map(_._2).flatten.map(sr => GrFNParser.sparqlResultTouJson(sr)))


//
    } else ujson.Arr("None")

  }

  /** grounding one mention; return a map from the name if the variable from the mention to its svo grounding */
  //todo: this should also probably return and option
  def groundOneMentionWithSparql(mention: Mention, k: Int): Map[String, Seq[sparqlResult]] = {
    println("Started grounding a mention: " + mention.arguments("description").head.text + " | var text: " + mention.arguments("variable").head.text + " " + "| Label: " + mention.label)
    val terms = getTerms(mention).get.filter(t => t.length > 1) //get terms gets nouns, verbs, and adjs, and also returns reasonable collocations (multi-word combinations), e.g., syntactic head of the mention + (>compound | >amod)
//    println("search terms: " + terms.mkString(" "))
    if (terms.nonEmpty) {
      val resultsFromAllTerms = groundTerms(terms)

      val variable = mention.arguments("variable").head.text
      val svoGroundings = rankAndReturnSVOGroundings(variable, k, resultsFromAllTerms)
      if (svoGroundings.isDefined) {
        return svoGroundings.get
      } else Map(mention.arguments("variable").head.text -> Array(new sparqlResult("None", "None", "None", None)))


    } else Map(mention.arguments("variable").head.text -> Array(new sparqlResult("None", "None", "None", None)))
  }

  def groundTerms(terms: Seq[String]): Seq[sparqlResult] = {
    val resultsFromAllTerms = new ArrayBuffer[sparqlResult]()
    for (word <- terms) {
      val result = runSparqlQuery(word, sparqlDir)

      if (result.nonEmpty) {
        //each line in the result is a separate entry returned by the query:
        val resultLines = result.split("\n")
        //represent each returned entry/line as a sparqlResult and sort those by edit distance score (lower score is better)

        val sparqlResults = resultLines.map(rl => new sparqlResult(rl.split("\t")(0).trim(), rl.split("\t")(1).trim(), rl.split("\t")(2).trim(), Some(editDistanceNormalized(rl.split("\t")(1).trim(), word)), "SVO")).sortBy(sr => sr.score).reverse

        for (sr <- sparqlResults) resultsFromAllTerms += sr
      }
    }
    resultsFromAllTerms
  }


  def rankAndReturnSVOGroundings(variable: String, k: Int, resultsFromAllTerms: Seq[sparqlResult]): Option[Map[String, Seq[sparqlResult]]] = {
    resultsFromAllTerms.toArray
    //RANKING THE RESULTS
    //getting all the results with same (maximum) score
    val onlyMaxScoreResults = resultsFromAllTerms.filter(res => res.score == resultsFromAllTerms.map(r => r.score).max).toArray.distinct

    //the results where search term contains "_" or "-" should be ranked higher since those are multi-word instead of separate words
    val (multiWord, singleWord) = onlyMaxScoreResults.partition(r => r.searchTerm.contains("_") || r.searchTerm.contains("-"))

    //this is the best results based on score and whether or not they are collocations
    val bestResults = if (multiWord.nonEmpty) multiWord else singleWord

    //return the best results first, then only the max score ones, and then all the rest; some may overlap thus distinct
    val allResults = (bestResults ++ onlyMaxScoreResults ++ resultsFromAllTerms).distinct
    if (allResults.nonEmpty) {
      //      println("len all results: " + allResults.length)
      //      for (r <- allResults) println("res: " + r)
      Some(Map(variable -> getTopK(allResults, k)))
    } else None
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

  /**takes a series of mentions, maps each variable/identifier in the description mentions (currently the only groundable
  * type of mentions) to a sequence of results from the SVO ontology, and converts these mappings into an object
  * writable with upickle */
  def groundDescriptionsToSVO(mentions: Seq[Mention], k: Int): Seq[SVOGrounding] = {
    //sanity check to make sure all the passed mentions are descr mentions
    val (descrMentions, other) = mentions.partition(m => m matches "Description")
    val groundings = groundMentionsWithSparql(descrMentions, k)
    val groundingsObj =
      for {
        gr <- groundings

      } yield SVOGrounding(gr._1, gr._2)
    groundingsObj.toSeq
  }

  def getTopK(results: Seq[sparqlResult], k: Int): Seq[sparqlResult] = {
    if (k < results.length) {
      results.slice(0,k)
    } else {
      results
    }
  }

  /*get the terms (single-and multi-word) from the mention to run sparql queries with;
  * only look at the terms in the description mentions for now*/
  def getTerms(mention: Mention): Option[Seq[String]] = {
    //todo: will depend on type of mention, e.g., for descriptions, only look at the words in the description arg, not var itself
//    println("Getting search terms for the mention")
    if (mention matches "Description") {
      val terms = new ArrayBuffer[String]()

      //the sparql query can't have spaces between words (can take words separated by underscores or dashes, so the compounds will include those)
      val compounds = getCompounds(mention.arguments("description").head)

      if (compounds.nonEmpty) {
        for (c <- compounds.get) {
          if (c.length > 0) { //empty string results halted the process
            terms += c
          }
        }
      }

//      for (t <- compounds) println(s"term from compounds ${t.mkString("|")} ${t.length}")
      //if there were no search terms found by getCompounds, just ground any nouns in the description
      if (terms.isEmpty) {
        //get terms from words
        val lemmas = mention.arguments("description").head.lemmas.get
        val tags = mention.arguments("description").head.tags.get
        for (i <- lemmas.indices) {
          //disregard words  other than nouns for now fixme: add other parts of speech?
          //disregard words that are too short---unlikely to ground well to svo
          if (lemmas(i).length > 3) {
//            println("one term; checking length: " + lemmas(i).length + " " + lemmas(i))
            if (tags(i).startsWith("N")) {
              terms += lemmas(i)
            }
          }
        }
      }

      val finalTerms = terms.map(t => t.filter(ch => ch.isLetter || ch.toString == "-" || ch.toString == "_"))
//      println(finalTerms)
      Some(finalTerms.sortBy(_.length))
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
    val compoundWords = new ArrayBuffer[String]()
    val headWord = mention.synHeadLemma.get
    if (headWord.trim().length > 3 && headWord.trim().count(_.isLetter) > 0) { //don't ground words that are too short---too many false pos from svo and many are variables; has to contain letters
      compoundWords.append(headWord)
      //todo: do we want terms other than syntactic head?
      val outgoing = mention.sentenceObj.universalEnhancedDependencies.head.getOutgoingEdges(mention.synHead.get)
      //get indices of compounds or modifiers to the head word of the mention
      val outgoingNodes = outgoing.map(o => o._1)

        //check if two previous words are parts of a compound---two words window was chosen based on seen examples
        for (i <- 1 to 2) {
          val idxToCheck = mention.synHead.get - i
          if (outgoingNodes.contains(idxToCheck)) {
            //ideally need to add an nmod_of here; would require checking cur word + 2-3;
            if (outgoing.exists(item => item._1 == idxToCheck && (item._2 == "compound" || item._2 == "amod"))) {

              val newComp = mention.sentenceObj.words.slice(idxToCheck,mention.synHead.get + 1).filter(w => w.count(_.isLetter) == w.length).mkString("_")
              //fixme: if grounder not too slow, also get compounds separated by "-" bc those also occur in SVO
              compoundWords.append(newComp)
            }
          }

        }

//      println("compound words: " + compoundWords.distinct.mkString(" "))
      Some(compoundWords.toArray.distinct)
    } else None


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

}
