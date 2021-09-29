package org.clulab.aske.automates.apps

import java.io.{BufferedWriter, File, FileWriter, PrintWriter}
import ai.lum.common.ConfigUtils._
import com.typesafe.config.{Config, ConfigFactory}
import org.clulab.aske.automates.data.{CosmosJsonDataLoader, DataLoader, PlainTextDataLoader, TextRouter}
import org.clulab.aske.automates.OdinEngine
import org.clulab.aske.automates.attachments.AutomatesAttachment
import org.clulab.aske.automates.serializer.AutomatesJSONSerializer
import org.clulab.utils.{FileUtils, Serializer}
import org.clulab.odin.Mention
import org.clulab.odin.serialization.json.JSONSerializer
import org.json4s.jackson.JsonMethods._
import com.github.tomtung.latex2unicode._
import ujson.False

import scala.collection.mutable
import scala.util.control._
import scala.collection.mutable.ArrayBuffer

/**
  * App used to extract mentions from files in a directory and produce the desired output format (i.e., serialized
  * mentions or any other format we may need).  The input and output directories as well as the desired export
  * formats are specified in the config file (located in src/main/resources).
  * This makes ONE output file for each of the input files.
  */
object Subscripts extends App {

  // todo: separate underscore file for each input file - done
  // just throw out everything between begin - end - done?
  // replace newcommand stuff - done
  // throw out \cite
  // preserve file name in data for easier debugging
  // do latex normalizing AFTER sentence splitting - split sentences

  val config = ConfigFactory.load()

  val inputDir: String = "/Users/alexeeva/Desktop/automates-related/arxiv/tex_dir/"
  //  val inputDir = "/Users/alexeeva/Desktop/subscripts/texfiles"
  val outputDir: String = "/Users/alexeeva/Desktop/automates-related/arxiv/tex_dir/firstPass/"
  val inputType = config[String]("apps.inputType")
  // if using science parse doc, uncomment next line and...
  //  val dataLoader = DataLoader.selectLoader(inputType) // pdf, txt or json are supported, and we assume json == science parse json
  //..comment out this line:
  val dataLoader = new PlainTextDataLoader
  val exportAs: List[String] = config[List[String]]("apps.exportAs")

  import java.io.File


  val files = FileUtils.findFiles(inputDir, "tex")

  val reader = OdinEngine.fromConfig(config[Config]("TextEngine"))
  val loop = new Breaks

  def isBalanced(string: String, openDelim: String, close_delim: String): Boolean = {

    var n_open = 0
    for (ch <- string) {
      if (ch == openDelim.head) {
        n_open += 1
      } else if (ch == close_delim.head) {
        n_open -= 1
      }
      if (n_open < 0) return false
    }
    n_open == 0
  }

  //uncomment these for using the text/comment router
  //  val commentReader = OdinEngine.fromConfig(config[Config]("CommentEngine"))
  //  val textRouter = new TextRouter(Map(TextRouter.TEXT_ENGINE -> reader, TextRouter.COMMENT_ENGINE -> commentReader))
  // For each file in the input directory:

  //  pw.write("MAsha")
  files.foreach { file =>
    try {
    val pw = new PrintWriter(new File(outputDir + file.getName.replace(".tex", "") + "subscripts_data_sample.txt"))
    //    println("FILE NAME" + file)
    // 1. Open corresponding output file and make all desired exporters
    //    println(s"Extracting from ${file.getName}")
    // 2. Get the input file contents
    // note: for science parse format, each text is a section
    val texts = dataLoader.loadFile(file)

    //    for (t <- texts) {
    //      println("t: " + t)
    //      println("replaced: " +
    //        " " + t.replaceAll("\\\\begin\\{equation\\}(.|\\n)*\\\\end\\{equation\\}","")) //\{equation\}.*\\end\{equation\}
    //    }
    val filteredTexts = new ArrayBuffer[String]()
    val newCommands = mutable.Map[String, String]()
    for (t <- texts) {
      val splitText = t.replaceAll("\\\\begin\\{equation\\}(.|\\n)*?\\\\end\\{equation\\}|%.*?\\n|\\\\label\\{.*?\\}\\}?", "").split("\n")
      //        replaceAll("\\\\begin\\{equation\\}(.|\\n)*\\\\end\\{equation\\}","").
      //        replaceAll("%.*?\n","").
      //        replaceAll("\\\\label\\{.*?\\}\\}?", "").
      //        split("\n")
      for (st <- splitText) {
        if (st.contains("\\newcommand")) {
          val split = st.split("\\}\\[?.*?\\]?\\{")
          //          println("split: " + split.mkString("|||"))
          newCommands(split.head.replace("\\newcommand{", "")) = split.last.dropRight(1)
        } else if (!(st.startsWith("\\document") || st.startsWith("\\usepackage") || st.startsWith("\\begin") || st.startsWith("\\end") || st.startsWith("\\input") || st.startsWith("\\author") || st.startsWith("\\keywords") || st.startsWith("\\altauthor") || st.startsWith("\\affiliation") || st.startsWith("\\include"))) {
          filteredTexts.append(st)
        }
      }
    }
    //    for (t <- filteredTexts) println(">> " + t)

    val regex = """\w+\_\{+.{1,20}\}\}*|\w+\_\w+""".r
    for (t <- filteredTexts) {
      // todo: so here first sentence_tokenize and then search for regex in each sent (possible issue---latex sequences being tokenized as separate sentences, but why would they?)
      //      println(">> " + t)
      val matches = regex.findAllIn(t).toList
      val matchIndices = regex.findAllMatchIn(t).toList
      val matchesStarts = matchIndices.map(m => (m.start)).toList
      val matchesEnds = matchIndices.map(m => (m.end)).toList
      val lastIndices = new ArrayBuffer[Int]()
      for ((mi, idx) <- matchesStarts.zipWithIndex) {
        //        println("mi: " + mi + " " + matches(idx))
        if (!matches(idx).contains("{")) {
          lastIndices.append(matchIndices(idx).end)
        } else {
          loop.breakable {
            var lastReasonableEndIndex = 0
            for (i <- 3 to 40) {
              val possibleMatch = t.slice(mi, mi + i)
              //              println("possible match: " + possibleMatch)
              if (possibleMatch.contains("{") && isBalanced(possibleMatch, "{", "}")) {
                lastIndices.append(mi + i)
                val idx = mi + i
                //                println("appending " + idx)
                loop.break()
              } //else {println("not appending")}
            }
          }
        }
      }


      //      println("len: " + matchesStarts.length)
      //      println("last indices: " + lastIndices.length)
      //      println("last indices: " + lastIndices.mkString("||"))
      val textChunks = new ArrayBuffer[String]()
      for ((pos, idx) <- matchesStarts.zipWithIndex) {
        //        println("pos and idx: " + pos + " " + idx)
        if (idx == 0) {
          textChunks.append(t.slice(0, pos))
          //          println(">>" + t.slice(0, pos))
        } else if (idx == matchesStarts.length - 1) {
          //          println("idx: " + idx)
          textChunks.append(t.slice(pos, t.length))
        } else {
          textChunks.append(t.slice(pos, lastIndices(idx)))
          val nextMatchStart = matchesStarts(idx + 1)
          textChunks.append(t.slice(matchesEnds(idx), nextMatchStart))
        }
      }
      //
      //      for (t <- textChunks) {
      //        println("==>" + t + "\n")
      //      }


      //      println("TEXT: " + t)
      //            if (!t.startsWith("""\""")) {
      //              println("t: " + t)
      ////      pw.write(t)
      //      for (j <- t.split("\n")) {
      //        println("j: " + j)
      //        println("k: " + LaTeX2Unicode.convert(j.replace("\\", "\\\\")))
      //        pw.write(LaTeX2Unicode.convert(j.replace("\\", "\\\\")))
      //      }

      for (t <- textChunks) {
        for (j <- t.replace("\\rm ", "").split("\n")) { //replaceAll("(<|>|\\.)", " $1 ").split("\n")) {
          if (!(j.startsWith("\\begin") || j.startsWith("\\end") || j.startsWith("\\include") || j.startsWith("\\userpackage") || j.startsWith("%"))) {
            //          println(">>" + j)
            for (i <- j.split(" ")) {
              //            println(i)
              //
              if (i.nonEmpty && isLanguage(i)) {
                //              println("i: " + i)
                if (i.contains("_")) {
                  // process subscripts and superscripts
                  val cleanedUp = AlignmentBaseline.replaceWordWithGreek(i.replace("_", " "), AlignmentBaseline.word2greekDict.toMap).replace(",", " , ")
                  //                println("i: " + i)
                  //                println("cleanedup: " + cleanedUp)
                  val withSubscr = try {
                    AlignmentBaseline.render(cleanedUp, AlignmentBaseline.pdfalignDir).split(" ")
                  } finally {
                    LaTeX2Unicode.convert(cleanedUp.replace("\\", "\\\\"))
                  }
                  val trimmedWithSubscr = withSubscr.head.trim
                  if (trimmedWithSubscr.nonEmpty) {
                    pw.write(withSubscr.head.trim + "\t" + "O" + "\n")

                  }
                  if (withSubscr.tail.nonEmpty) {
                    val withSubscrTailHead = withSubscr.tail.head.trim
                    if (withSubscrTailHead.nonEmpty) {
                      pw.write(withSubscrTailHead + "\t" + "B" + "\n")

                    }
                    for (k <- withSubscr.tail.tail) {
                      if (k.nonEmpty) {
                        pw.write(k.trim + "\t" + "I" + "\n")

                      }
                    }
                  }
                } else {
                  // if not latex seq, just replace greek
                  //                println("III: " + i)
                  if (!i.contains("\\")) {
                    //                  println("iii: " + i)
                    val toWrite = AlignmentBaseline.replaceWordWithGreek(i, AlignmentBaseline.word2greekDict.toMap)
                    //                  println("to write: " + toWrite)
                    if (toWrite.trim.nonEmpty) {
                      pw.write(toWrite.trim + "\t" + "O" + "\n")

                    }
                  } else {
                    if (!i.contains("\\label")) {
                      //                    println("jjj: " + i)
                      val replaceGreek = AlignmentBaseline.replaceWordWithGreek(i, AlignmentBaseline.word2greekDict.toMap)
                      //                    println("repl: " + replaceGreek)
                      val cleanedUp = replaceGreek.replace("\\", "\\\\")
                      val toWrite = try {
                        AlignmentBaseline.render(replaceGreek, AlignmentBaseline.pdfalignDir)
                      } catch {
                        case e: RuntimeException => LaTeX2Unicode.convert(cleanedUp)
                      }
                      //                    finally {
                      //                      println("womp womp")
                      //                    }
                      //                    println(toWrite)
                      if (toWrite.trim.nonEmpty) {
                        pw.write(toWrite.trim + "\t" + "O" + "\n")

                      }
                    }

                  }

                }

              }
            }
          }
        }
      }
      //println("DONE 2")
    }
    //    println("DONE 1 " + file.getName)

    // for this, the threshold is very low because it's only to filter out string that look like this $-------------$
    def isLanguage(string: String): Boolean = {
      val valid = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "
      val sentLength: Double = string.length
      val normalChars: Double = string.filter(c => valid contains c).length
      val proportion = normalChars / sentLength
      val threshold = 0.01 // fixme: tune
      //    println(s"$proportion --> ${mention.sentenceObj.getSentenceText}")
      if (proportion > threshold) {
        true
      } else false
    }


    // can just exclude the lines that start with \
    //    for (t <- texts) {
    //      println("Text: " + t)
    //      println("HERE: " + AlignmentBaseline.tokenize(t, AlignmentBaseline.pdfalignDir))
    //    }
    //    val string = """ a constant radiation background with the H$ 2$ photodissociation rate  \rho(q,z) &= \rho_0  the difference $e {\rm diss}  """
    //    println("HERE1: " + AlignmentBaseline.render(string, AlignmentBaseline.pdfalignDir))
    // could regex for the latex sequences and then tokenize whatever is in between
    // so like for the resulting list, when it's a latex sequence, use that and render, but if it's a simple string, tokenize in a regular way
    // 3. Extract causal mentions from the texts
    // todo: here I am choosing to pass each text/section through separately -- this may result in a difficult coref problem
    //    val mentions = texts.flatMap(reader.extractFromText(_, filename = Some(file.getName)))
    //The version of mention that includes routing between text vs. comment
    //    val mentions = texts.flatMap(text => textRouter.route(text).extractFromText(text, filename = Some(file.getName))).seq
    //    for (m <- mentions) {
    //      println("----------------")
    //      println(m.text)
    //
    //      if (m.arguments.nonEmpty) {
    //        for (arg <- m.arguments) {
    //          println("arg: " + arg._1 + ": " + m.arguments(arg._1).head.text)
    //        }
    //      }
    //
    //    }

    //    println("DONE 0")
    pw.close()


  } catch {
      case _ : Throwable => println("can't process file: " + file.getName)
    }
}

}


