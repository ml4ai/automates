package org.clulab.aske.automates.apps

import java.io.{File, PrintWriter}

import ai.lum.common.ConfigUtils._
import ai.lum.common.FileUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.aske.automates.data.{DataLoader, TextRouter}
import org.clulab.aske.automates.alignment.{Aligner, Alignment, VariableEditDistanceAligner}
import org.clulab.aske.automates.entities.StringMatchEntityFinder
import org.clulab.aske.automates.grfn._
import org.clulab.aske.automates.OdinEngine
import org.clulab.processors.Document
import org.clulab.processors.fastnlp.FastNLPProcessor
import org.clulab.utils.{DisplayUtils, FileUtils}
import org.slf4j.LoggerFactory
import upickle.default._

import scala.collection.mutable.ArrayBuffer
import scala.io.Source

object ExtractAndAlign {

  val logger = LoggerFactory.getLogger(this.getClass())

  def ltrim(s: String): String = s.replaceAll("^\\s*[C!]?[-=]*\\s{0,5}", "")

  def parseCommentText(text: String, filename: Option[String] = None): Document = {
    val proc = new FastNLPProcessor()
    //val Docs = Source.fromFile(filename).getLines().mkString("\n")
    val lines = for (sent <- text.split("\n") if ltrim(sent).length > 1 //make sure line is not empty
      && sent.stripMargin.replaceAll("^\\s*[C!]", "!") //switch two different comment start symbols to just one
      .startsWith("!")) //check if the line is a comment based on the comment start symbol (todo: is there a regex version of startWith to avoide prev line?
      yield ltrim(sent)
    var lines_combined = Array[String]()
    // which lines we want to ignore (for now, may change later)
    val ignoredLines = "(^Function:|^Calculates|^Calls:|^Called by:|([\\d\\?]{1,2}\\/[\\d\\?]{1,2}\\/[\\d\\?]{4})|REVISION|head:|neck:|foot:|SUBROUTINE|Subroutine|VARIABLES|Variables|State variables)".r

    for (line <- lines if ignoredLines.findAllIn(line).isEmpty) {
      if (line.startsWith(" ") && lines.indexOf(line) != 0) { //todo: this does not work if there happens to be more than five spaces between the comment symbol and the comment itself---will probably not happen too frequently. We shouldn't make it much more than 5---that can effect the lines that are indented because they are continuations of previous lines---that extra indentation is what helps us know it's not a complete line.
        var prevLine = lines(lines.indexOf(line) - 1)
        if (lines_combined.contains(prevLine)) {
          prevLine = prevLine + " " + ltrim(line)
          lines_combined = lines_combined.slice(0, lines_combined.length - 1)
          lines_combined = lines_combined :+ prevLine
        }
      }
      else {
        if (!lines_combined.contains(line)) {
          lines_combined = lines_combined :+ line
        }
      }
    }

    for (line <- lines_combined) println(line)
    println("Number of lines passed to the comment reader: " + lines_combined.length)

    val doc = proc.annotateFromSentences(lines_combined, keepText = true)
    doc.id = filename
    doc
  }


  def main(args: Array[String]): Unit = {
    val config: Config = ConfigFactory.load("automates")

    // Instantiate the text reader
    val textconfig: Config = config[Config]("TextEngine")
    val textReader = OdinEngine.fromConfig(textconfig)
    // Instantiate the comment reader
    val commentReader = OdinEngine.fromConfig(config[Config]("CommentEngine"))
    // todo: future readers
    //    val glossaryReader = OdinEngine.fromConfig(config[Config]("GlossaryEngine"))
    //    val tocReader = OdinEngine.fromConfig(config[Config]("TableOfContentsEngine"))
    val textRouter = new TextRouter(Map(TextRouter.TEXT_ENGINE -> textReader, TextRouter.COMMENT_ENGINE -> commentReader))

    // Load text input from directory
    val inputDir = config[String]("apps.inputDirectory")
    val inputType = config[String]("apps.inputType")
    val dataLoader = DataLoader.selectLoader(inputType) // txt, json (science parse) supported
    val files = FileUtils.findFiles(inputDir, dataLoader.extension)

    // Read the text
    val textMentions = files.par.flatMap { file =>
      // Open corresponding output file and make all desired exporters
      println(s"Extracting from ${file.getName}")
      // Get the input file contents, note: for science parse format, each text is a section
      val texts: Seq[String] = dataLoader.loadFile(file)
      // Route text based on the amount of sentence punctuation and the # of numbers (too many numbers = non-prose from the paper)
      texts.flatMap(text => textRouter.route(text).extractFromText(text, filename = Some(file.getName)))
    }
    println(s"Extracted ${textMentions.length} text mentions")


    // todo: We probably want a separate comment reader for each model....? i.e. PETPT vs PETASCE

    // Grfn
    val grfnPath: String = config[String]("apps.grfnFile") // fixme (Becky): extend to a dir later?
    val grfnFile = new File(grfnPath)
    //    val grfn = GrFNParser.mkDocument(new File(grfnFile))
    //    val grfnVars = GrFNDocument.getVariables(grfn)
    //    val variableNames = grfnVars.map(_.name.toUpperCase) // fixme: are all the variables uppercase?

    val grfn = ujson.read(grfnFile.readString())

    //Getting comments from grfn
    //the source_comments section of the json contains comments for multiple containers; get the container names to look up the comments for that container in the source_comments section
    //todo: do we want to include "$file_head" and "$file_foot"?
    val containerNames = grfn("containers").arr.map(_.obj("name").str)
    val sourceCommentObject = grfn("source_comments").obj
    //store comment strings here
    val commentTexts = new ArrayBuffer[String]()
    //for each container, the comment section has these three components
    val commentComponents = List("head", "neck", "foot") //todo: a better way to read these in?
    for (name <- containerNames) if (sourceCommentObject.contains(name)) {
      val commentObject = sourceCommentObject(name).obj
      for (cc <- commentComponents) if (commentObject.contains(cc)) {
        val text = commentObject(cc).arr.map(_.str).mkString("")
        if (text.length > 0) {
          commentTexts.append(text)
        }
      }
    }

    // Parse the comment texts
    val docs = commentTexts.map(parseCommentText(_, filename = Some(grfn("source").arr.head.str)))
    // Iterate through the docs and find the mentions; eliminate duplicates
    val commentMentions = docs.map(doc => commentReader.extractFrom(doc)).flatten.distinct

    //Getting Variables from Grfn
    val variableNames = grfn("variables").arr.map(_.obj("name").str)
    val variableShortNames = for (
      name <- variableNames
    ) yield name.split("::").reverse.slice(1, 2).mkString("")


    // Align the comment definitions to the GrFN variables
    val numAlignments = config[Int]("apps.numAlignments")
    val commentDefinitionMentions = commentMentions.seq.filter(_ matches "Definition")
    println("length "+ commentDefinitionMentions.length)


    val variableNameAligner = new VariableEditDistanceAligner(Set("variable"))

    val varNameAlignments = variableNameAligner.alignTexts(variableShortNames, commentDefinitionMentions.map(Aligner.getRelevantText(_, Set("variable"))))
    val top1ByVariableName = Aligner.topKBySrc(varNameAlignments, 1)


    // Align the comment definitions to the text definitions
    val w2vAligner = Aligner.fromConfig(config[Config]("alignment"))
    val textDefinitionMentions = textMentions.seq.filter(_ matches "Definition")

    // ----------------------------------
    // Debug:
    //    val pw = new PrintWriter("./output/definitions.txt")  ///../../../../../../../../ExtractAndAlign.scala
    //    for (m <- textDefinitionMentions) {
    //      pw.println("**************************************************")
    //      pw.println(m.sentenceObj.getSentenceText)
    //      DisplayUtils.printMention(m, pw)
    //      pw.println("")
    //    }
    //    pw.close()
    // ----------------------------------
    // Generates (src idx, dst idx, score tuples) -- exhaustive
    val commentToTextAlignments: Seq[Alignment] = w2vAligner.alignMentions(commentDefinitionMentions, textDefinitionMentions)
    val scoreThreshold = config[Double]("apps.commentTextAlignmentScoreThreshold")
    // group by src idx, and keep only top k (src, dst, score) for each src idx
    val topKAlignments: Seq[Seq[Alignment]] = Aligner.topKBySrc(commentToTextAlignments, numAlignments, scoreThreshold)


    // ----------------------------------
    // Debug:
    topKAlignments.foreach { aa =>
      println("====================================================================")
      println(s"              SRC VAR: ${commentDefinitionMentions(aa.head.src).arguments("variable").head.text}")
      println("====================================================================")
      aa.foreach { topK =>
        val v1Text = commentDefinitionMentions(topK.src).text
        val v2Text = textDefinitionMentions(topK.dst).text
        println(s"aligned variable (comment): ${commentDefinitionMentions(topK.src).arguments("variable").head.text}")
        println(s"aligned variable (text): ${textDefinitionMentions(topK.dst).arguments("variable").head.text}")
        println(s"comment: ${v1Text}")
        println(s"text: ${v2Text}")
        println(s"score: ${topK.score}\n")
      }
    }
    // ----------------------------------

    // Export alignment:
    val outputDir = config[String]("apps.outputDirectory")

    // Make Comment Spans from the comment variable mentions
    val commentLinkElems = commentDefinitionMentions.map { commentMention =>
      val elemType = "comment_span"
      val source = grfn("source").arr.head.str
      val content = commentMention.text
      val contentType = "null"
      mkLinkElement(elemType, source, content, contentType)
    }

    // Repeat for src code variables
    val sourceLinkElements = variableNames.map { varName =>
      val elemType = "identifier"
      val source = grfn("source").arr.head.str
      val content = varName
      val contentType = "null"
      mkLinkElement(elemType, source, content, contentType)
    }

    // Repeat for text variables

    val textLinkElements = textDefinitionMentions.map { mention =>
      val elemType = "text_span"
      val source = mention.document.id.getOrElse("unk_text_file") // fixme
    val content = mention.text //todo add the relevant parts of the metnion var + def as a string --> smth readable
    val contentType = "null"
      mkLinkElement(elemType, source, content, contentType)
    }

    // Repeat for Eqn Variables

    // Make Link Hypotheses (text/comment)
    val hypotheses = new ArrayBuffer[ujson.Obj]()
    for (topk <- topKAlignments) {
      for (alignment <- topk) {
        val commentLinkElement = commentLinkElems(alignment.src)
        val textLinkElement = textLinkElements(alignment.dst)
        val score = alignment.score
        val hypothesis = mkHypothesis(commentLinkElement, textLinkElement, score)
        hypotheses.append(hypothesis)
      }
    }

    for (topk <- top1ByVariableName) {
      for (alignment <- topk) {
        val variableLinkElement = sourceLinkElements(alignment.src)
        val commentLinkElement = commentLinkElems(alignment.dst)
        val score = alignment.score
        val hypothesis = mkHypothesis(variableLinkElement, commentLinkElement, score)
        hypotheses.append(hypothesis)
      }
    }

    grfn("grounding") = hypotheses.toList
    val grfnBaseName = new File(grfnPath).getBaseName()
    val grfnWriter = new PrintWriter(s"$outputDir/${grfnBaseName}_with_groundings.json")
    ujson.writeTo(grfn, grfnWriter)
//    grfnWriter.println(write(grfn.render()))
    grfnWriter.close()

  }

  def mkLinkElement(elemType: String, source: String, content: String, contentType: String): ujson.Obj = {
    val linkElement = ujson.Obj(
      "type" -> elemType,
      "source" -> source,
      "content" -> content,
      "content_type" -> contentType
    )
    linkElement
  }

  def mkHypothesis(elem1: ujson.Obj, elem2: ujson.Obj, score: Double): ujson.Obj = {
    val hypothesis = ujson.Obj(
      "element_1" -> elem1,
      "element_2" -> elem2,
      "score" -> score
    )
    hypothesis
  }


}


