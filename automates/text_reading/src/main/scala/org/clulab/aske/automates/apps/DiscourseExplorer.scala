package org.clulab.aske.automates.apps

import java.io.PrintWriter
import java.util.regex.Pattern

import org.clulab.discourse.rstparser.{DiscourseTree, DiscourseUnit, RelationDirection}
import org.clulab.processors.Document
import org.clulab.processors.fastnlp.FastNLPProcessor
import org.clulab.processors.shallownlp.ShallowNLPProcessor

import scala.collection.mutable.ArrayBuffer
import scala.io.Source


/**
  * Created by gus on 8/5/14.
  */
class DiscourseExplorer {
  // withDiscourse must be set to true!
  lazy val processor = new FastNLPProcessor(withDiscourse = ShallowNLPProcessor.WITH_DISCOURSE)

  // generate only the annotations necessary for discourse parsing
  def mkDiscourseDoc(text:String):Document = {
    val doc = processor.mkDocument(text)
    processor.tagPartsOfSpeech(doc)
    processor.lemmatize(doc)
    processor.recognizeNamedEntities(doc)
    processor.parse(doc)
    processor.discourse(doc)
    doc.clear()
    doc
  }

  // annotate an existing Document
  def mkDiscourseAnnotations(doc:Document) {
    if (doc.sentences.head.tags == None) processor.tagPartsOfSpeech(doc)
    if (doc.sentences.head.lemmas == None) processor.lemmatize(doc)
    if (doc.sentences.head.syntacticTree == None) processor.parse(doc)
    if (doc.discourseTree == None) processor.discourse(doc)
    doc.clear()
  }

  /** This converts a list of DiscourseTuples to a list of DiscourseUnits, essentially from list to string format
    */
//  def mkDiscourseUnitsFromTuples(dts: List[DiscourseTuple]): List[DiscourseUnit] = {
//    val units = new ArrayBuffer[DiscourseUnit]
//    for (dt <- dts) {
//      val rel = dt.relation
//      val nuc = dt.nucText.mkString(" ")
//      val sat = dt.satText.mkString(" ")
//      val newTriplet = new DiscourseUnit(rel, nuc, sat)
//      units.append(newTriplet)
//    }
//    units.toList
//  }

  /** This is a function that prunes the lists of nucText and satText in the DiscourseTuple, allowing you to
    * control how deep/shallow to use for making DiscourseUnits
    */
  def topN(dts:List[DiscourseTuple], topN:Int):List[DiscourseTuple] = {
    val pruned = new Array[DiscourseTuple](dts.size)
    for (i <- 0 until dts.size){
      pruned(i) = prune(dts(i), topN)
    }
    pruned.toList
  }

  /**
    * Used by topN, keeps the topN items in the nucText and satText of a DiscourseTuple
    **/
  def prune(dt: DiscourseTuple, topN: Int): DiscourseTuple = {
    //if there are more than topN items in nucText, keep only topN
    val outNuc = if (dt.nucText.size > topN) {
      dt.nucText.slice(0, topN)
    } else dt.nucText

    //if there are more than topN items in satText, keep only topN
    val outSat = if (dt.satText.size > topN) {
      dt.satText.slice(0, topN)
    } else dt.satText

    //return the new, pruned discourse tuple
    new DiscourseTuple(dt.relation, outNuc, outSat, (-1, -1)) // no char offsets for some reason
  }


  /** This is the wrapper for the work - it calls findTextPairs on the root node and makes a final combined list of
    * DiscourseTuples which is returned
    */
  def findRootPairs(dt:DiscourseTree):List[DiscourseTuple] = {
    if (dt.isTerminal){
      // if tree consists of a single, terminal node, then there is no relation (no children) so make a dummy DiscourseTuple
      val outList = List[DiscourseTuple](new DiscourseTuple("NULL", List[String](dt.rawText), List[String](dt.rawText), dt.charOffsets))
      outList
    } else { //otherwise, go and recursively get the DiscourseTuples!
      val (tuple, others) = findTextPairs(dt)
      tuple :: others //adds the tuple to the list
    }

  }

  /** Recursively goes through the discourse tree to assemble all DiscourseTuples, bottom up, so each node
   is visited only once, each time called passes up the tuple for the current non-terminal node along with a
   growing list of intermediate results (from lower in the tree)
    */
  def findTextPairs(dt:DiscourseTree):(DiscourseTuple, List[DiscourseTuple]) = {

    //check to make sure that the node is non-terminal
    if (dt.isTerminal) throw new Exception("Cannot call findTextPairs on a terminal node!")

    //this currently makes the joint/equal weighting left child be a "nuc" and the right child be a "sat",
    //potentially not what we want in the end
    //TODO: revisit this and decide how we want to handle it!
    val (nuc, sat) = if(dt.relationDirection != RelationDirection.RightToLeft) {
      (dt.children(0), dt.children(1))
    } else (dt.children(1), dt.children(0))

    // Helper function designed to assemble the text from the children in text order (regardless of relationDirection)
    // to make current tuple
    def smush (child:DiscourseTree): (List[String], List[DiscourseTuple]) = {

      if (child.children == null || child.children.isEmpty) { //if nuc terminal
        (List(child.rawText), List())

      } else {
        val (currentTuple, otherTuples) = findTextPairs(child)
        // (concatenated nuc+sat text, current added onto the running list)
        // this if statement checks for direction so text is concatenated in text order
        if (child.relationDirection != RelationDirection.RightToLeft){
          (currentTuple.nucText ++ currentTuple.satText, currentTuple :: otherTuples)
        } else {
          (currentTuple.satText ++ currentTuple.nucText, currentTuple :: otherTuples)
        }
      }
    }

    val (nucReturn, nucOther) = smush(nuc)

    val (satReturn, satOther) = smush(sat)

    val dTpl = DiscourseTuple(dt.relationLabel, nucReturn, satReturn, dt.charOffsets)

    //(disc tuple for current node, list of others...)
    (dTpl, nucOther ++ satOther)
  }


  case class DiscourseTuple(relation:String, nucText:List[String], satText:List[String], offset:(Int, Int))

  //TODO: Add methods to explore discourseTree structure
  def findDiscoursePairs = findRootPairs _

  /**
    * Reads in the textbook sentences file, parses the section info,
    * each index is of format --> bk.ch.sect.subsect.line
    * in each section, concatenates the sentences, and returns a list of those concatenated strings, which will be the document
    * (i.e. returns a list of documents)
    * */
  def readFromTextbookFile(inputFilename:String, parseDepth:String): List[String] = {

    //read in the lines from the file and removes the section info
    val parsedLines: List[(String, String)] = Source.fromFile(inputFilename, "ISO-8859-1").getLines().map(line => parseTextbookLine(line, parseDepth)).toList
    val docs: Map[String, List[(String, String)]] = parsedLines.groupBy(pair => pair._1) // group by the first element of each tuple,
    // note the anonymous function syntax,
    // (argument => return_value)
    println("-- File read")
    //for each list in the outer list, map the second anon function, for each pair get 2nd elem, and make string
    docs.values.map(list => list.map(pair => pair._2).mkString(" ")).toList
  }

  // takes String line from textbook and returns tuple with (index, string)
  def parseTextbookLine(line:String, parseDepth:String = "subsection"):(String, String) = {
    println(line)
    val SPACE = Pattern.compile("\\s")
    val m = SPACE.matcher(line)
    if (m.find()) {
      val index = line.substring(0, m.start())
      val docID = extractIndexInfo(index, parseDepth)
      val sentence = line.substring(m.end()).trim() + "\n"
      (docID, sentence)
    } else throw new Exception ("ERROR: Space not found on line >>" + line)
  }

  //turns the index into something we can group by, flexible using depth:String parameter
  def extractIndexInfo(index:String, depth:String):String = {
    //println(index)
    //Format of index --> 1.2.3.4.5.6
    val indices = index.split("\\.")

    //find the splitting point which corresponds to desired parsing depth
    val depthIndex: Int = depth match {
      case "book" => 0
      case "chapter" => 1
      case "section" => 2
      case "subsection" => 3
      case "paragraph" => 4
    }

    var newString = ""
    for (i <- 0 until Math.min(depthIndex, indices.size)){
      newString += indices(i) + "."
    }
    //println ("NEWSTRING: " + newString)
    return newString

  }

  // Takes the output of findDiscoursePairs and returns an Array of (relation, nucLemmas, satLemmas)
//  def toLemmas(dtPairs:List[DiscourseTuple]):Array[DiscourseUnit] = {
//
//    //lemmatize text
//    def lemmatizeText(text:String):String = {
//      val doc = processor.mkDocument(text)
//      processor.lemmatize(doc)
//      val lemmas = for (s <- doc.sentences) yield s.lemmas.get.mkString(" ")
//      lemmas.mkString(" ")
//    }
//
//    val dtLemmaPairs = new ArrayBuffer[DiscourseUnit]
//    for (pair <- dtPairs) {
//      val rel = pair.relation
//      val nucLemmas = lemmatizeText(pair.nucText.mkString(" "))
//      val satLemmas = lemmatizeText(pair.satText.mkString(" "))
//      dtLemmaPairs += new DiscourseUnit(rel, nucLemmas, satLemmas)
//    }
//    dtLemmaPairs.toArray
//  }

  /*
    * Load/Save Methods
  */
//  //TODO: make a load method which will load up an Array[DiscourseUnit] and then refactor this as save(), alternative instantiation as unnested list/array
//  def saveDiscourseUnits(discourseUnits:List[List[DiscourseUnit]], filenamePrefix:String){
//    val pw = new PrintWriter(filenamePrefix)
//
//    discourseUnits.foreach(list => list.foreach(du => saveDiscourseUnit(pw, du)))
//    pw.close()
//
//  }

  def saveText(filename:String, sectionTexts:List[String]){
    val pw = new PrintWriter(filename)
    sectionTexts.foreach(item => pw.write(item + "\n"))
    pw.close()
  }

  def printTrees(docs:List[Document], fn:String){
    val pw = new PrintWriter(fn)
    for (doc <- docs){
      pw.write(doc.discourseTree.toString)
    }
    pw.close()
  }

//  def saveDiscourseUnit(pw:PrintWriter, du:DiscourseUnit){
//    pw.write("RELATION: " + du.relation + "\n")
//    pw.write("NUC: " + du.nucText + "\n")
//    pw.write("SAT: " + du.satText + "\n")
//  }

//  def loadDiscourseUnits(filename:String, debug:Boolean = false):Array[DiscourseUnit] = {
//    val relns = new ArrayBuffer[String]
//    val nucs = new ArrayBuffer[String]
//    val sats = new ArrayBuffer[String]
//    val parsedDiscourseTexts = new ArrayBuffer[DiscourseUnit]()                           // Array of Question/Answer pairs to build
//
//    debugPrint (" * Loading Discourse Units: started... ", debug)
//    debugPrint (" * \tparsing file (filename: " + filename + ").", debug)
//
//    if (filename == null) {
//      throw new RuntimeException ("ERROR: DiscourseExplorer.loadDiscourseUnits: filename passed is null.  exiting... ")
//    }
//
//    val source = scala.io.Source.fromFile(filename, "ISO-8859-1")
//    val lines = source.getLines()
//    val SPACE = Pattern.compile("\\s")
//    for (line <- lines){
//      val m = SPACE.matcher(line)
//      if (m.find()) {
//        val lineType = line.substring(0, m.start())
//        val sentence = line.substring(m.end()).trim()
//        lineType match {
//          case "RELATION:" => relns.append(sentence)
//          case "NUC:" => nucs.append(sentence)
//          case "SAT:" => sats.append(sentence)
//        }
//      }
//    }
//
//    //check to make sure there are complete discourse units
//    val sizes = Array[Int](relns.size, nucs.size, sats.size).sorted
//    val lastComplete = sizes(0)
//
//    for (i <- 0 until lastComplete){
//      val dt = new DiscourseUnit(relns(i), nucs(i), sats(i))
//      parsedDiscourseTexts.append(dt)
//    }
//
//    debugPrint (s" * Finished loading Discourse Units from $filename... ", debug)
//
//    parsedDiscourseTexts.toArray
//  }

  // Takes an array of Files and parses each into DiscourseUnits, returns an array with the desired DiscourseUnits
//  def makeDiscourseUnitsArray(fileArray:Array[String], includedRelations:Array[String], printRelations:Boolean):Array[DiscourseUnit] = {
//    //for each file, instantiate the DiscourseUnits and make a master list, only keep the relations we're interested in
//    val discourseUnits = new ArrayBuffer[DiscourseUnit]
//
//    for (f <- fileArray){
//      println (s"\tReading discourse tuples from $f")
//      //Get the DiscourseUnits
//      val dusTemp = loadDiscourseUnits(f)
//      for (du <- dusTemp){
//        //if it's a relation we want...
//        if (includedRelations.contains(du.relation.toLowerCase) | includedRelations.contains("all")){
//          if (printRelations) {
//            println(s"\t\tIncluded relation: ${du.relation}")
//          }
//          //Add it to the array
//          discourseUnits.append(du)
//        } else if (printRelations) {
//          println (s"\t\tExcluded relation: ${du.relation}")
//        }
//
//      }
//    }
//    discourseUnits.toArray
//  }

  /*
    * Helper Methods
   */

  @inline
  def debugPrint(string: String, debug:Boolean) {
    if (debug) println(string)
  }

}


