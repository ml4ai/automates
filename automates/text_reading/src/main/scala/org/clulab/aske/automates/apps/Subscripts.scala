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
  // do latex normalizing AFTER sentence splitting - split sentences - done
  // handle $\lim_{n \rightarrow \infty} --- need to check for what can occur inside subscripts


  val config = ConfigFactory.load()

  val inputDir: String = "/Users/alexeeva/Desktop/automates-related/arxiv/tex_dir/fullCurrentBatch"
//  val inputDir: String = "/Users/alexeeva/Desktop/automates-related/arxiv/testSubscriptDataScript"
  //  val inputDir = "/Users/alexeeva/Desktop/subscripts/texfiles"
  val outputDir: String = "/Users/alexeeva/Desktop/automates-related/arxiv/tex_dir/secondPass/"
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
    val pw = new PrintWriter(new File(outputDir + file.getName.replace(".tex", "") + "subscripts_data_sample.tsv"))
    //    // println("FILE NAME" + file)
    // 1. Open corresponding output file and make all desired exporters
    //    // println(s"Extracting from ${file.getName}")
    // 2. Get the input file contents
    // note: for science parse format, each text is a section
    val texts = dataLoader.loadFile(file)

    //    for (t <- texts) {
    //      // println("t: " + t)
    //      // println("replaced: " +
    //        " " + t.replaceAll("\\\\begin\\{equation\\}(.|\\n)*\\\\end\\{equation\\}","")) //\{equation\}.*\\end\{equation\}
    //    }
    val filteredTexts = new ArrayBuffer[String]()
    val newCommands = mutable.Map[String, String]()
    for (t <- texts) {
      val splitText = t.replaceAll("\\\\begin\\{equation\\*?\\}(.|\\n)*?\\\\end\\{equation\\*?\\}" +
        "|" +
        "%.*?\\n" +
        "|" +
        "\\\\ref\\{.*?\\}?" +
        "|" +
        "\\\\cite\\{.*?\\}\\}?" +
        "|" +
        "\\\\label\\{.*?\\}\\}?", "")
        .split("\n\n") // split on two \n\n because it's only that that represents new paragraph

      // process new commands and if it's not a new command, check if the text is some sort of control sequence
      for (st <- splitText) {
        if (st.contains("\\newcommand")) {
          val split = st.split("\\}\\[?.*?\\]?\\{")
          //          // println("split: " + split.mkString("|||"))
          newCommands(split.head.replace("\\newcommand{", "")) = split.last.dropRight(1)
        } else if (!(st.startsWith("\\document")
          ||
          st.startsWith("\\usepackage")
          ||
          st.startsWith("\\begin")
          ||
          st.startsWith("\\end")
          ||
          st.startsWith("\\input")
          ||
          st.startsWith("\\author")
          ||
          st.startsWith("\\keywords")
          ||
          st.startsWith("\\altauthor")
          ||
          st.startsWith("\\affiliation")
          ||
          st.startsWith("\\include"))) {
          filteredTexts.append(st)
        }
      }
    }
    //    for (t <- filteredTexts) // println(">> " + t)
      val sentences = new ArrayBuffer[String]()

      // splitting filtered texts into sentences
      for (t <- filteredTexts) {
        val annotated = reader.annotate(t).sentences

        for (s <- annotated) {
          val sentString = t.slice(s.startOffsets.head, s.endOffsets.last)
          sentences.append(sentString)
//        // println("sentence: " + s.words.mkString(" "))
//        // println("sent: " + t.slice(s.startOffsets.head, s.endOffsets.last))
//        print("\n")
        }
      }

    val regex = """\w+\_\{+(.|\\s){1,20}\}\}*|\w+\_\w+""".r
    for (t <- sentences) {
      // search for regex in each sent (possible issue---latex sequences being tokenized as separate sentences, but why would they?)
      // println(">> " + t + "\n")

      val matches = regex.findAllIn(t).toList
      // println("matches: " + matches.mkString("||"))
      val matchIndices = regex.findAllMatchIn(t).toList
      val matchesStarts = matchIndices.map(m => (m.start)).toList
      val matchesEnds = matchIndices.map(m => (m.end)).toList
      val lastIndices = new ArrayBuffer[Int]()
      for ((mi, idx) <- matchesStarts.zipWithIndex) {
        //        // println("mi: " + mi + " " + matches(idx))
        if (!matches(idx).contains("{")) {
          lastIndices.append(matchIndices(idx).end)
        } else {
          loop.breakable {
            var lastReasonableEndIndex = 0 // why is this here?
            for (i <- 3 to 40) {
              val possibleMatch = t.slice(mi, mi + i)
              //              // println("possible match: " + possibleMatch)
              if (possibleMatch.contains("{") && isBalanced(possibleMatch, "{", "}")) {
                lastIndices.append(mi + i)
                val idx = mi + i
                //                // println("appending " + idx)
                loop.break()
              } //else {// println("not appending")}
            }
          }
        }
      }


            // println("starts len: " + matchesStarts.length)
      // println("starts: " + matchesStarts.mkString("||"))
            // println("last indices: " + lastIndices.length)
            // println("last indices: " + lastIndices.mkString("||"))

      // make sentence chunks based on the found start/end match offsets
      val textChunks = new ArrayBuffer[String]()
      for ((pos, idx) <- matchesStarts.zipWithIndex) {
        // println("idx: " + idx + " len: " + matchesStarts.length)
        // println("||> " + t.slice(pos, lastIndices(idx)))
        //        // println("pos and idx: " + pos + " " + idx)
        if (idx == 0) {
          // println("doing A")
          textChunks.append(t.slice(0, pos))
          textChunks.append(t.slice(pos, lastIndices(idx)))
          if (idx == matchesStarts.length - 1) {
            // println("doing B")

            textChunks.append(t.slice(lastIndices.last, t.length))
          }
        } else if (idx == matchesStarts.length - 1) {
          // println("doing C")
          textChunks.append(t.slice(pos, lastIndices(idx)))
          textChunks.append(t.slice(lastIndices.last, t.length))
        } else {
          // println("doing D")
          textChunks.append(t.slice(pos, lastIndices(idx)))
          val nextMatchStart = matchesStarts(idx + 1)
          textChunks.append(t.slice(lastIndices(idx), nextMatchStart))
        }
      }
      //todo: somewhere here, need to remove dollar signs



      var lastWritten = ""
      for (t <- textChunks.map(_.replace("$", ""))) {
//        // println("t: " + t)
        for (j <- t.replace("\\rm ", "").split("\n")) {
//          // println("j: " + j)
          if ( isLanguage(j) && (!(j.startsWith("\\begin") || j.startsWith("\\end") || j.startsWith("\\include") || j.startsWith("\\userpackage") || j.startsWith("%")))) {
//            // println(j + "<<<")
            // if it's a chunk with subscripts, remove spaces to make sure A_{5, 6} is not broken up into separate tokens
            val spacesInsideSubscriptsReplaced = if (j.contains("_")) j.replace(", ",",") else j
//            // println(spacesInsideSubscriptsReplaced + "<<")
            // rudimentary tokenization---can't use processor tokens because latex sequences are split
            for (i <- spacesInsideSubscriptsReplaced.split(" ")) {
              if (i.nonEmpty) {
                if (i.contains("_")) {
                  // println("-> " + i)
                  // process subscripts, e.g., A_{s,k}
                  val cleanedUp = AlignmentBaseline.replaceWordWithGreek(i.replace("_", " "), AlignmentBaseline.word2greekDict.toMap).replace(",", " , ").replace("  ", " ")
                  //                // println("i: " + i)
                  //                // println("cleanedup: " + cleanedUp)
                  val withSubscr = try {
                    AlignmentBaseline.render(cleanedUp, AlignmentBaseline.pdfalignDir).split(" ")
                  } finally {
                    LaTeX2Unicode.convert(cleanedUp.replace("\\", "\\\\"))
                  }

                  // this is just the subscripted variable, e.g., A
                  val trimmedWithSubscr = withSubscr.head.trim
//                  if (trimmedWithSubscr.nonEmpty) {
//                    val writingThis = withSubscr.head.trim + "\t" + "O" + "\n"
//                    pw.write(writingThis)
//                    lastWritten = writingThis
//
//                  }
                  if (withSubscr.tail.nonEmpty) {
                    // this is the first subscript, e.g, s in A_{s,k}
                    val withSubscrTailHead = withSubscr.tail.head.trim
                    // write the var with first subscript as B
                    val varWithFirstSubscript = trimmedWithSubscr + withSubscrTailHead
                    if (varWithFirstSubscript.nonEmpty) {
                      val writingThis = varWithFirstSubscript + "\t" + "B" + "\n"
                      pw.write(writingThis)
                      lastWritten = writingThis

                    }
                    // if there are more subscripts left (e.g., comma and k in A_{s,k}), write them as Is
//                    // println("with subscr tail tail: " + withSubscr.tail.tail.mkString("|"))
                    for (k <- withSubscr.tail.tail) {
                      if (k.nonEmpty) {
                        val writingThis = k.trim + "\t" + "I" + "\n"
                        // println("Is: " + writingThis)
                        pw.write(writingThis)
                        lastWritten = writingThis

                      }
                    }
                  }
                } else {
                  // if not latex seq, just replace greek
                  if (!i.contains("\\")) {
                    val toWrite = AlignmentBaseline.replaceWordWithGreek(i, AlignmentBaseline.word2greekDict.toMap)
                    // only write if non-empty
                    if (toWrite.trim.nonEmpty) {
                      val writingThis = toWrite.trim + "\t" + "O" + "\n"
                      pw.write(writingThis)
                      lastWritten = writingThis

                    }
                  } else {
                    // labels should have by now been replaced, but still
                    if (!i.contains("\\label")) {
                      val replaceGreek = AlignmentBaseline.replaceWordWithGreek(i, AlignmentBaseline.word2greekDict.toMap)
                      // todo: there may be an issue here---render and latex2unicode might not both work properly with double-slash
                      val cleanedUp = replaceGreek.replace("\\", "\\\\")
                      val toWrite = try {
                        AlignmentBaseline.render(replaceGreek, AlignmentBaseline.pdfalignDir)
                      } catch {
                        case e: RuntimeException => LaTeX2Unicode.convert(cleanedUp)
                      }
                      if (toWrite.trim.nonEmpty) {
                        val writingThis = toWrite.trim + "\t" + "O" + "\n"
                        pw.write(writingThis)
                        lastWritten = writingThis

                      }
                    }

                  }

                }

              }
            }
          }
        }
      }
      //// println("DONE 2")
      // write empty line to indicate sentence break; don't write a new line if have just written one
      if (lastWritten != "") {
        pw.write("\n")
        lastWritten = ""
      }

    }
    //    // println("DONE 1 " + file.getName)

    // for this, the threshold is very low because it's only to filter out string that look like this $-------------$
    def isLanguage(string: String): Boolean = {
      val valid = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "
      val sentLength: Double = string.length
      val normalChars: Double = string.filter(c => valid contains c).length
      val proportion = normalChars / sentLength
      val threshold = 0.01 // fixme: tune
      //    // println(s"$proportion --> ${mention.sentenceObj.getSentenceText}")
      if (proportion > threshold) {
        true
      } else false
    }


    // can just exclude the lines that start with \
    //    for (t <- texts) {
    //      // println("Text: " + t)
    //      // println("HERE: " + AlignmentBaseline.tokenize(t, AlignmentBaseline.pdfalignDir))
    //    }
    //    val string = """ a constant radiation background with the H$ 2$ photodissociation rate  \rho(q,z) &= \rho_0  the difference $e {\rm diss}  """
    //    // println("HERE1: " + AlignmentBaseline.render(string, AlignmentBaseline.pdfalignDir))
    // could regex for the latex sequences and then tokenize whatever is in between
    // so like for the resulting list, when it's a latex sequence, use that and render, but if it's a simple string, tokenize in a regular way
    // 3. Extract causal mentions from the texts
    // todo: here I am choosing to pass each text/section through separately -- this may result in a difficult coref problem
    //    val mentions = texts.flatMap(reader.extractFromText(_, filename = Some(file.getName)))
    //The version of mention that includes routing between text vs. comment
    //    val mentions = texts.flatMap(text => textRouter.route(text).extractFromText(text, filename = Some(file.getName))).seq
    //    for (m <- mentions) {
    //      // println("----------------")
    //      // println(m.text)
    //
    //      if (m.arguments.nonEmpty) {
    //        for (arg <- m.arguments) {
    //          // println("arg: " + arg._1 + ": " + m.arguments(arg._1).head.text)
    //        }
    //      }
    //
    //    }

    //    // println("DONE 0")
    pw.close()


  } catch {
      case _ : Throwable => // println("can't process file: " + file.getName)
    }
}

}


