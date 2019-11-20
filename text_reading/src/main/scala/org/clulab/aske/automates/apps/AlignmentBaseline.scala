package org.clulab.aske.automates.apps
import ai.lum.common.FileUtils._
import java.io.{File, PrintWriter}
import java.nio.file.{Files, Paths}

import ai.lum.common.ConfigUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.aske.automates.data.DataLoader
import org.clulab.aske.automates.OdinEngine
import org.clulab.odin.Mention
import org.clulab.processors.fastnlp.FastNLPProcessor
import org.clulab.utils.FileUtils

import scala.collection.mutable
import scala.collection.mutable.ArrayBuffer
import scala.io.Source


//todo: add eval:
//crop - done
//run through eq to latex
//read those equations in
//deal with not all gold files being actually there (unlikely but possible)--- should be fine if indices in json dir are correct/correspond to order/indices of equationFromTranslator.txt
//need to get gold files


class AlignmentBaseline() {
  def process() {


    //getting configs and such (borrowed from ExtractAndAlign):

    val config: Config = ConfigFactory.load()
    //in case we use the text from pdfMiner
    //val fullText = readInPdfMinedText("/home/alexeeva/Repos/automates/text_reading/input/LREC/Baseline/pdfMined/mined.txt")



    //this is where the latex equation files are
    val eqFileDir = config[String]("apps.baselineEquationDir")

    val eqFile = Source.fromFile("/home/alexeeva/Repos/automates/text_reading/input/LREC/Baseline/equations/equationsFromTranslator.txt")
    val eqLines = eqFile.getLines().toArray //all equations from file
    eqFile.close()


    val testEq = eqLines.head
    println(testEq.replace(" ", "") + "<<<")







    //latex symbols/fonts (todo: add more):
    //these will be deleted from the latex equation to get to the values
    val mathSymbolsFile = Source.fromFile("/home/alexeeva/Repos/automates/text_reading/src/main/resources/AlignmentBaseline/mathSymbols.tsv")
    val mathSymbols = mathSymbolsFile.getLines().toArray.filter(_.length > 0).sortBy(_.length).reverse
    mathSymbolsFile.close()

    //get the greek letters and their names
    val greekLetterFile = Source.fromFile("/home/alexeeva/Repos/automates/text_reading/src/main/resources/AlignmentBaseline/greek2words.tsv")
    val greekLetterLines = greekLetterFile.getLines()

    //these will be used to map greek letters to words and back
    val greek2wordDict = mutable.Map[String,String]()
    val word2greekDict = mutable.Map[String,String]()

    for (line <- greekLetterLines) {
      val splitLine = line.split("\t")
      greek2wordDict += (splitLine.head -> splitLine.last)
      word2greekDict += (splitLine.last -> splitLine.head)
    }
    greekLetterFile.close()

    //some configs and files to make sure this runs (borrowed from ExtractAndAlign
    val textConfig: Config = config[Config]("TextEngine")
    val textReader = OdinEngine.fromConfig(textConfig)
    val commentReader = OdinEngine.fromConfig(config[Config]("CommentEngine"))
    val inputDir = config[String]("apps.baslineInputDirectory")
    val inputType = config[String]("apps.inputType")
    val dataLoader = DataLoader.selectLoader(inputType) // txt, json (from science parse), pdf supported
    val files = FileUtils.findFiles(inputDir, dataLoader.extension).sorted

    //this is where the gold data is stored
    val goldDir = config[String]("apps.baselineGoldDir")






//    println("ZEROth " + eqLines(0))


//    for (e <- eqLines) println(e)
    //Use this to copy the pdfs for which we have the gold annotation (supposedly have)
//    val goldFileNames = getAnnotatedFileNamesFromTSV("input/LREC/Baseline/progressTSV/AnnotationProgressNov13.tsv")

//    for (name <- goldFileNames) copyPdfsAndTSVs(name)

    val file2FoundMatches = files.par.flatMap { file =>  //should return sth like Map[fileId, (equation candidate, text candidate) ]

      print("============\n" + "Index of file " + files.indexOf(file) + file.toString() +"\n")
      println("equation: " + eqLines(files.indexOf(file)).replace(" ", "") + "\n")
      println("filename " +  file.toString())

      //gold:
      //fixme: for now, it's a random gold file; switch to real gold files
      val goldMap = processOneAnnotatedEquation(new File("/home/alexeeva/Repos/automates/text_reading/input/LREC/Baseline/gold/sample/1801.00077_equation0004.json"))

//      println("+++++++++++++")
//      println("Gold data:")
//      for (k <- goldMap) println(k)
//      println("+++++++++++++")




      //for every file, get the text of the file
      val texts: Seq[String] = dataLoader.loadFile(file)
//    //todo: change greek letter in mentions to full words
//      //extract the mentions
      val textMentions = texts.flatMap(text => textReader.extractFromText(text, filename = Some(file.getName)))
      //only get the definition mentions
      val textDefinitionMentions = textMentions.seq.filter(_ matches "Definition")

      //this is in case we extract from the text we get from pdfMiner
//      val textDefinitionMentions = textReader.extractFromText(fullText, true, Some("somefile")).filter(_ matches("Definition"))

//      println("=====all definition mentions from text=====")
//      for (td <- textDefinitionMentions) println(td.text)
//      println("============================")

//      val equationName = eqFileDir.toString + file.toString.split("/").last.replace("json","txt")
//      println("Equation fequationName + "<--")
//      val equationStr = getEquationString(equationName, word2greekDict.toMap)

      val equationStr = eqLines(files.indexOf(file)).replace(" ", "")
      println("EQ STRING: " + equationStr)
      val allEqVarCandidates = getAllEqVarCandidates(equationStr)


      val latexTextMatches = getLatexTextMatches(textDefinitionMentions, allEqVarCandidates, mathSymbols, greek2wordDict.toMap, goldMap)
      println("+++++++++")
      for (m <- latexTextMatches) println("Match: " + m._1 + " " + m._2 + " " + file.toString)
      println("++++++++++++\n")
      latexTextMatches
    }
//    println("==================")
//    println("MATCHES:")
//    for (m <- file2FoundMatches) println(s"${m._1}, ${m._2}")
//    println("==================")
  }

  def readInPdfMinedText(path2File: String): String = {
    val textArr = new ArrayBuffer[String]()
    val file = Source.fromFile("./input/LREC/Baseline/pdfMined/mined.txt")
    val lines = file.getLines().toArray
    file.close()
    val pattern = ">(.{1})</text".r
    for (line <- lines) if (line.endsWith("</text>")){
      if (line.matches("<text.*>.{1}</text>")) {
        val char = pattern.findAllIn(line).group(1)
        textArr.append(char)
        //      println(char)

      } else {
        textArr.append(" ")

      }
    }

    textArr.mkString("")

  }

  def getLatexTextMatches(textDefinitionMentions: Seq[Mention], allEqVarCandidates: Seq[String], mathSymbols: Seq[String], greek2wordDict: Map[String, String], goldMap: Map[String, Seq[String]]): Seq[(String, String)] = {

    //this is just a match between the extracted var/def and the gold string--no boxes, no latex
    var goldTextVarMatch = 0
    var goldTextDefMatch = 0

    //for every extracted var-def var, find the best matching latex candidate var by iteratively replacing math symbols until the variables match up; out of those, return max length with matching curly brackets

    //all the matches from one file name will go here:1
    val latexTextMatches = new ArrayBuffer[(String, String)]()
    //for every extracted mention
    for (m <- textDefinitionMentions) {
      //rudimentary eval, just comparing extracted text mention and the values in gold data
//      if (goldMap.keys.toList.contains(m.arguments("variable").head.text)) {
//        goldTextVarMatch += 1
//       // println("-->" + m.text)
//
//        if (goldMap(m.arguments("variable").head.text).contains(m.arguments("definition").head.text)) goldTextDefMatch += 1
//      }

      //best candidates, out of which we'll take the max (to account for some font info
      val bestCandidates = new ArrayBuffer[String]()
      //for every candidate eq var
      for (cand <- allEqVarCandidates) {
//        println(cand)
        //check if the candidate matches the var extracted from text
        val resultOfMatching = findMatchingVar(m, cand, mathSymbols, greek2wordDict)

        //the result of matching for now is either the good candidate returned or the string "None"
        //todo: this None thing is not pretty---redo with an option or sth
        if (resultOfMatching != "None") {
          //println("result of matching: " + resultOfMatching)
          //if the candidate is returned (instead of None), it's good and thus added to best candidates
          bestCandidates.append(resultOfMatching)
        }
      }

      //when did all the looping, choose the most complete (longest) out of the candidates and add it to the seq of matches for this file
      if (bestCandidates.nonEmpty) {
        latexTextMatches.append((bestCandidates.sortBy(_.length).reverse.head, m.text))
      }
    }
    //for (l <- latexTextMatches) println("match: " + l)
    //println("varMatch: " + goldTextVarMatch)
    //println("defMatch: " + goldTextDefMatch)
    latexTextMatches
  }


  //fixme: how did I get this output? why did 'b' from lambda end up as a valid candidate? instead of matching greek->word in text, match word->greek in equation
//  b, ﬁgures (b),


  def findMatchingVar(textMention: Mention, latexCandidateVar: String, mathSymbols: Seq[String], greek2wordDict: Map[String, String]): String = {
    //only proceed if the latex candidate does not have unmatched braces
    //replace all the math symbols in the latex candidate variable
    if (!checkIfUnmatchedCurlyBraces(latexCandidateVar) && !latexCandidateVar.endsWith("_") && !latexCandidateVar.startsWith("_")) {
      val replacements = new ArrayBuffer[String]()
      replacements.append(latexCandidateVar)
      for (ms <- mathSymbols) {
        //to make the regex pattern work, add "\\" in case the pattern starts with backslashes
        val pattern = if (ms.startsWith("\\")) "\\" + ms else ms

        val anotherReplacement = replacements.last.replaceAll(pattern, "")
        replacements.append(anotherReplacement)
      }
      //take the last item from 'replacements' and replace the braces---that should get us to the value
      val maxReplacement = replacements.last.replaceAll("\\{","").replaceAll("\\}","")
      //if the value that was left over after deleting all the latex stuff, then return the candidate as matching
      val toReturn = if (maxReplacement == textMention.arguments("variable").head.text) replaceGreekWithWord(latexCandidateVar, greek2wordDict) else "None"
      //
      return toReturn
    }
    else "None"
  }


  def checkIfUnmatchedCurlyBraces(string: String): Boolean = {
    //from here: https://stackoverflow.com/questions/562606/regex-for-checking-if-a-string-has-mismatched-parentheses
    //if unmatched curly braces, return true
    var depth = 0
    for (ch <- string) if (depth >= 0) {
      ch match {
        case '{' => depth += 1
        case '}' => depth -= 1
        case _ => depth
      }
    }
    if (depth!=0) true else false
  }


  def getEquationString(latexFile: String, word2greekDict: Map[String, String]): String = {
    val latexLines = Source.fromFile(latexFile).getLines().toArray
    val equationCandidates = for (
      i <- 0 until latexLines.length - 1
      if latexLines(i).contains("begin{equation}")

    ) yield latexLines(i).replaceAll("begin\\{equation\\}", "") + latexLines(i+1).replaceAll("\\\\label\\{.*?\\}","")

    replaceWordWithGreek(equationCandidates.head, word2greekDict)
  }

  def replaceGreekWithWord(varName: String, greek2wordDict: Map[String, String]): String = {
    var toReturn = varName
    for (k <- greek2wordDict.keys) {
      if (varName.contains(k)) {
        toReturn = toReturn.replace(k, greek2wordDict(k))
      }
    }
    toReturn
  }

  def replaceWordWithGreek(varName: String, word2greekDict: Map[String, String]): String = {
    var toReturn = varName
    for (k <- word2greekDict.keys) {
      if (varName.contains(k)) {
        toReturn = toReturn.replace(k, word2greekDict(k))
      }
    }

    toReturn
  }

  def getAllEqVarCandidates(equation: String): Seq[String] = {
    //just getting all continuous partitions from the equation,
    //for now, even those containing mathematical symbols---bc we extract compound vars that can contain anything
    //maybe still get rid of the equal sign, integral, some types of font info
    val eqCandidates = new ArrayBuffer[String]()
    for (i <- 0 to equation.length) {
      for (j <- i + 1 until equation.length) {
        val eqCand = equation.slice(i,j)
        if (!eqCandidates.contains(eqCand)) eqCandidates.append(equation.slice(i,j))
      }
    }
    eqCandidates
  }


  def processOneAnnotatedEquation(fileName: File): Map[String, Seq[String]] = {
    //for now just a seq of (eq-var, def) tuples
    val goldFile = new File(fileName.toString.replace("jsons", "gold"))

    val file = ujson.read(goldFile.readString())
    val entries = mutable.Map[String, Seq[String]]() //append var -> Seq[def] here
    for (entry <- file.arr) { //one entry
//      val entryMap = mutable.Map[String, Seq[String]]() //append var -> Seq[def] here
      var variable = new ArrayBuffer[String]()
      var description = new ArrayBuffer[String]()
      for (annType <- entry.obj) if (annType._1 == "equation" || annType._1 == "description") {
        for (entity <- annType._2.arr) { //entity is every instance of whatever we are looking at
          val entityArr = new ArrayBuffer[String]()
          for (charGroup <- entity.arr) { //this would be separate words, need to be joined with a space
            val wordArr = new ArrayBuffer[String]()
            for (char <- charGroup.obj("chars").arr) {
              wordArr.append(char("value").str)
            }
            entityArr.append(wordArr.mkString(""))

          }
          if (annType._1 == "equation") {
            variable.append(entityArr.mkString(""))
          } else {
            description.append(entityArr.mkString(" ").replaceAll(",|\\.|:", ""))
          }
        }
      }
      entries += (variable.head -> description)
    }

    entries.toMap
  }

  def getAnnotatedFileNamesFromTSV(tsv: String): Seq[String] = {
    val equationFileNames = new ArrayBuffer[String]()
    val bufferedSource = Source.fromFile(tsv)
    for (line <- bufferedSource.getLines()) {
      if ((line.split("\t").length > 10 && line.split("\t")(10)=="y" )|| ( line.split("\t").length > 11 && line.split("\t")(11) == "y")) {
        equationFileNames.append(line.split("\t")(0))
      }
    }
    bufferedSource.close()
    equationFileNames
  }

  def copyPdfsAndTSVs(equationName: String): Unit = {
    val srcDir = "/media/alexeeva/ee9cacfc-30ac-4859-875f-728f0764925c/storage/final_output/" + equationName + "/"
    val destDir = "input/LREC/Baseline/pdfsOfAnnotatedEquations/" + equationName + ".pdf"
    val destAabb = "input/LREC/Baseline/aabbs/" + equationName + ".tsv"
    val srcDirFile = new File(srcDir)
    val pdf = srcDirFile.listFiles().filter(_.toString.endsWith("pdf")).head
    //println(pdf)
    val aabb = srcDirFile.listFiles().filter(_.toString.endsWith("aabb.tsv")).head
    Files.copy(Paths.get(pdf.toString), Paths.get(destDir))
    Files.copy(Paths.get(aabb.toString), Paths.get(destAabb))

  }



}


object AlignmentBaseline {
  def main(args:Array[String]) {
    val fs = new AlignmentBaseline()//(args(0))
    fs.process()
  }
}
