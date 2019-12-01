package org.clulab.aske.automates.apps
import ai.lum.common.FileUtils._
import java.io.{File, PrintWriter}
import java.nio.file.{Files, Paths}

import ai.lum.common.ConfigUtils._
import ai.lum.common.Serializer
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.aske.automates.data.{DataLoader, TextRouter}
import org.clulab.aske.automates.OdinEngine
import org.clulab.odin.Mention
import org.clulab.processors.fastnlp.FastNLPProcessor
import org.clulab.utils.FileUtils._

import scala.collection.mutable
import scala.collection.mutable.ArrayBuffer
import scala.io.Source
import sys.process._
import scala.io.StdIn.readLine
import org.clulab.aske.automates.apps.ExtractAndExport.getExporter
import org.clulab.utils.DisplayUtils
import org.clulab.utils.Serializer._

import scala.collection.parallel.ParSeq



//todo: add eval:
//crop - done
//run through eq to latex
//read those equations in
//deal with not all gold files being actually there (unlikely but possible)--- should be fine if indices in json dir are correct/correspond to order/indices of equationFromTranslator.txt
//need to get gold files

import upickle.default._

case class Prediction(paperId: String, eqnId:String, latexIdentifier: String, textVariable: Option[String], definitions: Option[Seq[String]])
object Prediction{
  implicit val rw: ReadWriter[Prediction] = macroRW
}

class AlignmentBaseline() {
  //getting configs and such (borrowed from ExtractAndAlign)
  val config: Config = ConfigFactory.load()

  val pdfalignDir = config[String]("apps.pdfalignDir")
  val extractedMentionsDir = config[String]("apps.exportedMentionsDir")
  //this is where the latex equation files are
  val eqFileDir = config[String]("apps.baselineEquationDir")

  val eqSrcFile = config[String]("apps.eqnSrcFile")
  val eqFile = config[String]("apps.eqnPredFile")

  //these will be deleted from the latex equation to get to the values; not currently used
  val mathSymbolsFile = loadStringsFromResource("/AlignmentBaseline/mathSymbols.tsv")
  val mathSymbols = mathSymbolsFile.filter(_.length > 0).sortBy(_.length).reverse

  //get the greek letters and their names
  val greekLetterLines = loadStringsFromResource("/AlignmentBaseline/greek2words.tsv")

  //these will be used to map greek letters to words and back
  //    val greek2wordDict = mutable.Map[String, String]()
  val word2greekDict = mutable.Map[String, String]()

  for (line <- greekLetterLines) {
    val splitLine = line.split("\t")
    //      greek2wordDict += (splitLine.head -> splitLine.last)
    word2greekDict += (splitLine.last -> splitLine.head)
  }

  val greekWords = word2greekDict.keys.toList

  val inputDir = config[String]("apps.baselineTextInputDirectory")
  val inputType = config[String]("apps.inputType")
  val dataLoader = DataLoader.selectLoader(inputType) // txt, json (from science parse), pdf supported
  //    val paper_jsons = findFiles(inputDir, dataLoader.extension).sorted

  val outDir = config[String]("apps.baselineOutputDirectory")

  //all equations from file
  val eqn_ids = loadStrings(eqSrcFile).map(_.replace(".png", ""))
  val eqLines = loadStrings(eqFile)

  def customRender(cand: String): String = {
    render(replaceWordWithGreek(cand, word2greekDict.toMap), pdfalignDir).replaceAll("\\s", "")
  }

  def writePredictionsForEqn(eqnIndex: Int, eqn_id: String): Unit = {

    val split = eqn_id.split("_")
    val paperId = split(0)
    val eq = split(1)
    val paper = s"$inputDir/${eqn_id}.json"
    val predictionsFile = new PrintWriter(s"$outDir/predictions_${eqn_id}.jsonl")

    val equationStr = eqLines(eqnIndex)//.replaceAll("\\s", "")
    //      val allEqVarCandidates = getAllEqVarCandidates(equationStr)
    val allEqVarCandidates = getFrags(equationStr, pdfalignDir)
      .split("\n")
      // keep the ones that have less than 50 non-space chars
      .filter(cand => cand.count(char => !char.isSpaceChar) <= 50)
//    println("allEqVarCandidates:" + allEqVarCandidates.mkString(", "))

    val renderedAll = mutable.HashMap[String, String]()
    for (variableCand <- allEqVarCandidates) {
      renderedAll.put(variableCand, customRender(variableCand))
    }
    //for every file, get the text of the file
    //      val texts: Seq[String] = dataLoader.loadFile(paper)
    //      //todo: change greek letter in mentions to full words

    //IF MENTIONS NOT PREVIOUSLY EXPORTED:
    //extract the mentions
    //      val textMentions = texts.flatMap(text => textRouter.route(text).extractFromText(text, filename = Some(eqn_id)))
    ////      //only get the definition mentions
    //      val textDefinitionMentions = textMentions.seq.filter(_ matches "Definition")
    //
    //      //IF WANT TO EXPORT THE MENTIONS FOR EACH FILE:
    //      val exporter = new SerializedExporter("./input/LREC/Baseline/extractedMentions/" + eqn_id)
    //      exporter.export(textDefinitionMentions)
    //      exporter.close()
    //      println("exported ID: " + eqn_id)

    //IF HAVE PREVIOUSLY EXPORTED MENTIONS:

    val textDefinitionMentions = SerializedMentions
      .load(s"$extractedMentionsDir/${eqn_id}.serialized")
      .filter(mention => mention matches "Definition")
//    textDefinitionMentions.foreach(DisplayUtils.displayMention)
    //      for (td <- textDefinitionMentions) println("var: " + td.arguments("variable").head.text + " def: " + td.arguments("definition").head.text)

    val groupedByCommonVar = textDefinitionMentions
      .groupBy(_.arguments("variable").head.text)
      .mapValues(seq => moreLanguagey(seq).map(m => m.arguments("definition").head.text).distinct) //the definitions are sorted such that the first priority is the proportion of nat language text over len of def (we want few special chars in defs) and the second priority is length
//    groupedByCommonVar.foreach(println)

    val latexTextMatches = getLatexTextMatches(groupedByCommonVar, allEqVarCandidates, renderedAll.toMap, mathSymbols, word2greekDict.toMap, pdfalignDir, paperId, eq).seq
//    latexTextMatches.foreach(println)
    val filtered = latexTextMatches.filter(p => p.definitions.exists(defs => defs.exists(d => (d.count(_.isLetter)/d.length) > 0.7 )))


    println("+++++++++")
    for (m <- latexTextMatches) println(s"$m\t${paper}")
    println("++++++++++++\n")

    for (pred <- filtered) {
      writeTo(pred, predictionsFile)
      predictionsFile.write("\n")
      predictionsFile.flush()
    }

    // GETTING SIMPLE VARS FROM LATEX
    //which latex identifiers we got from text---used for filtering out the simple variables that have already been found from reading the text
    val latexIdentifiersFromText = latexTextMatches.map(_.latexIdentifier)

    //the simple var predictions (for the vars that were not found through reading text) will go here
    val simpleVars = getSimpleVars(equationStr, pdfalignDir, greekWords)

    val simpleValsNotFoundInText = for {
      sv <- simpleVars
      completeSV = if (checkIfUnmatchedCurlyBraces(sv)) sv + " }" else sv
      if !latexIdentifiersFromText.contains(completeSV)
      rendered = render(replaceWordWithGreek(completeSV, word2greekDict.toMap), pdfalignDir).replaceAll("\\s", "")
      newPred = new Prediction(paperId, eq, completeSV, Some(rendered), None)
    } yield newPred

    for (pred <- simpleValsNotFoundInText) {
      println(pred)
      writeTo(pred, predictionsFile)
      predictionsFile.write("\n")
      predictionsFile.flush()
    }

    // housekeeping
    predictionsFile.close()

  }

  def process() {

    //some configs and files to make sure this runs (borrowed from ExtractAndAlign
    //uncomment if need to extract mentions
    //    val textConfig: Config = config[Config]("TextEngine")
    //    val textReader = OdinEngine.fromConfig(textConfig)
    //    val commentReader = OdinEngine.fromConfig(config[Config]("CommentEngine"))
    //    val textRouter = new TextRouter(Map(TextRouter.TEXT_ENGINE -> textReader, TextRouter.COMMENT_ENGINE -> commentReader))

    //this is where the gold data is stored
    //    val goldDir = config[String]("apps.baselineGoldDir")
    // todo: eval script

    // todo: Becky -- speed this up a bit, and maybe add a backoff? par?
    // todo: for debug load in the mentions?
    for ((eqn_id, eqnIndex) <- eqn_ids.zipWithIndex.par) {
//      if (eqn_id == "1801.00110_equation0002") {
        println(s"processing $eqn_id")
        writePredictionsForEqn(eqnIndex, eqn_id)
//      }
    }
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


  def getSimpleVars(eqString: String, pdfalignDir: String, greekLetterWords: Seq[String]): Seq[String] = {
    val simpleVars = new ArrayBuffer[String]()
    //    val splitOnSpace = eqString.split("\\\\\\w*")
    //    val splitOnSpace = eqString.split(" ")
    //    val pattern1 = "\\{.*?\\}".r
    val fontStrings = "(\\\\mathcal|\\\\mathrm|\\\\mathbf|\\\\mathrm|\\\\pmb|\\\\mathcal|\\\\boldsymbol|\\\\mathbf|\\\\acute|\\\\grave|\\\\ddotv|\\\\tilde|\\\\bar|\\\\breve|\\\\check|\\\\hat|\\\\vec|\\\\dot|\\\\ddot|\\\\textrm|\\\\textsf|\\\\texttt|\\\\textup|\\\\textit|\\\\textsl|\\\\textsc|\\\\uppercase|\\\\textbf|\\\\textmd|\\\\textlf|\\\\mathbb)"

    val greekLetters = "[Aa]lpha|\\\\[Bb]eta|\\\\[Gg]amma|\\\\[Dd]elta|\\\\[Ee]psilon|\\\\[Zz]eta|\\\\[Ee]ta|\\\\[Tt]heta|\\\\[Ii]ota|\\\\[Kk]appa|\\\\[Ll]ambda|\\\\[Mm]u|\\\\[Nn]u|\\\\[Xx]i|\\\\[Oo]mikron|\\\\[Pp]i|\\\\[Rr]ho|\\\\[Ss]igma|\\\\[Tt]au|\\\\[Uu]psilon|\\\\[Pp]hi|\\\\[Cc]hi|\\\\[Pp]si|\\\\[Oo]mega"

    val pattern0 = s"\\\\sum\\s[_^]\\s\\{.*?}(\\s[_^]\\s\\{.*?\\}\\s)?".r //get rid of sum symbol with other stuff on it
    val pattern1 = s"${fontStrings}?\\s(${greekLetters})\\s[_^]\\s\\{\\s\\D*?\\s\\}(\\s\\}\\s[_^]\\s\\{\\s\\D*?\\s\\})?".r //lambdas with sub- and super-scripts
    val pattern2 = s"${fontStrings}?\\s\\w*?\\s[_^]\\s\\{\\s\\D*?\\s\\}(\\s\\}\\s[_^]\\s\\{\\s\\D*?\\s\\})?".r //non-lambdas with both superscript and subscript
    //    val pattern2 = "\\s\\w*?\\s[_^]\\s\\{.*?\\}".r //one var + subscript or superscript---patterns 1 and 2 should take care of this
    val pattern3 = s"${fontStrings}?\\s\\{\\s\\w*?\\s\\}\\s[_^]\\s\\{\\s\\D*?\\s\\}(\\s\\}\\s[_^]\\s\\{\\s\\D*?\\s\\})?".r //same as 2, but the main thing is wrapped in curly braces
    val pattern4 = s"${fontStrings}\\s\\{\\s\\D\\s\\}".r

//    println(eqString)


    for (m <- pattern0.findAllIn(eqString)) println("> " + m)
    val afterPatt0 = pattern0.replaceAllIn(eqString, "") //don't append these to possible vars---we don't care what's in the sum if it's not defined

    //what we find with patt 1:
    for (m <- pattern1.findAllIn(afterPatt0)) {
      if (!simpleVars.contains(m)) {
        simpleVars.append(m.trim)
      }
//      println("=> " + m)
    }
    val afterPatt1 = pattern1.replaceAllIn(afterPatt0, "")
//    println(afterPatt1)

    //what we find with patt2:
    for (m <- pattern2.findAllIn(afterPatt1)) {
      if (!simpleVars.contains(m)) {
        simpleVars.append(m.trim)
      }
//      println("=> " + m)
    }
    val afterPatt2 = pattern2.replaceAllIn(afterPatt1, "")
//    println(afterPatt2)

    //what we find with patt 3:
    for (m <- pattern3.findAllIn(afterPatt2)) {
      if (!simpleVars.contains(m)) {
        simpleVars.append(m.trim)
      }
//      println("=> " + m)
    }
    val afterPatt3 = pattern3.replaceAllIn(afterPatt2, "")
//    println(afterPatt3)

    //what we find with patt 4:
    for (m <- pattern4.findAllIn(afterPatt3)) {
      if (!simpleVars.contains(m)) {
        simpleVars.append(m)
      }
//      println("=> " + m)
    }
    val afterPatt4 = pattern4.replaceAllIn(afterPatt3, "")
//    println(afterPatt4)


    val finalStringTokenized = afterPatt4.split(" ")



    for (i <- finalStringTokenized.indices) {
      if (finalStringTokenized(i).toCharArray.length == 1 && finalStringTokenized(i).toCharArray.head.isLetter) {
        if ((i == 0 || i == finalStringTokenized.length) && !simpleVars.contains(finalStringTokenized(i))) {
          simpleVars.append(finalStringTokenized(i).trim)
        } else {
          if (i + 1 < finalStringTokenized.length && i - 1 >= 0 && finalStringTokenized(i-1).toCharArray.length > 0 && finalStringTokenized(i+1).toCharArray.length > 0) {

//            println("---->" + finalStringTokenized(i) + "next: " +   finalStringTokenized(i+1))
            if (!finalStringTokenized(i-1).toCharArray.last.isLetter
              && !finalStringTokenized(i+1).toCharArray.head.isLetter
              && !simpleVars.contains(finalStringTokenized(i))) {
              simpleVars.append(finalStringTokenized(i).trim)
            }
          }
        }
      } else {
        //if matches one of greek letters
        if (greekLetterWords.contains(finalStringTokenized(i).toLowerCase.replace("\\", "")) && !simpleVars.contains(finalStringTokenized(i))) {
          simpleVars.append(finalStringTokenized(i).trim)
        }
      }
    }

    simpleVars

  }

  def getLatexTextMatches(
    var2Defs: Map[String, Seq[String]],
    allEqVarCandidates: Seq[String],
    renderedAll: Map[String, String],
    mathSymbols: Seq[String],
    word2greekDict: Map[String, String],
    pdfalignDir: String,
    paperId: String,
    eqnId: String): Seq[Prediction] = {

    //for every extracted var-def var, find the best matching latex candidate var by iteratively replacing math symbols until the variables match up; out of those, return max length with matching curly brackets

    //all the matches from one file name will go here:1
    val latexTextMatches = new ArrayBuffer[Prediction]()
    //for every extracted mention
    for (variable <- var2Defs.keys) {
//      println(s"checking variable: $variable")
      //best Latex candidates, out of which we'll take the max (to account for some font info)
//      val bestCandidates = new ArrayBuffer[String]()
        //for every candidate eq var
        val bestCandidates = for {
          cand <- allEqVarCandidates
          renderedCand = renderedAll(cand)
          //check if the candidate matches the var extracted from text and return the good candidate or str "None"
          resultOfMatching = findMatchingVar(variable, cand, renderedCand, mathSymbols, word2greekDict, pdfalignDir)
//          _ = println(resultOfMatching)
          if resultOfMatching.isDefined
        } yield resultOfMatching.get

      // choose the most complete (longest) out of the candidates and add it to the seq of matches for this file
      if (bestCandidates.nonEmpty) {
        val bestCand = bestCandidates.maxBy(numLetters)
        val pred = Prediction(paperId, eqnId, bestCand.trim, Some(variable), Some(var2Defs(variable)))
        latexTextMatches.append(pred)
      }
    }
    for (l <- latexTextMatches) println("match: " + l)
    latexTextMatches
  }

  def numLetters(s: String): Int = s.count(_.isLetter)

  //fixme: how did I get this output? why did 'b' from lambda end up as a valid candidate? instead of matching greek->word in text, match word->greek in equation
//  b, ﬁgures (b),


  def findMatchingVar(
                       variable: String,
                       latexCandidateVar: String,
                       renderedLatexCandidateVar: String,
                       mathSymbols: Seq[String],
                       word2greekDict: Map[String, String],
                       pdfalignDir: String): Option[String] = {
    //only proceed if the latex candidate does not have unmatched braces
    //replace all the math symbols in the latex candidate variable
//    println("variable: " + variable)
//    println("candidate: " + latexCandidateVar)
//          val replacements = new ArrayBuffer[String]()
//          replacements.append(latexCandidateVar)
//          for (ms <- mathSymbols) {
//            //to make the regex pattern work, add "\\" in case the pattern starts with backslashes
//            val pattern = if (ms.startsWith("\\")) "\\" + ms else ms
//
//            val anotherReplacement = replacements.last.replaceAll(pattern, "")
//            replacements.append(anotherReplacement)
//          }
//    //      take the last item from 'replacements' and replace the braces---that should get us to the value
//          val maxReplacement = replacements.last.replaceAll("\\{","").replaceAll("\\}","").replace(" ","")

    //render the candidate with the greek letter word replaced with the greek letter
//    val rendered = render(replaceWordWithGreek(latexCandidateVar, word2greekDict), pdfalignDir).replaceAll("\\s", "")
    //if the value that was left over after deleting all the latex stuff, then return the candidate as matching
    if (renderedLatexCandidateVar == variable) {
      println(" --> rendered == variable")
      println(" --> rendered: " + renderedLatexCandidateVar)
      //return the candidate
      return Some(latexCandidateVar)
    }

    None
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
        toReturn = toReturn.replace(k, s"""\${greek2wordDict(k)}""")
      }
    }
    toReturn
  }

  def replaceWordWithGreek(varName: String, word2greekDict: Map[String, String]): String = {
    var toReturn = varName
    for (k <- word2greekDict.keys) {
      val escaped = """\""" + k
      if (varName.contains(escaped)) {
        toReturn = toReturn.replace(escaped, word2greekDict(k))
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
    val goldFile = new File(fileName.toString.replace("ParsedJsons", "gold"))

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

  def render(formula: String, pdfalignDir: String): String = {
    val command = Seq("python", s"$pdfalignDir/align_latex/normalize.py", "render", formula.trim)
    val process = Process(command, new File(s"$pdfalignDir/align_latex"))
    process.!!
  }

  def getFrags(formula: String, pdfalignDir: String): String = {
    val command = Seq("python", s"$pdfalignDir/align_latex/tokenize_and_fragment.py", "get_fragments", formula.trim)
    val process = Process(command, new File(s"$pdfalignDir/align_latex"))
    process.!!.trim
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

  def moreLanguagey(mentions: Seq[Mention]): Seq[Mention] = {
    val valid = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ "

//    val defsWithLengthOfLangChars = for (
//      m <- mentions
//
//    ) yield (m, m.arguments("definition").head.text.filter(c => valid contains c).length / m.arguments("definition").head.text.length)
//
//    val defsWithPropOfLang = mentions.map(m => m.arguments("definition").head.text.filter(c => valid contains c).length / m.arguments("definition").head.text.length)

    val sorted = mentions.sortBy(m => (m.arguments("definition").head.text.filter(c => valid contains c).length.toFloat / m.arguments("definition").head.text.length, m.arguments("definition").head.text.length)).reverse

//    val betterDefinedMentions = defsWithLengthOfLangChars.sortBy(_._2)
//    for (b <- betterDefinedMentions) println("better def " + b._1.text)
//    println("++++++++++++++++")
//    for (b <- sorted) println("better def " + b.arguments("definition").head.text + b.arguments("definition").head.text.filter(c => valid contains c).length.toFloat / b.arguments("definition").head.text.length + " " + b.arguments("definition").head.text.length)
//    println("best" + sorted.head.arguments("definition").head.text)
//    println("-+-+-+-+-+")
    sorted

  }


  def copyPdfsAndTSVs(equationName: String): Unit = {
    val srcDir = "/media/alexeeva/ee9cacfc-30ac-4859-875f-728f0764925c/storage/final_output/" + equationName + "/"
    val destDir = "input/LREC/Baseline/pdfsOfAnnotatedEquations/" + equationName + ".pdf"
    val destAabb = "input/LREC/Baseline/aabbs/" + equationName + ".tsv"
    val srcDirFile = new File(srcDir)
    print(srcDirFile.toString)
    val pdf = srcDirFile.listFiles().filter(_.toString.endsWith("pdf")).head
    //println(pdf)
    val aabb = srcDirFile.listFiles().filter(_.toString.endsWith("aabb.tsv")).head
    Files.copy(Paths.get(pdf.toString), Paths.get(destDir))
    Files.copy(Paths.get(aabb.toString), Paths.get(destAabb))

  }

  def runCopyPdfAndTsvs(): Unit = {
    val file = new File ("/home/alexeeva/Repos/automates/text_reading/input/LREC/Baseline/gold")
    val files = file.listFiles()
    for (f <- files) {
      copyPdfsAndTSVs(f.toString.split("/").last.replace(".json", ""))
//      print(f.toString.split("/").last)
    }
  }

}



object AlignmentBaseline {
  def main(args:Array[String]) {
    val fs = new AlignmentBaseline()//(args(0))
//        fs.runCopyPdfAndTsvs()
    fs.process()


  }
}
