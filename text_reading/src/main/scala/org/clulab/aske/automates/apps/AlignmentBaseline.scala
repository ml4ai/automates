package org.clulab.aske.automates.apps


import ai.lum.common.ConfigUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.aske.automates.data.DataLoader
import org.clulab.aske.automates.OdinEngine
import org.clulab.odin.Mention
import org.clulab.utils.FileUtils
import scala.collection.mutable
import scala.collection.mutable.ArrayBuffer
import scala.io.Source

class AlignmentBaseline() {
  def process() {
    //getting configs and such (borrowed from ExtractAndAlign):

    val config: Config = ConfigFactory.load()
    //mathsymbols:
    val mathSymbols = Source.fromFile("/home/alexeeva/Repos/automates/text_reading/src/main/resources/AlignmentBaseline/mathSymbols.tsv").getLines().toArray.filter(_.length > 0).sortBy(_.length).reverse


    val greekLetterLines = Source.fromFile("/home/alexeeva/Repos/automates/text_reading/src/main/resources/AlignmentBaseline/greek2words.tsv").getLines()

    val greek2wordDict = mutable.Map[String,String]()
    for (line <- greekLetterLines) {
      val splitLine = line.split("\t")
      greek2wordDict += (splitLine.head -> splitLine.last)
    }

    val textConfig: Config = config[Config]("TextEngine")
    val textReader = OdinEngine.fromConfig(textConfig)
    val commentReader = OdinEngine.fromConfig(config[Config]("CommentEngine"))
    val inputDir = config[String]("apps.baslineInputDirectory")
    val inputType = config[String]("apps.inputType")
    val dataLoader = DataLoader.selectLoader(inputType) // txt, json (from science parse), pdf supported
    val files = FileUtils.findFiles(inputDir, dataLoader.extension)
    val eqFileDir = config[String]("apps.baselineEquationDir")

    //todo: this is just one equation; need to have things such that text files are read in parallel with the corresponding equation latexes

    val file2FoundMatches = files.par.flatMap { file =>  //should return sth like Map[fileId, (equation candidate, text candidate) ]
      //for every file, get the text of the file
      val texts: Seq[String] = dataLoader.loadFile(file)
    //todo: change greek letter in mentions to full words
      //extract the mentions
      val textMentions = texts.flatMap(text => textReader.extractFromText(text, filename = Some(file.getName)))
      //only get the definition mentions
      val textDefinitionMentions = textMentions.seq.filter(_ matches "Definition")

      for (td <- textDefinitionMentions) println(td.text)

      val equationName = eqFileDir.toString + file.toString.split("/").last.replace("json","txt")
      println(equationName + "<--")
      val equationStr = getEquationString(equationName)
      val allEqVarCandidates = getAllEqVarCandidates(equationStr)
      //get the name of the equation file
      //for now let's just use our old one

      val latexTextMatches = getLatexTextMatches(textDefinitionMentions, allEqVarCandidates, mathSymbols, greek2wordDict.toMap)

      latexTextMatches
    }


    for (m <- file2FoundMatches) println(s"Matches: ${m._1}, ${m._2}")
  }

  def getLatexTextMatches(textDefinitionMentions: Seq[Mention], allEqVarCandidates: Seq[String], mathSymbols: Seq[String], greek2wordDict: Map[String, String]): Seq[(String, String)] = {

    //for every extracted var-def var, find the best matching latex candidate var by iteratively replacing math symbols until the variables match up; out of those, return max length with matching curly brackets

    //all the matches from one file name will go here:
    val latexTextMatches = new ArrayBuffer[(String, String)]()
    //for every extracted mention
    for (m <- textDefinitionMentions) {
      //best candidates, out of which we'll take the max (to account for some font info
      val bestCandidates = new ArrayBuffer[String]()
      //for every candidate eq var
      for (cand <- allEqVarCandidates) {
        //check if the candidate matches the var extracted from text
        val resultOfMatching = findMatchingVar(m, cand, mathSymbols, greek2wordDict)
        //the result of matching for now is either the good candidate returned or the string "None"
        //todo: this None thing is not pretty---redo with an option or sth
        if (resultOfMatching != "None") {
          //if the candidate is returned (instead of None), it's good and thus added to best candidates
          bestCandidates.append(resultOfMatching)
        }
      }

      //when did all the looping, choose the most complete (longest) out of the candidates and add it to the seq of matches for this file
      if (bestCandidates.nonEmpty) {
        latexTextMatches.append((bestCandidates.sortBy(_.length).reverse.head, m.text))
      }
    }
    latexTextMatches
  }

  def findMatchingVar(textMention: Mention, latexCandidateVar: String, mathSymbols: Seq[String], greek2wordDict: Map[String, String]): String = {
    //only proceed if the latex candidate does not have unmatched braces
    if (!checkIfUnmatchedCurlyBraces(latexCandidateVar)) {
      //good candidates will go here
      val replacements = new ArrayBuffer[String]()
      replacements.append(latexCandidateVar)
      for (ms <- mathSymbols) {
        val pattern = if (ms.startsWith("\\")) "\\" + ms else ms
        //      println(pattern)

        val anotherReplacement = replacements.last.replaceAll(pattern, "")
        replacements.append(anotherReplacement)
      }

      val maxReplacement = replacements.last.replaceAll("\\{","").replaceAll("\\}","")

      val toReturn = if (maxReplacement == replaceGreekWithWord(textMention.arguments("variable").head.text, greek2wordDict)) latexCandidateVar else "None"
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


  def getEquationString(latexFile: String): String = {
    val latexLines = Source.fromFile(latexFile).getLines().toArray
    val equationCandidates = for (
      i <- 0 until latexLines.length - 1
      if latexLines(i).contains("begin{equation}")

    ) yield latexLines(i+1).replaceAll("\\\\label\\{.*?\\}","")
    equationCandidates.head
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
}


object AlignmentBaseline {
  def main(args:Array[String]) {
    val fs = new AlignmentBaseline()//(args(0))
    fs.process()
  }
}
