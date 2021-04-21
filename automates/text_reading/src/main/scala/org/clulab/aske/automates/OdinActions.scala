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
import org.clulab.processors.fastnlp.FastNLPProcessor
import org.clulab.struct.Interval

import scala.collection.mutable
import scala.collection.mutable.ArrayBuffer




class OdinActions(val taxonomy: Taxonomy, expansionHandler: Option[ExpansionHandler], validArgs: List[String], freqWords: Array[String]) extends Actions with LazyLogging {

  val proc = new FastNLPProcessor()
  def globalAction(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {


    if (expansionHandler.nonEmpty) {
      // expand arguments

      val (identifiers, non_identifiers) = mentions.partition(m => m.label == "Identifier")
      val expandedIdentifiers = keepLongestIdentifier(identifiers)

      val (expandable, other) = (expandedIdentifiers ++ non_identifiers).partition(m => m.label.contains("Description"))

      val expanded = expansionHandler.get.expandArguments(expandable, state, validArgs)
      val (conjDescrType2, otherDescrs) = expanded.partition(_.label.contains("Type2"))
      // only keep type 2 conj descriptions that do not have description arg overlap AFTER expansion
      val allDescrs = noDescrOverlap(conjDescrType2) ++ otherDescrs
      keepOneWithSameSpanAfterExpansion(allDescrs) ++ other
//      allDescrs ++ other

    } else {
      mentions
    }
  }

  def findOverlappingInterval(tokenInt: Interval, intervals: List[Interval]): Interval = {
    val overlapping = new ArrayBuffer[Interval]()
    for (int <- intervals) {
      if (tokenInt.intersect(int).nonEmpty) overlapping.append(int)
    }
    overlapping.maxBy(_.length)
  }

  def keepWithGivenArgs(mentions: Seq[Mention], argTypes: Seq[String]): Seq[Mention] = {
    val toReturn = new ArrayBuffer[Mention]()
    for (m <- mentions) {
      if (m.arguments.keys.toList.intersect(argTypes).length == argTypes.length) {
        toReturn.append(m)
      }
    }
    toReturn
  }

  def groupByDescrOverlap(mentions: Seq[Mention]): Map[Interval, Seq[Mention]] = {
    // only apply this when there is one var and one descr
    // group mentions by token overlap of a given argument
    // has to be used for mentions in the same sentence - token intervals are per sentence

    val intervalMentionMap = mutable.Map[Interval, Seq[Mention]]()
    val mentionsWithRightArgs = keepWithGivenArgs(mentions, Seq("description"))
    for (m <- mentionsWithRightArgs) {
      // assume there's one of each arg
      val descrTextBoundMention = m.arguments("description").head
      if (intervalMentionMap.isEmpty) {
        intervalMentionMap += (descrTextBoundMention.tokenInterval -> Seq(m))
      } else {
        if (intervalMentionMap.keys.exists(k => k.intersect(descrTextBoundMention.tokenInterval).nonEmpty)) {
          val interval = findOverlappingInterval(descrTextBoundMention.tokenInterval, intervalMentionMap.keys.toList)
          val currMen = intervalMentionMap(interval)
          val updMen = currMen :+ m
          if (interval.length >= descrTextBoundMention.tokenInterval.length) {
            intervalMentionMap += (interval -> updMen)
          } else {
            intervalMentionMap += (descrTextBoundMention.tokenInterval -> updMen)
            intervalMentionMap.remove(interval)
          }

        } else {
          intervalMentionMap += (descrTextBoundMention.tokenInterval -> Seq(m))
        }
      }
    }
    intervalMentionMap.toMap
  }

  def groupByTokenOverlap(mentions: Seq[Mention]): Map[Interval, Seq[Mention]] = {
    // has to be used for mentions in the same sentence - token intervals are per sentence
    val intervalMentionMap = mutable.Map[Interval, Seq[Mention]]()
    // start with longest - the shorter overlapping ones should be subsumed this way
    for (m <- mentions.sortBy(_.tokenInterval).reverse) {
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
    val newMentions = new ArrayBuffer[Mention]() //Map("variable" -> Seq(v), "description" -> Seq(newDescriptions(i)))
    for (m <- mentions) {
      val newArgs = mutable.Map[String, Seq[Mention]]() //Map("variable" -> Seq(v), "description" -> Seq(newDescriptions(i)))
      val attachedTo = if (m.arguments.exists(arg => looksLikeAnIdentifier(arg._2, state).nonEmpty)) "variable" else "concept"
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


      val att = new ParamSettingIntAttachment(inclLower, inclUpper, attachedTo, "ParamSettingIntervalAtt")
      newMentions.append(copyWithArgs(m, newArgs.toMap).withAttachment(att))
    }
    newMentions
  }

  def processUnits(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    val newMentions = new ArrayBuffer[Mention]()
    for (m <- mentions) {
      val newArgs = mutable.Map[String, Seq[Mention]]()
      val attachedTo = if (m.arguments.exists(arg => looksLikeAnIdentifier(arg._2, state).nonEmpty)) "variable" else "concept"
      val att = new UnitAttachment(attachedTo, "UnitAtt")
      newMentions.append(m.withAttachment(att))
    }
    newMentions
  }


  def processParamSetting(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    val newMentions = new ArrayBuffer[Mention]()
    for (m <- mentions) {
      val newArgs = mutable.Map[String, Seq[Mention]]()
      val attachedTo = if (m.arguments.exists(arg => looksLikeAnIdentifier(arg._2, state).nonEmpty)) "variable" else "concept"

      val att = new UnitAttachment(attachedTo, "ParamSetAtt")
      newMentions.append(m.withAttachment(att))
    }
    newMentions
  }

  def keepLongestIdentifier(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    // used to avoid identifiers like R(t) being found as separate R, t, R(t, and so on
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
    // after expanding descriptions and ConjDescriptions, eliminate redundant mentions;
    // out of overlapping mentions, keep the ones that have more than one variable - those are the conj descriptions that can be "untangled" - those are the events that have more than one var-descr combos in them
    val mns = new ArrayBuffer[Mention]()

    // group by sentence
    val sentGroup = mentions.filter(_.arguments.contains("variable")).groupBy(_.sentence)
    for ((sentId, sameSentMentions) <- sentGroup) {
      // group by group
      val spanGroups = sameSentMentions.groupBy(_.tokenInterval)

      for (sg <- spanGroups) {
        // check the max number of args (conj descrs type 2 have at least two var-descr pairs (i.e., at least 4 args)
        val maxNumOfArgs = sg._2.maxBy(_.arguments.values.flatten.toList.length).arguments.values.flatten.toList.length
        // check the max num of variables in the mentions in the overlapping group - we want to preserve conj descrs and those will have most vars
        val maxNumOfVars = sg._2.maxBy(_.arguments("variable").length).arguments("variable").length
        // chose a mention with most args and most vars - if they have the same span and same (max) num of args and vars, it shouldnt matter which one it is, so take the first one
        val chosenMen = sg._2.filter(m => m.arguments("variable").length == maxNumOfVars & m.arguments.values.flatten.toList.length==maxNumOfArgs).head
        mns.append(chosenMen)
      }
    }

    val mens = mns.toList
    mens.toVector.distinct
  }

  def filterDescrsByOffsets(mentions: Seq[Mention], filterBy: String ,state: State = new State()): Seq[Mention] = {
    // get rid of overlapping descriptions; depending on when we need to use it, we will check descr start offset or end offset - it also makes sense to do both directions
    val mns = new ArrayBuffer[Mention]()

    // group by sentence
    val sentGroup = mentions.filter(_.arguments.contains("variable")).groupBy(_.sentence)
    for ((sentId, sameSentMentions) <- sentGroup) {

      val spanGroups = filterBy match {
        case "varAndDescrStartOffset" => sameSentMentions.filter(_.arguments.contains("variable")).groupBy(m => (m.arguments("variable").head, m.arguments("description").head.startOffset))
        case "varAndDescrEndOffset" => sameSentMentions.filter(_.arguments.contains("variable")).groupBy(m => (m.arguments("variable").head, m.arguments("description").head.endOffset))
        case _ => ???

      }

      for (sg <- spanGroups) {
        // out of the overlapping group, choose the one with longest descr
        val chosenMen = sg._2.maxBy(_.arguments("description").head.text.length)
        mns.append(chosenMen)
      }
    }

    mns.toVector.distinct
  }

  def noOverlapInGivenArg(mention: Mention, argType: String): Boolean = {
    // check if mention contains overlapping args of a given type
    val argsOfGivenType = mention.arguments(argType)
    val groupedByTokenInt = groupByTokenOverlap(argsOfGivenType)
    // if there is an overlap in args, those will be grouped => the number of groups will be lower than the number of args
    groupedByTokenInt.keys.toList.length == argsOfGivenType.length
  }

  def noDescrOverlap(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    // used for type2 conj descriptions
    // only keep the ones that have the same number of vars and descriptions
    val sameNumOfVarsAndDescrs = mentions.filter(m => m.arguments("variable").length == m.arguments("description").length)
    // and avoid the ones where there is descr overlap
    sameNumOfVarsAndDescrs.filter(noOverlapInGivenArg(_, "description"))

  }

  def getEdgesForMention(m: Mention): List[(Int, Int, String)] = {
    // return only edges within the token interval of the mention
    m.sentenceObj.dependencies.get.allEdges.filter(edge => math.min(edge._1, edge._2) >= m.tokenInterval.start && math.max(edge._1, edge._2) <= m.tokenInterval.end)
  }

  def filterOutOverlappingDescrMen(mentions: Seq[Mention]): Seq[Mention] = {
    // input is only mentions with the label ConjDescription (types 1 and 2) or Description with conjunctions
    // this is to get rid of conj descriptions that are redundant in the presence of a more complete ConjDescription
    val toReturn = new ArrayBuffer[Mention]()
    val groupedBySent = mentions.groupBy(_.sentence)

    for (gr <- groupedBySent) {

      val groupedByTokenOverlap = groupByTokenOverlap(gr._2)
      for (gr1 <- groupedByTokenOverlap.values) {
        // if there are ConjDescrs among overlapping decsrs (at this point, all of them are withConj), then pick the longest conjDescr
        if (gr1.exists(_.label.contains("ConjDescription"))) {
          // type 2 has same num of vars and descriptions (a minimum of two pairs)
          val (type2, type1) = gr1.partition(_.label.contains("Type2"))

          if (type2.isEmpty) {
            // use conf descrs type 1 only if there are no overlapping (more complete) type 2 descriptions
            val longestConjDescr = gr1.filter(_.label == "ConjDescription").maxBy(_.tokenInterval.length)
            toReturn.append(longestConjDescr)
          } else {
            val longestConjDescr = gr1.filter(_.label == "ConjDescriptionType2").maxBy(_.tokenInterval.length)
            toReturn.append(longestConjDescr)
          }

        } else {
          for (men <- gr1) toReturn.append(men)
        }
      }
    }
    toReturn
  }


  // keep this as a stub for function action flow
   def functionActionFlow(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
     mentions.distinct
   }

  // this should be the descr text bound mention
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
    val descrMention = m.arguments("description").head
    val tokInAsList = descrMention.tokenInterval.toList

    val newTokenInt = tokInAsList.filter(idx => (idx < sortedConj.head || idx >= sortedConj.last) & !preconj.contains(idx))

    val charOffsets = new ArrayBuffer[Int]()
    val wordsWIndex = m.sentenceObj.words.zipWithIndex

    val descrTextWordsWithInd = wordsWIndex.filter(w => newTokenInt.contains(w._2))
    for (ind <- descrTextWordsWithInd.map(_._2)) {
      charOffsets.append(m.sentenceObj.startOffsets(ind))
    }
    val descrText = descrTextWordsWithInd.map(_._1)
    val charOffsetsForAttachment= getDiscontCharOffset(m, newTokenInt)
    if (charOffsetsForAttachment.length > 1) {
      val attachment = new DiscontinuousCharOffsetAttachment(charOffsetsForAttachment,  "DiscontinuousCharOffset")
      // attach the attachment to the descr arg
      val descrMenWithAttachment = descrMention.withAttachment(attachment)
      val newArgs = Map("variable" -> Seq(m.arguments("variable").head), "description" -> Seq(descrMenWithAttachment))

        copyWithArgs(m, newArgs)
    } else m

  }


  def hasConj(m: Mention): Boolean = {
    val onlyThisMenEdges = getEdgesForMention(m)
    onlyThisMenEdges.map(_._3).exists(_.startsWith("conj"))
  }

  /*
  A method for handling descriptions depending on whether or not they have any conjoined elements
   */
  def untangleConj(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {

    // fixme: account for cases when one conj is not part of the extracted description
    //todo: if plural noun (eg entopies) - lemmatize?

    val (descrs, nondescrs) = mentions.partition(_.label.contains("Description"))
    // check if there's overlap between conjdescrs and standard descrs; if there is, drop the standard descr; add nondescrs
    val withoutOverlap = filterOutOverlappingDescrMen(descrs) ++ nondescrs
    // all that have conj (to be grouped further) and those with no conj
    val (withConj, withoutConj) = withoutOverlap.partition(m => hasConj(m))

    // descrs that were found as ConjDescriptions - that is events with multiple variables (at least partially) sharing a descriptions vs descriptions that were found with standard rule that happened to have conjunctions in their descriptions
    val (conjDescrs, standardDescrsWithConj) = withConj.partition(_.label.contains("ConjDescription"))
    val (conjType2, conjType1) = withConj.partition(_.label.contains("Type2"))

    val toReturn = new ArrayBuffer[Mention]()


    for (m <- untangleConjunctionsType2(conjType2)) {
      toReturn.append(m)
    }
    // the descrs found with conj description rules should be processed differently from standard descrs that happen to have conjs
    for (m <- untangleConjunctions(conjType1)) {
      toReturn.append(m)
    }

    for (m <- standardDescrsWithConj) {
      // only apply this to descriptions where var is to the right of the description, e.g., '...individuals who are either Susceptible (S), Infected (I), or Recovered (R)." In other cases observed so far, it removes chunks of descriptions it shouldn't remove
      if (m.arguments("variable").head.startOffset > m.arguments("description").head.startOffset) {
        val edgesForOnlyThisMen = m.sentenceObj.dependencies.get.allEdges.filter(edge => math.min(edge._1, edge._2) >= m.tokenInterval.start && math.max(edge._1, edge._2) <= m.tokenInterval.end)
        // take max conjunction hop contained inside the description - that will be removed
        val maxConj = edgesForOnlyThisMen.filter(_._3.startsWith("conj")).sortBy(triple => math.abs(triple._1 - triple._2)).reverse.head
        val preconj = m.sentenceObj.dependencies.get.outgoingEdges.flatten.filter(_._2.contains("cc:preconj")).map(_._1)
        val newMention = returnWithoutConj(m, maxConj, preconj)
        toReturn.append(newMention)
      } else toReturn.append(m)

    }
    // make sure to add non-conj events
    for (m <- withoutConj) toReturn.append(m)


    // filter by start offset can eliminate the shorter description 'index' if there are two overlapping descriptions - "index" and "index card"; filter by end offset can eliminate the shorter description 'index' if there are two overlapping descriptions - "index" and "leaf area index"
    filterDescrsByOffsets(filterDescrsByOffsets(toReturn, "varAndDescrStartOffset"), "varAndDescrEndOffset")

  }

  def untangleConjunctionsType2(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    // conj descr type 2 - equal number of vars and descrs, but at least 2 of each
    val toReturn = new ArrayBuffer[Mention]()
    for (m <- mentions) {
      val variableArgs = m.arguments("variable")
      val descrArgs = m.arguments("description")
      // should have correct number of args, but doing a sanity check
      if (variableArgs.length == descrArgs.length) {
        // corresponding vars and descrs will come in the same order, eg "v1, v2, and v3 stand for descr1, descr2, and descr3, respectively"
        val varsSortedByTokenInt = variableArgs.sortBy(_.tokenInterval)
        val descrsSortedByTokenInt = descrArgs.sortBy(_.tokenInterval)
        for ((v, i) <- varsSortedByTokenInt.zipWithIndex) {
          val newDescrMen = descrsSortedByTokenInt(i)
          val newArgs = Map("variable" -> Seq(v), "description" -> Seq(newDescrMen))
          val newInt = Interval(math.min(v.tokenInterval.start, newDescrMen.tokenInterval.start), math.max(v.tokenInterval.end, newDescrMen.tokenInterval.end))
          toReturn.append(new EventMention(
            m.labels,
            newInt,
            m.asInstanceOf[EventMention].trigger,
            newArgs,
            m.paths, // the paths are off
            m.sentence,
            m.document,
            m.keep,
            m.foundBy ++ "++untangleConjunctionsType2",
            Set.empty
          ))
        }
      } else {
        logger.debug(s"Number of vars is not equal to number of descrs:\nvariables: ${variableArgs.map(_.text).mkString(",")}\n${descrArgs.map(_.text).mkString(",")}")
      }
    }

    toReturn

  }

  /*
  a method for handling `ConjDescription`s - descriptions that were found with a special rule---the descr has to have at least two conjoined variables and at least one (at least partially) shared description
   */
  def untangleConjunctions(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {

    val toReturn = new ArrayBuffer[Mention]()

    val groupedBySent = mentions.groupBy(_.sentence)
    for (gr1 <- groupedBySent) {
      val groupedByIntervalOverlap = groupByTokenOverlap(gr1._2)
      for (gr <- groupedByIntervalOverlap) {
        val mostComplete = gr._2.maxBy(_.arguments.toSeq.length)
        // out of overlapping descrs, take the longest one
        val headDescr = mostComplete.arguments("description").head
        val edgesForOnlyThisMen = headDescr.sentenceObj.dependencies.get.allEdges.filter(edge => math.min(edge._1, edge._2) >= headDescr.tokenInterval.start && math.max(edge._1, edge._2) <= headDescr.tokenInterval.end)
        val conjEdges = edgesForOnlyThisMen.filter(_._3.startsWith("conj"))
        val conjNodes = new ArrayBuffer[Int]()
        for (ce <- conjEdges) {
          conjNodes.append(ce._1)
          conjNodes.append(ce._2)
        }
        val allConjNodes = conjNodes.distinct.sorted
        val preconj = headDescr.sentenceObj.dependencies.get.outgoingEdges.flatten.filter(_._2.contains("cc:preconj")).map(_._1)
        val previousIndices = new ArrayBuffer[Int]()

        val newDescriptions = new ArrayBuffer[Mention]()
        val descrAttachments = new ArrayBuffer[DiscontinuousCharOffsetAttachment]()

        if (allConjNodes.nonEmpty) {

          for (int <- allConjNodes.sorted) {
            val headDescrStartToken = headDescr.tokenInterval.start
            // the new descr token interval is the longest descr available with words like `both` and `either` removed and ...
            var newDescrTokenInt = headDescr.tokenInterval.filter(item => (item >= headDescrStartToken & item <= int) & !preconj.contains(item))
            //...with intervening conj hops removed, e.g., in `a and b are the blah of c and d, respectively`, for the descr of b, we will want to remove `c and ` - which make up the intervening conj hop
            if (previousIndices.nonEmpty) {
              newDescrTokenInt = newDescrTokenInt.filter(ind => ind < previousIndices.head || ind >= int )
            }

            val wordsWIndex = headDescr.sentenceObj.words.zipWithIndex
//            val descrText = wordsWIndex.filter(w => newDescrTokenInt.contains(w._2)).map(_._1)
            val newDescr = new TextBoundMention(headDescr.labels, Interval(newDescrTokenInt.head, newDescrTokenInt.last + 1), headDescr.sentence, headDescr.document, headDescr.keep, headDescr.foundBy, headDescr.attachments)
            newDescriptions.append(newDescr)
            // store char offsets for discont descr as attachments
            val charOffsetsForAttachment= getDiscontCharOffset(headDescr, newDescrTokenInt.toList)

            val attachment = new DiscontinuousCharOffsetAttachment(charOffsetsForAttachment, "DiscontinuousCharOffset")
            descrAttachments.append(attachment)

            previousIndices.append(int)
          }
        }


        // get the conjoined vars
        val variables = mostComplete.arguments("variable")
        for ((v, i) <- variables.zipWithIndex) {
          // if there are new descrs, we will assume that they should be matched with the vars in the linear left to right order
          if (newDescriptions.nonEmpty) {

            val newArgs = Map("variable" -> Seq(v), "description" -> Seq(newDescriptions(i)))
            val newInt = Interval(math.min(v.tokenInterval.start, newDescriptions(i).tokenInterval.start), math.max(v.tokenInterval.end, newDescriptions(i).tokenInterval.end))
            // construct a new description with new token int, foundBy, and args
            val newDescrMen = mostComplete match {
              case e: EventMention => {
                new EventMention(
                  mostComplete.labels,
                  newInt,
                  mostComplete.asInstanceOf[EventMention].trigger,
                  newArgs,
                  mostComplete.paths, // the paths are off; fixme: drop paths to one of the old args or consturct new paths somehow
                  mostComplete.sentence,
                  mostComplete.document,
                  mostComplete.keep,
                  mostComplete.foundBy ++ "++untangleConjunctions",
                  Set.empty
                )
              }
              case r: RelationMention => {
                new RelationMention(
                  mostComplete.labels,
                  newInt,
                  newArgs,
                  mostComplete.paths, // the paths are off
                  mostComplete.sentence,
                  mostComplete.document,
                  mostComplete.keep,
                  mostComplete.foundBy ++ "++untangleConjunctions",
                  Set.empty
                )
              }
              case _ => ???

            }

            if (descrAttachments(i).toUJson("charOffsets").arr.length > 1) {
              val descrWithAtt = newDescriptions(i).withAttachment(descrAttachments(i))
              val newArgs = Map("variable" -> Seq(v), "description" -> Seq(descrWithAtt))
              val newDescrMenWithAtt = copyWithArgs(mostComplete, newArgs)
              toReturn.append(newDescrMenWithAtt)
            } else {
              val newArgs = Map("variable" -> Seq(v), "description" -> Seq(newDescriptions(i)))
              val newDescrMen = copyWithArgs(mostComplete, newArgs)
              toReturn.append(newDescrMen)
            }

            // if there are no new descrs, we just assume that the description is shared between all the variables
          } else {
            val newArgs = Map("variable" -> Seq(v), "description" -> Seq(headDescr))
            val newInt = Interval(math.min(v.tokenInterval.start, headDescr.tokenInterval.start), math.max(v.tokenInterval.end, headDescr.tokenInterval.end))
            val newDescrMen = mostComplete match {
              case e: EventMention => {
                new EventMention(
                  mostComplete.labels,
                  newInt,
                  mostComplete.asInstanceOf[EventMention].trigger,
                  newArgs,
                  mostComplete.paths, // the paths are off
                  mostComplete.sentence,
                  mostComplete.document,
                  mostComplete.keep,
                  mostComplete.foundBy ++ "++untangleConjunctions",
                  Set.empty
                )
              }
              case r: RelationMention => {
                new RelationMention(
                  mostComplete.labels,
                  newInt,
                  newArgs,
                  mostComplete.paths, // the paths are off
                  mostComplete.sentence,
                  mostComplete.document,
                  mostComplete.keep,
                  mostComplete.foundBy ++ "++untangleConjunctions",
                  Set.empty
                )
              }
              case _ => ???
            }
            toReturn.append(newDescrMen)
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

  def identifierArguments(mentions: Seq[Mention], state: State): Seq[Mention] = {
    val mentionsDisplayOnlyArgs = for {
      m <- mentions
      arg <- m.arguments.values.flatten
    } yield copyWithLabel(arg, "Identifier")

    mentionsDisplayOnlyArgs
  }

  def modelArguments(mentions: Seq[Mention], state: State): Seq[Mention] = {
    val mentionsDisplayOnlyArgs = for {
      m <- mentions
      arg <- m.arguments.values.flatten
    } yield copyWithLabel(arg, "Model")

    mentionsDisplayOnlyArgs
  }

  def functionArguments(mentions: Seq[Mention], state: State): Seq[Mention] = {
    val mentionsDisplayOnlyArgs = for {
      m <- mentions
      arg <- m.arguments.values.flatten
    } yield copyWithLabel(arg, "Function")

    mentionsDisplayOnlyArgs
  }

  def selectShorterAsIdentifier(mentions: Seq[Mention], state: State): Seq[Mention] = {
    def foundBy(base: String) = s"$base++selectShorter"

    def mkDescriptionMention(m: Mention): Seq[Mention] = {
      val outer = m.arguments("c1").head
      val inner = m.arguments("c2").head
      if (outer.text.split(" ").last.length == 1 & inner.text.length == 1) return Seq.empty // this is a filter that helps avoid splitting of compound variables/identifiers, e.g. the rate R(t) - t should not be extracted as a variable with a description 'rate R'
      val sorted = Seq(outer, inner).sortBy(_.text.length)
      // The longest mention (i.e., the description) should be at least 3 characters, else it's likely a false positive
      // todo: tune
      // todo: should we constrain on the length of the variable name??
      // looksLikeAnIdentifier is there to eliminate some false negatives, e.g., 'radiometer' in 'the Rn device (radiometer)':
      // might need to revisit
      if (sorted.last.text.length < 3 || looksLikeAnIdentifier(Seq(sorted.head), state).isEmpty) {
        return Seq.empty
      }
      val variable = changeLabel(sorted.head, IDENTIFIER_LABEL) // the shortest is the variable/identifier
      val description = changeLabel(sorted.last, DESCRIPTION_LABEL) // the longest if the description
      val descrMention = m match {
        case rm: RelationMention => rm.copy(
          arguments = Map(VARIABLE_ARG -> Seq(variable), DESCRIPTION_ARG -> Seq(description)),
          foundBy=foundBy(rm.foundBy),
          tokenInterval = Interval(math.min(variable.start, description.start), math.max(variable.end, description.end)))
//         case em: EventMention => em.copy(//alexeeva wrote this to try to try to fix an appos. dependency rule
        //is changing the keys in 'paths' to variable and description bc as of now they show up downstream (in the expansion handler) as c1 and c2
//           arguments = Map(VARIABLE_ARG -> Seq(variable), DEFINITION_ARG -> Seq(description)),
//           foundBy=foundBy(em.foundBy),
//           tokenInterval = Interval(math.min(variable.start, description.start), math.max(variable.end, description.end)))
        case _ => ???
      }
      Seq(variable, descrMention)
    }

    mentions.flatMap(mkDescriptionMention)
  }


  def looksLikeAnIdentifier(mentions: Seq[Mention], state: State): Seq[Mention] = {

    //returns mentions that look like an identifier
    def passesFilters(v: Mention, isArg: Boolean): Boolean = {
      // If the variable/identifier was found with a Gazetteer passed through the webservice, keep it
      if (v == null) return false
      if ((v matches OdinEngine.VARIABLE_GAZETTEER_LABEL) && isArg) return true
      if (v.words.length < 3 && v.entities.exists(ent => ent.exists(_ == "B-GreekLetter"))) return true
      if (v.words.length == 1 && !(v.words.head.count(_.isLetter) > 0)) return false
      if ((v.words.length >= 1) && v.entities.get.exists(m => m matches "B-GreekLetter")) return true //account for identifiers that include a greek letter---those are found as separate words even if there is not space
      if (v.words.length==4) {
        // to account for identifiers like R(t)
        if (v.words(1) == "(" & v.words(3) == ")" ) return true
      }
      if (v.words.length != 1) return false
      if (v.words.head.contains("-") & v.words.head.last.isDigit) return false
      // Else, the identifier candidate has length 1
      val word = v.words.head
      if (freqWords.contains(word.toLowerCase())) return false //filter out potential variables that are freq words
      if (word.length > 6) return false
      // an identifier/variable cannot be a unit
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
        word.length < 3 && word.exists(_.isDigit) && !word.contains("-")  && word.replaceAll("\\d|\\s", "").length > 0//this is too specific; trying to get to single-letter identifiers with a subscript (e.g., u2) without getting units like m-2
      |
          (word.length < 6 && tag != "CD") //here, we allow words for under 6 char bc we already checked above that they are not among the freq words
        )
    }


    for {
      m <- mentions
      // Identifiers are extracted as a variable argument
      (varMention, isArg) = m match {
        case tb: TextBoundMention => (m, false)
        case rm: RelationMention => {
          if (m.arguments.contains("variable")) {
            (m.arguments("variable").head, true)
          } else (null, false)
        }
        case em: EventMention => (m.arguments.getOrElse("variable", Seq()).head, true)
        case _ => ???
      }
      if passesFilters(varMention, isArg)
    } yield m
  }

  def looksLikeAnIdentifierWithGreek(mentions: Seq[Mention], state: State): Seq[Mention] = {
    //returns mentions that look like an identifier
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


  def descrIsNotVar(mentions: Seq[Mention], state: State): Seq[Mention] = {
    //returns mentions in which descriptions are not also variables
    //and the variable and the description don't overlap
    for {
      m <- mentions
      if !m.words.contains("not") //make sure, the description is not negative

      variableMention = m.arguments.getOrElse("variable", Seq())
      descrMention = m.arguments.getOrElse("description", Seq())
      if (
        descrMention.nonEmpty && //there has to be a description
        looksLikeADescr(descrMention, state).nonEmpty && //make sure the descr looks like a descr
        descrMention.head.text.length > 4 && //the descr can't be the length of a var
        !descrMention.head.text.contains("=") &&
        looksLikeAnIdentifier(descrMention, state).isEmpty //makes sure the description is not another variable (or does not look like what could be an identifier)
        &&
        descrMention.head.tokenInterval.intersect(variableMention.head.tokenInterval).isEmpty //makes sure the variable and the description don't overlap
        ) || (descrMention.nonEmpty && freqWords.contains(descrMention.head.text)) //the description can be one short, frequent word
    } yield m
  }


  def descriptionActionFlow(mentions: Seq[Mention], state: State): Seq[Mention] = {
    val toReturn = descrIsNotVar(looksLikeAnIdentifier(mentions, state), state)
    toReturn
  }

  def descriptionActionFlowSpecialCase(mentions: Seq[Mention], state: State): Seq[Mention] = {
    //select shorter as var (identifier) is only applicable to one rule, so it can't be part of the regular descr. action flow
    val varAndDescr = selectShorterAsIdentifier(mentions, state)
    val toReturn = if (varAndDescr.nonEmpty) descriptionActionFlow(varAndDescr, state) else Seq.empty
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

  def looksLikeADescr(mentions: Seq[Mention], state: State): Seq[Mention] = {
    val valid = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ "
    for {
      m <- mentions
      descrText = m match {
        case tb: TextBoundMention => m
        case rm: RelationMention => m.arguments.getOrElse("description", Seq()).head
        case em: EventMention => m.arguments.getOrElse("description", Seq()).head
        case _ => ???
      }

      if descrText.text.filter(c => valid contains c).length.toFloat / descrText.text.length > 0.60
      // make sure there's at least one noun; there may be more nominal pos that will need to be included - revisit: excluded descr like "Susceptible (S)"
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
