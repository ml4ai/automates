
import org.apache.spark.sql.{SaveMode, SparkSession}

// using the code from here: https://sparkbyexamples.com/spark/spark-convert-parquet-file-to-json/


object ParquetToJson extends App {

  val spark: SparkSession = SparkSession.builder()
    .master("local[1]")
    .appName("SparkByExamples.com")
    .getOrCreate()

//  spark.sparkContext.setLogLevel("ERROR")

  //read parquet file
  val df = spark.read.format("parquet")
    .load("/media/alexeeva/ee9cacfc-30ac-4859-875f-728f0764925c/storage/automates-related/double_epidemic_model_COSMOS/documents.parquet")
  df.show()
  df.printSchema()

  //convert to json
  df.write.mode(SaveMode.Overwrite)
    .json("/media/alexeeva/ee9cacfc-30ac-4859-875f-728f0764925c/storage/automates-related/double_epidemic_model_COSMOS/documents.json")
}