package org.clulab.aske.automates

import com.typesafe.scalalogging.LazyLogging
import org.clulab.aske.automates.actions.ExpansionHandler
import org.clulab.odin._
import org.clulab.odin.impl.Taxonomy
import org.clulab.utils.{DisplayUtils, FileUtils}
import org.yaml.snakeyaml.Yaml
import org.yaml.snakeyaml.constructor.Constructor
import org.clulab.aske.automates.OdinEngine._
import org.clulab.aske.automates.entities.EntityHelper
import org.clulab.processors.fastnlp.FastNLPProcessor
import org.clulab.struct.Interval

import scala.collection.mutable
import scala.collection.mutable.ArrayBuffer
import scala.io.{BufferedSource, Source}



class OdinActions(val taxonomy: Taxonomy, expansionHandler: Option[ExpansionHandler], validArgs: List[String], freqWords: Array[String]) extends Actions with LazyLogging {

  val proc = new FastNLPProcessor()
  def globalAction(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {

//    for (m <- mentions) println("BEG OF GL ACTION: " + m.text + " " + m.labels + " " + m.foundBy)
    if (expansionHandler.nonEmpty) {
      // expand arguments
      //val (textBounds, expandable) = mentions.partition(m => m.isInstanceOf[TextBoundMention])
      //val expanded = expansionHandler.get.expandArguments(expandable, state)
      //keepLongest(expanded) ++ textBounds

//      def condition(m:Mention): Boolean = {
//        m matches "Definition"
//        m matches "EventMention"
//      }
//      for (e <- mentions) println("all-->" + e.text + " " + e.foundBy)
      val (vars, non_vars) = mentions.partition(m => m.label == "Variable")
//      println("variables: " + vars.map(m => m.text + " " + m.label + " " + m.labels.mkString("||")).mkString("\n"))
//      println("non-variables " + non_vars.map(_.text).mkString("\n"))
      val expandedVars = keepLongestVariable(vars)
//      println("expanded vars: " + expandedVars.map(_.text).mkString("\n"))

      val (expandable, other) = (expandedVars ++ non_vars).partition(m => m matches "Definition")
//      for (e <- other) println("o-->" + e.text + " " + e.foundBy)
//      for (e <- expandable) println("e-->" + e.text + " " + e.foundBy)
      val expanded = expansionHandler.get.expandArguments(expandable, state, validArgs) //todo: check if this is the best place for validArgs argument
      keepOneWithSameSpanAfterExpansion(expanded) ++ other
//       keepLongest(expanded) ++ other
//      expanded ++ other

//      other
//    mentions
//      expandable
//      expanded
      //val mostComplete = keepMostCompleteEvents(expanded, state.updated(expanded))
      //val result = mostComplete ++ textBounds
    } else {

//      for (e <- mentions) println("??-->" + e.text + " " + e.foundBy)
      mentions
    }
  }

  def findOverlappingInterval(tokenInt: Interval, intervals: List[Interval]): Interval = {
    val overlapping = new ArrayBuffer[Interval]()
    for (int <- intervals) {
      if (tokenInt.intersect(int).nonEmpty) overlapping.append(int)
    }
    return overlapping.maxBy(_.length)
  }

  def groupByTokenOverlap(mentions: Seq[Mention]): Map[Interval, Seq[Mention]] = {
    // has to be used for mentions in the same sentence - token intervals are per sentence
    val intervalMentionMap = mutable.Map[Interval, Seq[Mention]]()
    for (m <- mentions) {
      if (intervalMentionMap.isEmpty) {
//        println("++>" + intervalMentionMap)
        println("m tok int: " + m.tokenInterval)
        intervalMentionMap += (m.tokenInterval -> Seq(m))
      } else {
        println("---->" + intervalMentionMap)
        if (intervalMentionMap.keys.exists(k => k.intersect(m.tokenInterval).nonEmpty)) {
          val interval = findOverlappingInterval(m.tokenInterval, intervalMentionMap.keys.toList)
          val currMen = intervalMentionMap(interval)
          val updMen = currMen :+ m
          if (interval.length >= m.tokenInterval.length) {
            intervalMentionMap += (interval -> updMen)
          } else {
            intervalMentionMap += (m.tokenInterval -> updMen)
            intervalMentionMap.remove(interval)
          }

        } else {
          intervalMentionMap += (m.tokenInterval -> Seq(m))
        }
      }
    }
    println("---> " + intervalMentionMap.toMap)
    intervalMentionMap.toMap
  }

  def keepLongestVariable(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {

    for (v <- mentions) println("here:: " + v.text + " " + v.label)
    val maxInGroup = new ArrayBuffer[Mention]()
    val groupedBySent = mentions.groupBy(_.sentence)
    println("-> " + groupedBySent)
    for (gbs <- groupedBySent) {
      println("--> " + groupedBySent)
      val groupedByIntervalOverlap = groupByTokenOverlap(gbs._2)
      println(groupedByIntervalOverlap)
      for (item <- groupedByIntervalOverlap) {
        println(item._1)
        for (m <- item._2) println("here1: " + m.text)
        val longest = item._2.maxBy(_.tokenInterval.length)
        maxInGroup.append(longest)
      }

    }

    maxInGroup.distinct

  }


  /** Keeps the longest mention for each group of overlapping mentions **/
  def keepLongest(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    val mns: Iterable[Mention] = for {
      // find mentions of the same label and sentence overlap
      (k, v) <- mentions.groupBy(m => (m.sentence, m.label))
//      (k1, v1) <- v.groupBy(m => m.arguments("variable"))
      m <- v
      // for overlapping mentions starting at the same token, keep only the longest
      longest = v.filter(_.tokenInterval.overlaps(m.tokenInterval)).maxBy(m => (m.end - m.start) + 0.1 * m.arguments.size)
      //      longest = v.filter(_.tokenInterval.start == m.tokenInterval.start).maxBy(m => ((m.end - m.start) + 0.1 * m.arguments.size))

    } yield longest
    mns.toVector.distinct
  }

  def keepOneWithSameSpanAfterExpansion(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
//    for ((k, v) <- mentions.filter(_.arguments.keys.toList.contains("variable")).groupBy(men => men.arguments("variable").head.text)) {
////      println("New group: ")
////      for (vi <- v) println("men!!: " + vi.text + " " + vi.labels + " " + vi.foundBy + " " + vi.tokenInterval.mkString("-") + " " + vi.arguments.map(_._1).mkString("+"))
//    }
//    for (m <- mentions) println(">>>" + m.text + " " + m.label)
    val mns: Iterable[Mention] = for {
      // find mentions of the same label and sentence overlap
      (k, v) <- mentions.filter(_.arguments.keys.toList.contains("variable")).groupBy(men => men.arguments("variable").head.text)
      // conj defs have more vars, so from overlapping mentions, choose those that have most vars and...
      maxNumOfVars = v.maxBy(_.arguments("variable").length).arguments("variable").length
      //out of the ones with most vars, pick the longest
    } yield v.filter(_.arguments("variable").length == maxNumOfVars).maxBy(_.text.length)//v.maxBy(_.text.length)
    val mens = mns.toList
//    println("num of groups: " + mentions.groupBy(_.tokenInterval).keys.toList.length + " mens returned: " + mns.toList.distinct.length + " " + mentions.length)
    mens.toVector.distinct
  }

  def getEdgesForMention(m: Mention): List[(Int, Int, String)] = {
    // return only edges within the token interval of the mention
    m.sentenceObj.dependencies.get.allEdges.filter(edge => math.min(edge._1, edge._2) >= m.tokenInterval.start && math.max(edge._1, edge._2) <= m.tokenInterval.end)
  }

  def hasConj(m: Mention): Boolean = {
    val onlyThisMenedges = getEdgesForMention(m)
    onlyThisMenedges.map(_._3).exists(_.startsWith("conj"))
  }
  def untangleConj(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {

    // partition on those with and without conj
    // if !conjDef, take out interval between conj node start and end, store interval (is it possible to get char offset here?)
    // if conjdef, use conjDefinitions
    // get rid of cc's and cc:preconj (maybe just all cc's?)
    // account for cases when one conj is not part of the extracted definition
    // if plural noun (eg entopies) - lemmatize
    println("======" + mentions.length)




    def filterOutOverlappingMen(mentions: Seq[Mention]): Seq[Mention] = {
      // input is only mentions with the label ConjDefinition or Definition with conjunctions
      // this is to get rid of conj definitions that are redundant in the presence of a more complete ConjDefinition
      val toReturn = new ArrayBuffer[Mention]()
      val groupedBySent = mentions.groupBy(_.sentence)

      for (gr <- groupedBySent) {
        val groupedByTokenOverlap = groupByTokenOverlap(gr._2)
        for (gr1 <- groupedByTokenOverlap.values) {
          // if there are ConjDefs among overlapping defs (at this point, all of them are withConj), then pick the longest conjDef
          println("------")
          for (g <- gr1) println("overlapping " + g.text + " " + g.tokenInterval + " " + g.label)

          if (gr1.exists(_.label=="ConjDefinition")) {
            println("TRUE")
            val longestConjDef = gr1.filter(_.label == "ConjDefinition").maxBy(_.tokenInterval.length)
            println("longest: " + longestConjDef.text)
            toReturn.append(longestConjDef)
          } else {
            for (men <- gr1) toReturn.append(men)
          }
        }
      }
      toReturn
    }

    val (tempWithConj, withoutConj) = mentions.partition(hasConj(_))
//      val (withConj, withoutConj) = mentions.partition(hasConj(_))

    val withConj = filterOutOverlappingMen(tempWithConj)
    for (wc <- withConj) println("wc " + wc.text)
    for (woc <- withoutConj) println("woc " + woc.text)



    val (conjDefs, standardDefsWithConj) = withConj.partition(_.label matches "ConjDefinition")

    for (wc <- conjDefs) println("conjdef " + wc.text)
    for (woc <- standardDefsWithConj) println("standard def " + woc.text)

    val toReturn = new ArrayBuffer[Mention]()

//    val untangled = new ArrayBuffer[Mention]()
//    for (m <- conjDefs) {
//      val untang = untangleOneConjunction(m)
//      for (men <- untang) untangled.append(men)
//    }

    //maybe before appending, check if there's overlap between conjdefs and standard defs; if there is, drop the standard def or even check conjdef and regular def? can end up filtering out small defs like class I; yes, this is better done before bc then the conjDef is the lonest and will be easier to filter the others; not standard, withoutConj
    for (m <- untangleConjunctions(conjDefs)) {
//      println("m returned " + m.text)
      toReturn.append(m)
    }
    for (m <- withoutConj) toReturn.append(m)

    for (m <- standardDefsWithConj) toReturn.append(m)

    for (m <- standardDefsWithConj) {
      println("m: " + m.text )
      println("ti: " + m.tokenInterval)
//      println("full deps: " + m.sentenceObj.dependencies.get.allEdges)


      def returnWithoutConj(m: Mention, conjEdge: (Int, Int, String)): Unit = {
        // this should be the def text bound mention
        def getDiscontCharOffset(m: Mention, newTokenList: List[Int]): Unit = {
          val charOffsets = new ArrayBuffer[Array[Int]]
          var spanStartAndEndOffset = new ArrayBuffer[Int]()
          var prevTokenIndex = 0
          for ((tokenInt, indexOnList) <- newTokenList.zipWithIndex) {
            println("tok in and ind on list " + tokenInt + " " + indexOnList)
            if (indexOnList == 0) {
              spanStartAndEndOffset.append(m.sentenceObj.startOffsets(tokenInt))
              prevTokenIndex = tokenInt
            } else {
              if (!(prevTokenIndex + 1 == tokenInt) || indexOnList + 1 == newTokenList.length) {
                //this means, we have found the the gap in the token int
                // and the previous token was the end of previous part of the discont span, so we should get the endOffset of prev token
                spanStartAndEndOffset.append(m.sentenceObj.endOffsets(prevTokenIndex))
                charOffsets.append(spanStartAndEndOffset.toArray)
                spanStartAndEndOffset = new ArrayBuffer[Int]()
                spanStartAndEndOffset.append(m.sentenceObj.startOffsets(tokenInt))
                prevTokenIndex = tokenInt
              } else {
                prevTokenIndex = tokenInt
              }
            }

          }
          println("spans: ")
          for (ch <- charOffsets) {
            println("ch span " + ch.mkString(" "))
            println("span text: " + m.document.text.get.slice(ch.head, ch.last))
          }
        }
        val sortedConj = List(conjEdge._1, conjEdge._2).sorted
        println("sorted conj: " + sortedConj)
        val tokInAsList = m.tokenInterval.toList
        val newTokenInt = tokInAsList.filter(idx => idx < sortedConj.head || idx >= sortedConj.last)
        println("conj " + conjEdge)
        println("M: " + m.text)
        println("M orig token int " + tokInAsList)
        println("M new " + newTokenInt)
        println("m char offset: " + m.startOffset + " " + m.endOffset)


        val charOffsets = new ArrayBuffer[Int]()
        val wordsWIndex = m.sentenceObj.words.zipWithIndex

        val defTextWordsWithInd = wordsWIndex.filter(w => newTokenInt.contains(w._2))
        for (ind <- defTextWordsWithInd.map(_._2)) {
          charOffsets.append(m.sentenceObj.startOffsets(ind))
        }
        val defText = defTextWordsWithInd.map(_._1)
        println("_-_-_" + defText.mkString(" "))
        println("words char offset " + charOffsets)
        println("here:: " + m.document.text.get.slice(charOffsets.head, charOffsets(2)).mkString(""))
        getDiscontCharOffset(m, newTokenInt)

      }

      val edgesForOnlyThisMen = m.sentenceObj.dependencies.get.allEdges.filter(edge => math.min(edge._1, edge._2) >= m.tokenInterval.start && math.max(edge._1, edge._2) <= m.tokenInterval.end)
      println("only ours: " + edgesForOnlyThisMen)
      val maxConj = edgesForOnlyThisMen.filter(_._3.startsWith("conj")).sortBy(triple => math.abs(triple._1 - triple._2)).reverse.head
      println(maxConj + "<<")
      returnWithoutConj(m, maxConj)



//      println("mp filtered: " + m.sentenceObj.dependencies.get.incomingEdges.flatten.toList.filter(id => m.tokenInterval.contains(id._1)))

//      for (path <- m.paths) {
////        println("p: " + path)
//        for (x <- path._2) {
//          for (i <- x._2) {
//            println("----> " + x._1.text + " " + i._3)
//          }
//        }
//      }
    }
    // Only Def mentions will be passed
//    val (haveConj, no_conj) = mentions.partition(m => m.paths.map)
//    for (hc <- haveConj) println("hc: " + hc.text)
//    for (nc <- no_conj) println("nc: " + nc.text)

    toReturn
  }



  // this one worked separately but not when used within untangleConj
  def untangleConjunctions(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {


    // todo: only conj defs should get here
    // todo: if overlap, take most complete
    // todo: if conj is outside def but overlap, take longest - but how? i only annotated the def itself... maybe combine all defs if there are more than one?
//    val (conjDef, other) = mentions.partition(_ matches "ConjDefinition")
//    println(conjDef.length)
//    for (m <- mentions) println("Inside untangle conj: " + m.text + " " + m.label)
    val toReturn = new ArrayBuffer[Mention]()

    val groupedBySent = mentions.groupBy(_.sentence)
    for (gr1 <- groupedBySent) {
      val groupedByIntervalOverlap = groupByTokenOverlap(gr1._2)
//      println("GR LEN: " + groupedByIntervalOverlap.keys)
      for (gr <- groupedByIntervalOverlap) {
//        println("-->> " + gr._1 + " " + gr._2.length)
//        for (m <- gr._2) println(m.text)
        val mostComplete = gr._2.maxBy(_.arguments.toSeq.length)
//        println("most co,mplete: " + mostComplete.text)
        val headDef = mostComplete.arguments("definition").head
        //    println("head def: " + headDef.text)

        //fixme: try to do this without reannotating just using the method for finding deps for the edge
        val deps = proc.annotate(headDef.text).sentences.head.universalEnhancedDependencies.get
//        println("deps: " + deps)
println(">>>> " + deps.incomingEdges.flatten.mkString("|"))
        val tokenWithOutgoingConjAll = deps.incomingEdges.flatten.filter(_._2.contains("conj")).map(_._1)

//         val tokenWithOutgoingConj = tokenWithOutgoingConjAll.head//assume one
        //    println(tokenWithOutgoingConj)

        val incomingConjNodes = deps.outgoingEdges.flatten.filter(_._2.contains("conj")).map(_._1)
//        println(">>" + incomingConjNodes.mkString("||"))
        val previousIndices = new ArrayBuffer[Int]()

        val newDefinitions = new ArrayBuffer[Mention]()

        val allConjNodes = tokenWithOutgoingConjAll.head +: incomingConjNodes
        if (allConjNodes.length > 0) {
          for (int <- (allConjNodes).sorted) {
            //      println("prev indices: " + previousIndices)
            var newDefTokenInt = headDef.tokenInterval.slice(0, int + 1)
            //      println("defs" + int + " " + newDefTokenInt)
            if (previousIndices.nonEmpty) {

              for (pi <- previousIndices.reverse) {

                newDefTokenInt = newDefTokenInt.patch(pi, Nil, 1)

              }
            }
            //          println("new def tok in: " + newDefTokenInt)
            val wordsWIndex = headDef.sentenceObj.words.zipWithIndex
            val defText = wordsWIndex.filter(w => newDefTokenInt.contains(w._2)).map(_._1)
            val newDef = new TextBoundMention(headDef.labels, Interval(newDefTokenInt.head, newDefTokenInt.last + 1), headDef.sentence, headDef.document, headDef.keep, headDef.foundBy, headDef.attachments)
            newDefinitions.append(newDef)
            //          println("text " + defText.mkString(" "))
            previousIndices.append(int)
          }

        }


        val variables = mostComplete.arguments("variable")
        for ((v, i) <- variables.zipWithIndex) {
//          println("here: " + v.text + " " + i)
          if (newDefinitions.nonEmpty) {
            val newArgs = Map("variable" -> Seq(v), "definition" -> Seq(newDefinitions(i)))
            val newDefMen = copyWithArgs(mostComplete, newArgs)
            //          println("new def men line 335 "+newDefMen.text)
            toReturn.append(newDefMen)
          } else {
            val newArgs = Map("variable" -> Seq(v), "definition" -> Seq(headDef))
            val newDefMen = copyWithArgs(mostComplete, newArgs)
            //          println("new def men line 335 "+newDefMen.text)
            toReturn.append(newDefMen)
          }

        }

      }

    }

//    for (m <- toReturn) println("to ret 343 " + m.text)

    toReturn //++ other
  }



  def addArgument(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    for {
      m <- mentions
      argsToAdd = m.arguments - "original" // remove the original
      origMention = m.arguments("original").head // assumes one only
      combinedArgs = origMention.arguments ++ argsToAdd
    } yield copyWithArgs(origMention, combinedArgs)
  }

  def copyWithArgs(orig: Mention, newArgs: Map[String, Seq[Mention]]): Mention = {
    orig match {
      case tb: TextBoundMention => ???
      case rm: RelationMention => rm.copy(arguments = newArgs)
      case em: EventMention => em.copy(arguments = newArgs)
      case _ => ???
    }
  }

  def copyWithLabel(m: Mention, lab: String): Mention = {
    val newLabels = taxonomy.hypernymsFor(lab)
    val copy = m match {
      case tb: TextBoundMention => tb.copy(labels = newLabels)
      case rm: RelationMention => rm.copy(labels = newLabels)
      case em: EventMention=> em.copy(labels = newLabels)
      case _ => ???
    }
    copy
  }

  def variableArguments(mentions: Seq[Mention], state: State): Seq[Mention] = {
    val mentionsDisplayOnlyArgs = for {
      m <- mentions
      arg <- m.arguments.values.flatten
    } yield copyWithLabel(arg, "Variable")

    mentionsDisplayOnlyArgs
  }

  def modelArguments(mentions: Seq[Mention], state: State): Seq[Mention] = {
    val mentionsDisplayOnlyArgs = for {
      m <- mentions
      arg <- m.arguments.values.flatten
    } yield copyWithLabel(arg, "Model")

    mentionsDisplayOnlyArgs
  }

  def selectShorterAsVariable(mentions: Seq[Mention], state: State): Seq[Mention] = {
    def foundBy(base: String) = s"$base++selectShorter"

    def mkDefinitionMention(m: Mention): Seq[Mention] = {
      val outer = m.arguments("c1").head
      val inner = m.arguments("c2").head
      if (outer.text.split(" ").last.length == 1 & inner.text.length == 1) return Seq.empty // this is a filter that helps avoid splitting of compound variables, e.g. the rate R(t) - t should not be extracted as a variable with a definition 'rate R'
      val sorted = Seq(outer, inner).sortBy(_.text.length)
      // The longest mention (i.e., the definition) should be at least 3 characters, else it's likely a false positive
      // todo: tune
      // todo: should we constrain on the length of the variable name??
      // looksLikeAVariable is there to eliminate some false negatives, e.g., 'radiometer' in 'the Rn device (radiometer)':
      // might need to revisit
      if (sorted.last.text.length < 3 || looksLikeAVariable(Seq(sorted.head), state).isEmpty) {
        return Seq.empty
      }
      val variable = changeLabel(sorted.head, VARIABLE_LABEL) // the shortest is the variable
      val definition = changeLabel(sorted.last, DEFINITION_LABEL) // the longest if the definition
      val defMention = m match {
        case rm: RelationMention => rm.copy(
          arguments = Map(VARIABLE_ARG -> Seq(variable), DEFINITION_ARG -> Seq(definition)),
          foundBy=foundBy(rm.foundBy),
          tokenInterval = Interval(math.min(variable.start, definition.start), math.max(variable.end, definition.end)))
//         case em: EventMention => em.copy(//alexeeva wrote this to try to try to fix an appos. dependency rule todo: what seems to need don
        //is changing the keys in 'paths' to variable and defintion bc as of now they show up downstream (in the expansion handler) as c1 and c2
//           arguments = Map(VARIABLE_ARG -> Seq(variable), DEFINITION_ARG -> Seq(definition)),
//           foundBy=foundBy(em.foundBy),
//           tokenInterval = Interval(math.min(variable.start, definition.start), math.max(variable.end, definition.end)))
        case _ => ???
      }
      Seq(variable, defMention)
//      Seq(defMention)
    }

    mentions.flatMap(mkDefinitionMention)
  }


  def looksLikeAVariable(mentions: Seq[Mention], state: State): Seq[Mention] = {

    //returns mentions that look like a variable
    def passesFilters(v: Mention, isArg: Boolean): Boolean = {
      // If the variable was found with a Gazetteer passed through the webservice, keep it
      if ((v matches OdinEngine.VARIABLE_GAZETTEER_LABEL) && isArg) return true
      if (v.words.length == 1 && !(v.words.head.count(_.isLetter) > 0)) return false
      if ((v.words.length >= 1) && v.entities.get.exists(m => m matches "B-GreekLetter")) return true //account for var that include a greek letter---those are found as separate words even if there is not space
      if (v.words.length != 1) return false
      // Else, the variable candidate has length 1
      val word = v.words.head
      if (freqWords.contains(word.toLowerCase())) return false //filter out potential variables that are freq words
      if (word.length > 6) return false
      // a variable cannot be a unit
      if (v.entities.get.exists(_ == "B-unit")) return false
      val tag = v.tags.get.head
      if (tag == "POS") return false
      return (
        word.toLowerCase != word // mixed case or all UPPER
        |
        v.entities.exists(ent => ent.contains("B-GreekLetter")) //or is a greek letter
        |
        word.length == 1 && (tag.startsWith("NN") | tag == "FW") //or the word is one character long and is a noun or a foreign word (the second part of the constraint helps avoid standalone one-digit numbers, punct, and the article 'a'
        |
        word.length < 3 && word.exists(_.isDigit) && !word.contains("-")  && word.replaceAll("\\d|\\s", "").length > 0//this is too specific; trying to get to single-letter vars with a subscript (e.g., u2) without getting units like m-2
      |
          (word.length < 6 && tag != "CD") //here, we allow words for under 6 char bc we already checked above that they are not among the freq words
        )
    }
    for {
      m <- mentions
      (varMention, isArg) = m match {
        case tb: TextBoundMention => (m, false)
        case rm: RelationMention => (m.arguments.getOrElse("variable", Seq()).head, true)
        case em: EventMention => (m.arguments.getOrElse("variable", Seq()).head, true)
        case _ => ???
      }
      if passesFilters(varMention, isArg)
    } yield m
  }

  def looksLikeAVariableWithGreek(mentions: Seq[Mention], state: State): Seq[Mention] = {
    //returns mentions that look like a variable
    for {
      m <- mentions
      varMention = m match {
        case tb: TextBoundMention => m
        case rm: RelationMention => m.arguments.getOrElse("variable", Seq()).head
        case em: EventMention => m.arguments.getOrElse("variable", Seq()).head
        case _ => ???
      }
      if varMention.words.length < 3
      if varMention.entities.exists(ent => ent.exists(_ == "B-GreekLetter"))

    } yield m
  }


  def defIsNotVar(mentions: Seq[Mention], state: State): Seq[Mention] = {
    //returns mentions in which definitions are not also variables
    //and the variable and the definition don't overlap
    for {
      m <- mentions
      if !m.words.contains("not") //make sure, the definition is not negative

      variableMention = m.arguments.getOrElse("variable", Seq())
      defMention = m.arguments.getOrElse("definition", Seq())
      if (
        defMention.nonEmpty && //there has to be a definition
        looksLikeADef(defMention, state).nonEmpty && //make sure the def looks like a def
        defMention.head.text.length > 4 && //the def can't be the length of a var
        !defMention.head.text.contains("=") &&
        looksLikeAVariable(defMention, state).isEmpty //makes sure the definition is not another variable (or does not look like what could be a variable)
        &&
        defMention.head.tokenInterval.intersect(variableMention.head.tokenInterval).isEmpty //makes sure the variable and the definition don't overlap
        ) || (defMention.nonEmpty && freqWords.contains(defMention.head.text)) //the definition can be one short, frequent word
    } yield m
  }


  def definitionActionFlow(mentions: Seq[Mention], state: State): Seq[Mention] = {
    val toReturn = defIsNotVar(looksLikeAVariable(mentions, state), state)
    toReturn
  }

  def definitionActionFlowSpecialCase(mentions: Seq[Mention], state: State): Seq[Mention] = {
    //select shorter as var is only applicable to one rule, so it can't be part of the regular def. action flow
    val varAndDef = selectShorterAsVariable(mentions, state)
    val toReturn = if (varAndDef.nonEmpty) definitionActionFlow(varAndDef, state) else Seq.empty
    toReturn
  }



  def looksLikeAUnit(mentions: Seq[Mention], state: State): Seq[Mention] = {
    for {
      //every mention in array...
      m <- mentions
      //get the split text of the suspected unit
      unitTextSplit = m match {
          //for tbs, the text of the unit, is the text of the whole mention
        case tb: TextBoundMention => m.text.split(" ")
          //for relation and event mentions, the unit is the value of the arg with the argName "unit"
        case _ => {
          val unitArgs = m.arguments.getOrElse("unit", Seq())
          if (unitArgs.nonEmpty) {
            unitArgs.head.text.split(" ")
          }
          unitArgs.head.text.split(" ")
        }

      }
      //the pattern to check if the suspected unit contains dashes (e.g., m-1), slashes (e.g., MJ/kg, or square brackets
      //didn't add digits bc that resulted in more false positives (e.g., for years)
      pattern = "[-/\\[\\]]".r
      //negative pattern checks if the suspected unit contains char-s that should not be present in a unit
      negPattern = "[<>=]".r
      //the length constraints: the unit should consist of no more than 5 words and the first word of the unit should be no longer than 3 characters long (heuristics)
      if ((unitTextSplit.length <=5 && unitTextSplit.head.length <=3) || pattern.findFirstIn(unitTextSplit.mkString(" ")).nonEmpty ) && negPattern.findFirstIn(unitTextSplit.mkString(" ")).isEmpty
    } yield m
  }

  def looksLikeADef(mentions: Seq[Mention], state: State): Seq[Mention] = {
    val valid = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ "
    for {
      m <- mentions
      definText = m match {
        case tb: TextBoundMention => m
        case rm: RelationMention => m.arguments.getOrElse("definition", Seq()).head
        case em: EventMention => m.arguments.getOrElse("definition", Seq()).head
        case _ => ???
      }

      if definText.text.filter(c => valid contains c).length.toFloat / definText.text.length > 0.60
      // make sure there's at least one noun; there may be more nominal pos that will need to be included - revisit: excluded def like "Susceptible (S)"
//      if m.tags.get.exists(_.contains("N"))

    } yield m
  }

  def changeLabel(orig: Mention, label: String): Mention = {
    orig match {
      case tb: TextBoundMention => tb.copy(labels = taxonomy.hypernymsFor(label))
      case rm: RelationMention => rm.copy(labels = taxonomy.hypernymsFor(label))
      case em: EventMention => em.copy(labels = taxonomy.hypernymsFor(label))
    }
  }

}

object OdinActions {

  def apply(taxonomyPath: String, enableExpansion: Boolean, validArgs: List[String], freqWords: Array[String]) =
    {
      val expansionHandler = if(enableExpansion) {
      Some(ExpansionHandler())
      } else None
      new OdinActions(readTaxonomy(taxonomyPath), expansionHandler, validArgs, freqWords)
    }

  def readTaxonomy(path: String): Taxonomy = {
    val input = FileUtils.getTextFromResource(path)
    val yaml = new Yaml(new Constructor(classOf[java.util.Collection[Any]]))
    val data = yaml.load(input).asInstanceOf[java.util.Collection[Any]]
    Taxonomy(data)
  }
}
