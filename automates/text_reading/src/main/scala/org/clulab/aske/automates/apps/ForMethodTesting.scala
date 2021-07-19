package org.clulab.aske.automates.apps
import ai.lum.common.ConfigFactory

import java.io.File
import ai.lum.common.FileUtils._
import org.clulab.aske.automates.data.CosmosJsonDataLoader
import org.clulab.aske.automates.scienceparse.ScienceParseClient
import org.clulab.embeddings.word2vec.Word2Vec
import org.clulab.grounding.SVOGrounder.{editDistanceNormalized, groundTerms, rankAndReturnSVOGroundings, runSparqlQuery, sparqlDir}
import org.clulab.grounding.{sparqlResult, wikidataGrounder}
import org.clulab.utils.Sourcer
import ai.lum.common.ConfigUtils._
import org.clulab.processors.fastnlp.FastNLPProcessor

import scala.collection.mutable.ArrayBuffer
import scala.sys.process.Process
//import org.apache.spark.sql.SparkSession
object ForMethodTesting {
  def main(args: Array[String]): Unit = {

    val config = ConfigFactory.load()
    val vectors: String = config[String]("alignment.w2vPath")
    println("vectors: " + vectors)
    val w2v = new Word2Vec("/Users/alexeeva/Repos/automates/automates/text_reading/src/main/resources/vectors.txt", None)



    def runSparqlQuery(term: String, scriptDir: String): String = {
      //todo: currently, the sparql query returns up to 9 results to avoid overloading the server; this is currently defined
      //in the query in sparqlWrapper.py, but should be passed as a var.
      val command = Seq("python", s"$sparqlDir/sparqlWikiWrapper.py", term)
      val process = Process(command, new File(s"$scriptDir"))
      process.!!
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

//    val grounded = groundTerms(Seq("crop"))
//    for (g <- grounded) println("->" + g)

//    val groundings = groundVarTermsToSVO("Cr", Seq("Tree", "crop"), 5)
//    for (g <- groundings) {
//      println("->>" + g)
//    }

    val proc = new FastNLPProcessor()
//    val text = "The farmer grows crops in an agricultural district of Brittany."
    val text = "I went to get a haircut and the barber gave me a crop."
    val sent = proc.annotate(text)
    val grounder = wikidataGrounder
    val wikiGroundings = grounder.groundTermsToWikidataRanked("Cr", Seq("crop"), sent.sentences.head.words, w2v, 10).getOrElse("No groundings")

    println(">>>" + wikiGroundings)

//    println(config)
//    println("HEREEE: " + org.apache.commons.text.StringEscapeUtils.unescapeJava("(2) Eeq = s s + \\u03b3 \\u03bb where " +
//      "Rnday is daily surface net radiation (in J m\\u22122 day\\u22121) and \\u03bb is the latent heat of vaporization" +
//      " (in J kg\\u22121)"))
    //    val mySpark = SparkSession
    //      .builder()
    //      .appName("Spark SQL basic example")
    //      .config("spark.some.config.option", "some-value")
    //      .getOrCreate()
    // For implicit conversions like converting RDDs to DataFrames
    //import mySpark.implicits._
    //        val loader = new CosmosJsonDataLoader
    //        val loaded = loader.loadFile("/Users/alexeeva/Desktop/LPJmL_LPJmL4 – a dynamic global vegetation model with managed land – Part 1 Model description--COSMOS-data.json")
    //    //
    //        for (s <- loaded) println("->" + s + "\n")
    //    val parquetFileDF = spark.read.parquet("people.parquet")
  }
}