package org.clulab.aske.automates.apps
import ai.lum.common.ConfigFactory

import java.io.File
import ai.lum.common.FileUtils._
import org.clulab.aske.automates.data.CosmosJsonDataLoader
import org.clulab.aske.automates.scienceparse.ScienceParseClient
//import org.apache.spark.sql.SparkSession
object ForMethodTesting {
  def main(args: Array[String]): Unit = {

    val config = ConfigFactory.load()
    println(config)
    println("HEREEE: " + org.apache.commons.text.StringEscapeUtils.unescapeJava("(2) Eeq = s s + \\u03b3 \\u03bb where " +
      "Rnday is daily surface net radiation (in J m\\u22122 day\\u22121) and \\u03bb is the latent heat of vaporization" +
      " (in J kg\\u22121)"))
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