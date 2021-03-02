package org.clulab.aske.automates

import com.typesafe.scalalogging.LazyLogging
import org.clulab.aske.automates.actions.ExpansionHandler
import org.clulab.odin.{Mention, _}
import org.clulab.odin.impl.Taxonomy
import org.clulab.utils.{DisplayUtils, FileUtils}
import org.yaml.snakeyaml.Yaml
import org.yaml.snakeyaml.constructor.Constructor
import org.clulab.aske.automates.OdinEngine._
import org.clulab.aske.automates.attachments.{DiscontinuousCharOffsetAttachment, ParamSettingIntAttachment, UnitAttachment}
import org.clulab.aske.automates.entities.EntityHelper
import org.clulab.processors.fastnlp.FastNLPProcessor
import org.clulab.struct.Interval

import scala.collection.mutable
import scala.collection.mutable.ArrayBuffer
import scala.io.{BufferedSource, Source}



class OdinActions(val taxonomy: Taxonomy, expansionHandler: Option[ExpansionHandler], validArgs: List[String], freqWords: Array[String]) extends Actions with LazyLogging {

  val proc = new FastNLPProcessor()
  def globalAction(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {


    if (expansionHandler.nonEmpty) {
      // expand arguments

      val (vars, non_vars) = mentions.partition(m => m.label == "Variable")
      val expandedVars = keepLongestVariable(vars)

      val (expandable, other) = (expandedVars ++ non_vars).partition(m => m matches "Definition")
      val expanded = expansionHandler.get.expandArguments(expandable, state, validArgs) //todo: check if this is the best place for validArgs argument
      keepOneWithSameSpanAfterExpansion(expanded) ++ other

    } else {
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
        intervalMentionMap += (m.tokenInterval -> Seq(m))
      } else {
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
    intervalMentionMap.toMap
  }


  def processParamSettingInt(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    val newMentions = new ArrayBuffer[Mention]() //Map("variable" -> Seq(v), "definition" -> Seq(newDefinitions(i)))
    for (m <- mentions) {
      val newArgs = mutable.Map[String, Seq[Mention]]() //Map("variable" -> Seq(v), "definition" -> Seq(newDefinitions(i)))
      val attachedTo = if (m.arguments.exists(arg => looksLikeAVariable(arg._2, state).nonEmpty)) "variable" else "concept"
      var inclLower: Option[Boolean] = None
      var inclUpper: Option[Boolean] = None
      for (arg <- m.arguments) {
        arg._1 match {
          case "valueLeastExcl" => {
            newArgs("valueLeast") = arg._2
            inclLower = Some(false)
          }
          case "valueLeastIncl" => {
          newArgs("valueLeast") = arg._2
            inclLower = Some(true)
        }
          case "valueMostExcl" => {
            newArgs("valueMost") = arg._2
            inclUpper = Some(false)
          }
          case "valueMostIncl" => {
            newArgs("valueMost") = arg._2
            inclUpper = Some(true)
          }

          case _ => newArgs(arg._1) = arg._2
        }
      }
//      for (arg <- m.arguments) {
//        if (arg._1 == "valueLeastExcl") {
//          newArgs("valueLeast") = arg._2
//        } else newArgs(arg._1) = arg._2
//      }

      val att = new ParamSettingIntAttachment(inclLower, inclUpper, attachedTo, "ParamSettingIntervalAtt")
      newMentions.append(copyWithArgs(m, newArgs.toMap).withAttachment(att))
    }
    newMentions
  }

  def processUnits(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    val newMentions = new ArrayBuffer[Mention]() //Map("variable" -> Seq(v), "definition" -> Seq(newDefinitions(i)))
    for (m <- mentions) {
      val newArgs = mutable.Map[String, Seq[Mention]]() //Map("variable" -> Seq(v), "definition" -> Seq(newDefinitions(i)))
      val attachedTo = if (m.arguments.exists(arg => looksLikeAVariable(arg._2, state).nonEmpty)) "variable" else "concept"

      val att = new UnitAttachment(attachedTo, "UnitAtt")
      newMentions.append(m.withAttachment(att))
    }
    newMentions
  }

  def keepLongestVariable(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    // used to avoid vars like R(t) being found as separate R, t, R(t, and so on
    val maxInGroup = new ArrayBuffer[Mention]()
    val groupedBySent = mentions.groupBy(_.sentence)
    for (gbs <- groupedBySent) {
      val groupedByIntervalOverlap = groupByTokenOverlap(gbs._2)
      for (item <- groupedByIntervalOverlap) {
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
      m <- v
      // for overlapping mentions starting at the same token, keep only the longest
      longest = v.filter(_.tokenInterval.overlaps(m.tokenInterval)).maxBy(m => (m.end - m.start) + 0.1 * m.arguments.size)
    } yield longest
    mns.toVector.distinct
  }

  def keepOneWithSameSpanAfterExpansion(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    val mns: Iterable[Mention] = for {
      // find mentions of the same label and sentence overlap
      (k, v) <- mentions.filter(_.arguments.keys.toList.contains("variable")).groupBy(men => men.arguments("variable").head.text)
      // conj defs have more vars, so from overlapping mentions, choose those that have most vars and...
      maxNumOfVars = v.maxBy(_.arguments("variable").length).arguments("variable").length
      //out of the ones with most vars, pick the longest
    } yield v.filter(_.arguments("variable").length == maxNumOfVars).maxBy(_.text.length)//v.maxBy(_.text.length)
    val mens = mns.toList
    mens.toVector.distinct
  }

  def getEdgesForMention(m: Mention): List[(Int, Int, String)] = {
    // return only edges within the token interval of the mention
    m.sentenceObj.dependencies.get.allEdges.filter(edge => math.min(edge._1, edge._2) >= m.tokenInterval.start && math.max(edge._1, edge._2) <= m.tokenInterval.end)
  }

  def filterOutOverlappingMen(mentions: Seq[Mention]): Seq[Mention] = {
    // input is only mentions with the label ConjDefinition or Definition with conjunctions
    // this is to get rid of conj definitions that are redundant in the presence of a more complete ConjDefinition
    val toReturn = new ArrayBuffer[Mention]()
    val groupedBySent = mentions.groupBy(_.sentence)

    for (gr <- groupedBySent) {
      val groupedByTokenOverlap = groupByTokenOverlap(gr._2)
      for (gr1 <- groupedByTokenOverlap.values) {
        // if there are ConjDefs among overlapping defs (at this point, all of them are withConj), then pick the longest conjDef
        if (gr1.exists(_.label=="ConjDefinition")) {
          val longestConjDef = gr1.filter(_.label == "ConjDefinition").maxBy(_.tokenInterval.length)
          toReturn.append(longestConjDef)
        } else {
          for (men <- gr1) toReturn.append(men)
        }
      }
    }
    toReturn
  }


  // this should be the def text bound mention
  def getDiscontCharOffset(m: Mention, newTokenList: List[Int]): Seq[(Int, Int)] = {
    val charOffsets = new ArrayBuffer[Array[Int]]
    var spanStartAndEndOffset = new ArrayBuffer[Int]()
    var prevTokenIndex = 0
    for ((tokenInt, indexOnList) <- newTokenList.zipWithIndex) {
      if (indexOnList == 0) {
        spanStartAndEndOffset.append(m.sentenceObj.startOffsets(tokenInt))
        prevTokenIndex = tokenInt
      } else {
        if (!(prevTokenIndex + 1 == tokenInt) ) {
          //this means, we have found the the gap in the token int
          // and the previous token was the end of previous part of the discont span, so we should get the endOffset of prev token
          spanStartAndEndOffset.append(m.sentenceObj.endOffsets(prevTokenIndex))
          charOffsets.append(spanStartAndEndOffset.toArray)
          spanStartAndEndOffset = new ArrayBuffer[Int]()
          spanStartAndEndOffset.append(m.sentenceObj.startOffsets(tokenInt))
          prevTokenIndex = tokenInt
          // if last token, get end offset and append resulting offset
          if (indexOnList + 1 == newTokenList.length) {
            spanStartAndEndOffset.append(m.sentenceObj.endOffsets(prevTokenIndex))
            charOffsets.append(spanStartAndEndOffset.toArray)
          }

        } else {
          // if last token, get end offset and append resulting offset
          if (indexOnList + 1 == newTokenList.length) {
            spanStartAndEndOffset.append(m.sentenceObj.endOffsets(prevTokenIndex))
            charOffsets.append(spanStartAndEndOffset.toArray)
          } else {
            prevTokenIndex = tokenInt
          }

        }
      }

    }
    val listOfIntCharOffsets = new ArrayBuffer[(Int, Int)]()
    for (item <- charOffsets) {
      listOfIntCharOffsets.append((item.head, item.last))
    }
    listOfIntCharOffsets
  }

  def returnWithoutConj(m: Mention, conjEdge: (Int, Int, String), preconj: Seq[Int]): Mention = {
    // only change the mention if there is a discontinuous char offset - if there is, make it into an attachment
    val sortedConj = List(conjEdge._1, conjEdge._2).sorted
    val tokInAsList = m.arguments("definition").head.tokenInterval.toList

    val newTokenInt = tokInAsList.filter(idx => (idx < sortedConj.head || idx >= sortedConj.last) & !preconj.contains(idx))

    val charOffsets = new ArrayBuffer[Int]()
    val wordsWIndex = m.sentenceObj.words.zipWithIndex

    val defTextWordsWithInd = wordsWIndex.filter(w => newTokenInt.contains(w._2))
    for (ind <- defTextWordsWithInd.map(_._2)) {
      charOffsets.append(m.sentenceObj.startOffsets(ind))
    }
    val defText = defTextWordsWithInd.map(_._1)
    val charOffsetsForAttachment= getDiscontCharOffset(m, newTokenInt)
    if (charOffsetsForAttachment.length > 1) {
      val attachment = new DiscontinuousCharOffsetAttachment(charOffsetsForAttachment, "definition", "DiscontinuousCharOffset")
      val menWithAttachment = m.withAttachment(attachment)
      menWithAttachment
    } else m

  }


  def hasConj(m: Mention): Boolean = {
    val onlyThisMenedges = getEdgesForMention(m)
    onlyThisMenedges.map(_._3).exists(_.startsWith("conj"))
  }

  /*
  A method for handling definitions depending on whether or not they have any conjoined elements
   */
  def untangleConj(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {

    // fixme: account for cases when one conj is not part of the extracted definition
    //todo: if plural noun (eg entopies) - lemmatize?

    // all that have conj (to be grouped further) and those with no conj
    val (tempWithConj, withoutConj) = mentions.partition(hasConj(_))
    // check if there's overlap between conjdefs and standard defs; if there is, drop the standard def
    val withConj = filterOutOverlappingMen(tempWithConj)
    // defs that were found as ConjDefinitions - that is events with multiple variables (at least partially) sharing a definitions vs definitions that were found with standard rule that happened to have conjunctions in their definitions
    val (conjDefs, standardDefsWithConj) = withConj.partition(_.label matches "ConjDefinition")

    val toReturn = new ArrayBuffer[Mention]()
    // the defs found with conj definition rules should be processed differently from standard defs that happen to have conjs
    for (m <- untangleConjunctions(conjDefs)) {
      toReturn.append(m)
    }

    for (m <- standardDefsWithConj) {
      val edgesForOnlyThisMen = m.sentenceObj.dependencies.get.allEdges.filter(edge => math.min(edge._1, edge._2) >= m.tokenInterval.start && math.max(edge._1, edge._2) <= m.tokenInterval.end)
      // take max conjunction hop contained inside the definition - that will be removed
      val maxConj = edgesForOnlyThisMen.filter(_._3.startsWith("conj")).sortBy(triple => math.abs(triple._1 - triple._2)).reverse.head
      val preconj = m.sentenceObj.dependencies.get.outgoingEdges.flatten.filter(_._2.contains("cc:preconj")).map(_._1)
      val newMention = returnWithoutConj(m, maxConj, preconj)
      toReturn.append(newMention)
    }
    // make sure to add non-conj events
    for (m <- withoutConj) toReturn.append(m)

    toReturn
  }


  /*
  a method for handling `ConjDefinition`s - definitions that were found with a special rule---the def has to have at least two conjoined variables and at least one (at least partially) shared definition
   */
  def untangleConjunctions(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {

    val toReturn = new ArrayBuffer[Mention]()

    val groupedBySent = mentions.groupBy(_.sentence)
    for (gr1 <- groupedBySent) {
      val groupedByIntervalOverlap = groupByTokenOverlap(gr1._2)
      for (gr <- groupedByIntervalOverlap) {
        val mostComplete = gr._2.maxBy(_.arguments.toSeq.length)
        // out of overlapping defs, take the longest one
        val headDef = mostComplete.arguments("definition").head
        val edgesForOnlyThisMen = headDef.sentenceObj.dependencies.get.allEdges.filter(edge => math.min(edge._1, edge._2) >= headDef.tokenInterval.start && math.max(edge._1, edge._2) <= headDef.tokenInterval.end)
        val conjEdges = edgesForOnlyThisMen.filter(_._3.startsWith("conj"))
        val conjNodes = new ArrayBuffer[Int]()
        for (ce <- conjEdges) {
          conjNodes.append(ce._1)
          conjNodes.append(ce._2)
        }
        val allConjNodes = conjNodes.distinct.sorted
        val preconj = headDef.sentenceObj.dependencies.get.outgoingEdges.flatten.filter(_._2.contains("cc:preconj")).map(_._1)
        val previousIndices = new ArrayBuffer[Int]()

        val newDefinitions = new ArrayBuffer[Mention]()
        val defAttachments = new ArrayBuffer[DiscontinuousCharOffsetAttachment]()

        if (allConjNodes.nonEmpty) {

          for (int <- allConjNodes.sorted) {
            val headDefStartToken = headDef.tokenInterval.start
            // the new def token interval is the longest def available with words like `both` and `either` removed and ...
            var newDefTokenInt = headDef.tokenInterval.filter(item => (item >= headDefStartToken & item <= int) & !preconj.contains(item))
            //...with intervening conj hops removed, e.g., in `a and b are the blah of c and d, respectively`, for the def of b, we will want to remove `c and ` - which make up the intervening conj hop
            if (previousIndices.nonEmpty) {
              newDefTokenInt = newDefTokenInt.filter(ind => ind < previousIndices.head || ind >= int )
            }

            val wordsWIndex = headDef.sentenceObj.words.zipWithIndex
//            val defText = wordsWIndex.filter(w => newDefTokenInt.contains(w._2)).map(_._1)
            val newDef = new TextBoundMention(headDef.labels, Interval(newDefTokenInt.head, newDefTokenInt.last + 1), headDef.sentence, headDef.document, headDef.keep, headDef.foundBy, headDef.attachments)
            newDefinitions.append(newDef)
            // store char offsets for discont def as attachments
            val charOffsetsForAttachment= getDiscontCharOffset(headDef, newDefTokenInt.toList)

            val attachment = new DiscontinuousCharOffsetAttachment(charOffsetsForAttachment, "definition", "DiscontinuousCharOffset")
            defAttachments.append(attachment)

            previousIndices.append(int)
          }
        }


        // get the conjoined vars
        val variables = mostComplete.arguments("variable")
        for ((v, i) <- variables.zipWithIndex) {
          // if there are new defs, we will assume that they should be matched with the vars in the linear left to right order
          if (newDefinitions.nonEmpty) {
            val newArgs = Map("variable" -> Seq(v), "definition" -> Seq(newDefinitions(i)))
            val newDefMen = copyWithArgs(mostComplete, newArgs)
            if (defAttachments(i).toUJson("charOffsets").arr.length > 1) {
              val newDefWithAtt = newDefMen.withAttachment(defAttachments(i))
              toReturn.append(newDefWithAtt)
            } else {
              toReturn.append(newDefMen)
            }

            // if there are no new defs, we just assume that the definition is shared between all the variables
          } else {
            val newArgs = Map("variable" -> Seq(v), "definition" -> Seq(headDef))
            val newDefMen = copyWithArgs(mostComplete, newArgs)
            toReturn.append(newDefMen)
          }
        }
      }

    }
    toReturn
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
//         case em: EventMention => em.copy(//alexeeva wrote this to try to try to fix an appos. dependency rule
        //is changing the keys in 'paths' to variable and defintion bc as of now they show up downstream (in the expansion handler) as c1 and c2
//           arguments = Map(VARIABLE_ARG -> Seq(variable), DEFINITION_ARG -> Seq(definition)),
//           foundBy=foundBy(em.foundBy),
//           tokenInterval = Interval(math.min(variable.start, definition.start), math.max(variable.end, definition.end)))
        case _ => ???
      }
      Seq(variable, defMention)
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

  def unitActionFlow(mentions: Seq[Mention], state: State): Seq[Mention] = {
    val toReturn = processUnits(looksLikeAUnit(mentions, state), state)
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
