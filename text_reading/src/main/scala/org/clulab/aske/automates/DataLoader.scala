package org.clulab.aske.automates

import java.io.File
import ai.lum.common.FileUtils._
import org.clulab.utils.FileUtils.{findFiles, getTextFromFile}
import org.clulab.aske.automates.scienceparse.ScienceParseClient.mkDocument


/**
  * This DataLoader abstract class is intended to be able to load information from files, with each file providing
  * a sequence of Strings.
  */
abstract class DataLoader {
  val extension: String
  def loadFile(f: File): Seq[String]
  def loadFile(filename: String): Seq[String] = loadFile(new File(filename))
//  // defaultExtension can always be overridden, but will hopefully make calls to this method easier...?
//  def loadCollection(collectionDir: String, extension: String = defaultExtension): Seq[Seq[String]] = findFiles(collectionDir, extension).map(loadFile)
}

object DataLoader {

  // Select the kind of data loader you want,
  // todo: (revisit?) here we are working on scientific papers, so if it's json here we assume it's from science parse
  def selectLoader(s: String): DataLoader = {
    s match {
      case "txt" => new PlainTextDataLoader
      case "json" => new ScienceParsedDataLoader
    }
  }
}


class ScienceParsedDataLoader extends DataLoader {
  /**
    * Loader for documents which have been pre-processed with science parse (v1).  Each file contains a json representation
    * of the paper sections, here we will return the strings from each section as a Seq[String].
    *
    * @param f the File being loaded
    * @return string content of each section in the parsed pdf paper (as determined by science parse)
    */
  def loadFile(f: File): Seq[String] = {
    // todo: this approach should like be revisited to handle sections more elegantly, or to omit some, etc.
    val scienceParseDoc = mkDocument(f)
    scienceParseDoc.sections.map(_.text)
  }
  override val extension: String = "json"
}


class PlainTextDataLoader extends DataLoader {
  /**
    * Loader for text files.  Here we will return the content of the file as a Seq[String] (with length 1).
    *
    * @param f the File being loaded
    * @return string content of file (wrapped in sequence)
    */
  def loadFile(f: File): Seq[String] = Seq(getTextFromFile(f))
  override val extension: String = "txt"
}



//object Testy {
//  def main(args: Array[String]): Unit = {
//    val dir = args(0)
//    val loader = new ScienceParsedDataLoader
//    val files = findFiles(dir, "json")
//    files foreach { f =>
//      val doc = loader.loadFile(f)
//      println(s"Filename: ${f.getBaseName}")
//      println(doc.head)
//      println()
//    }
//  }
//}