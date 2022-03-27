package org.clulab.aske.automates


import com.typesafe.scalalogging.LazyLogging
import edu.stanford.nlp.dcoref.Dictionaries.MentionType
import org.clulab.aske.automates.actions.ExpansionHandler
import org.clulab.odin.{Mention, _}
import org.clulab.odin.impl.Taxonomy
import org.clulab.utils.FileUtils
import org.yaml.snakeyaml.Yaml
import org.yaml.snakeyaml.constructor.Constructor
import org.clulab.aske.automates.OdinEngine._
import org.clulab.aske.automates.attachments.{ContextAttachment, DiscontinuousCharOffsetAttachment, FunctionAttachment, ParamSetAttachment, ParamSettingIntAttachment, UnitAttachment}
import org.clulab.aske.automates.mentions.CrossSentenceEventMention
import org.clulab.processors.Document
import org.clulab.processors.fastnlp.FastNLPProcessor
import org.clulab.struct.Interval
import org.clulab.utils.MentionUtils.distinctByText

import scala.collection.mutable
import scala.collection.mutable.ArrayBuffer
import scala.math.Ordering
import scala.util.Try
import scala.util.matching.Regex
import scala.util.control.Breaks._




class OdinActions(val taxonomy: Taxonomy, expansionHandler: Option[ExpansionHandler], validArgs: List[String], freqWords: Array[String]) extends Actions with LazyLogging {

  val proc = new FastNLPProcessor()

  def globalAction(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {

    //mentions
    if (expansionHandler.nonEmpty) {
      // expand arguments

      val (values, non_values) = mentions.partition(m => m.label == "Value")
      // making sure we put together values that got broken up in tokenization
      val expandedValues = keepLongestValue(values)
      val (identifiers, non_identifiers) = (expandedValues ++ non_values).partition(m => m.label == "Identifier")
      val expandedIdentifiers = keepLongestIdentifier(identifiers)
      val (descriptions, other) = (expandedIdentifiers ++ non_identifiers).partition(m => m.label.contains("Description"))
      val (functions, nonFunc) = other.partition(m => m.label.contains("Function"))
      val (modelDescrs, nonModelDescrs) = nonFunc.partition(m => m.labels.contains("ModelDescr"))

      // only expand concepts in param settings and units, not the identifier-looking variables (e.g., expand `temperature` in `temparature is set to 0`, but not `T` in `T is set to 0`)
      val (paramSettingsAndUnitsNoIdfr, nonExpandable) = nonModelDescrs.partition(m => (m.label.contains("ParameterSetting") || m.label.contains("UnitRelation")) && !m.arguments("variable").head.labels.contains("Identifier"))

      val expandedParamSettings = expansionHandler.get.expandArguments(paramSettingsAndUnitsNoIdfr, state, List("variable"))

      val expandedDescriptions = expansionHandler.get.expandArguments(descriptions, state, validArgs)

      val expandedFunction = expansionHandler.get.expandArguments(functions, state, List("input", "output"))
      val expandedModelDescrs = expansionHandler.get.expandArguments(modelDescrs, state, List("modelDescr"))
      val (conjDescrType2, otherDescrs) = expandedDescriptions.partition(_.label.contains("Type2"))
      // only keep type 2 conj definitions that do not have definition arg overlap AFTER expansion
      val allDescrs = noDescrOverlap(conjDescrType2) ++ otherDescrs

      resolveCoref(keepOneWithSameSpanAfterExpansion(allDescrs) ++ expandedFunction ++ expandedParamSettings ++ expandedModelDescrs ++ nonExpandable)
      //      allDescrs ++ other
    } else {
      mentions
    }

  }

  def findOverlappingInterval(tokenInt: Interval, intervals: Seq[Interval]): Option[Interval] = {
    val overlapping = new ArrayBuffer[Interval]()
    for (int <- intervals) {
      if (tokenInt.intersect(int).nonEmpty) overlapping.append(int)
    }
    if (overlapping.nonEmpty) {
      Some(overlapping.maxBy(_.length))
    } else None

  }

  def findMentionWithOverlappingInterval(tokenInt: Interval, mentions: Seq[Mention]): Option[Mention] = {
    val overlapping = new ArrayBuffer[Mention]()
    for (m <- mentions) {
      if (tokenInt.intersect(m.tokenInterval).nonEmpty) overlapping.append(m)
    }
    if (overlapping.nonEmpty) {
      Some(overlapping.maxBy(_.text.length))
    } else None

  }

  def replaceWithLongerIdentifier(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    val toReturn = new ArrayBuffer[Mention]()
    // group identifiers by sentence to avoid replacing an identifier from one sent with a longer identifier from a different one
    val allIdentifierMentionsBySent = mentions.filter(_.label == "Identifier").groupBy(_.sentence)
    val (mentionsWithIdentifier, other) = mentions.partition(m => m.arguments.contains("variable") && m.arguments("variable").head.label == "Identifier") // for now, if there are two vars, then both would be either identifiers or not identifiers, so can just check the first one
    for (m <- mentionsWithIdentifier) {
      val newIdentifiers = new ArrayBuffer[Mention]()
      for (varArg <- m.arguments("variable")) {
        val overlappingMention = findMentionWithOverlappingInterval(varArg.tokenInterval, allIdentifierMentionsBySent(m.sentence))
        if (overlappingMention.nonEmpty) {
          newIdentifiers.append(overlappingMention.get)
        }
      }
      if (newIdentifiers.nonEmpty) {
        // construct a new mention with the new identifiers
        val newArgs = m.arguments.filter(_._1 != "variable") ++ Map("variable" -> newIdentifiers)
        val newMen = copyWithArgs(m, newArgs)
        toReturn.append(newMen)
      }
    }
    toReturn ++ other
  }

  def replaceWithLongerValue(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    // this appears to work correctly, but also seems unnecessary right now; can enable as needed
    val toReturn = new ArrayBuffer[Mention]()
    // group values by sentence to avoid replacing a value from one sent with a longer value from a different one
    val allValueMentionsBySent = mentions.filter(_.label == "Value").groupBy(_.sentence)
    val (mentionsWithValues, other) = mentions.partition(m => m.arguments.keys.exists(_.contains("value")))
    for (m <- mentionsWithValues) {
      val newArgs = mutable.Map[String, Seq[Mention]]()
      for (arg <- m.arguments.keys) {
        if (arg.contains("value")) {
          for (valArg <- m.arguments(arg)) {
            val overlappingMention = findMentionWithOverlappingInterval(valArg.tokenInterval, allValueMentionsBySent(m.sentence))
            if (overlappingMention.nonEmpty) {
              newArgs += (arg -> Seq(overlappingMention.get))
            }
          }
        }
      }

      if (newArgs.nonEmpty) {
        // construct a new mention with the new identifiers
        val finalArgs = m.arguments.filter(!_._1.contains("value")) ++ newArgs.toMap
        val newMen = copyWithArgs(m, finalArgs)
        toReturn.append(newMen)
      }
    }
    toReturn ++ other
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
          val interval = findOverlappingInterval(descrTextBoundMention.tokenInterval, intervalMentionMap.keys.toSeq).get
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
    // returns a map of intervals to mentions that overlap with that (max) interval
    // has to be used for mentions in the same sentence - token intervals are per sentence
    val intervalMentionMap = mutable.Map[Interval, Seq[Mention]]()
    // start with longest - the shorter overlapping ones should be subsumed this way
    for (m <- mentions.sortBy(_.tokenInterval.length).reverse) {
      if (intervalMentionMap.isEmpty) {
        intervalMentionMap += (m.tokenInterval -> Seq(m))
      } else {
        if (intervalMentionMap.keys.exists(k => k.intersect(m.tokenInterval).nonEmpty)) {
          val interval = findOverlappingInterval(m.tokenInterval, intervalMentionMap.keys.toSeq).get
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

  // solution from https://stackoverflow.com/questions/9542126/how-to-find-if-a-scala-string-is-parseable-as-a-double-or-not
  def parseDouble(s: String): Option[Double] = Try {
    s.toDouble
  }.toOption

  def processParamSettingInt(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    val newMentions = new ArrayBuffer[Mention]()
    for (m <- mentions) {
      val valueArgs = m.arguments.filter(_._1.contains("value"))
      // if there are two value args, that means we have both least and most value, so it makes sense to try to remap the least and most values in case they are in the wrong order (example: "... varying from 27 000 to 22000...")
      val valueMentionsSorted: Option[Seq[Mention]] = if (valueArgs.toSeq.length == 2) {
        // check if the values are actual numbers
        if (valueArgs.forall(arg => parseDouble(arg._2.head.text.replace(" ", "")).isDefined)) {
          // if yes, sort them in increasing order (so that the least value is first and most is last)
          Some(valueArgs.flatMap(_._2).toSeq.sortBy(_.text.replace(" ", "").toDouble))
        } else None
      } else None

      val newArgs = mutable.Map[String, Seq[Mention]]()
      val attachedTo = if (m.arguments.exists(arg => looksLikeAnIdentifier(arg._2, state).nonEmpty)) "variable" else "concept"
      var inclLower: Option[Boolean] = None
      var inclUpper: Option[Boolean] = None
      for (arg <- m.arguments) {
        arg._1 match {
          case "valueLeastExcl" => {
            newArgs("valueLeast") = if (valueMentionsSorted.isDefined) {
              Seq(valueMentionsSorted.get.head)
            } else arg._2
            inclLower = Some(false)
          }
          case "valueLeastIncl" => {
            newArgs("valueLeast") = if (valueMentionsSorted.isDefined) {
              Seq(valueMentionsSorted.get.head)
            } else arg._2
            inclLower = Some(true)
          }
          case "valueMostExcl" => {
            newArgs("valueMost") = if (valueMentionsSorted.isDefined) {
              Seq(valueMentionsSorted.get.last)
            } else arg._2
            inclUpper = Some(false)
          }
          case "valueMostIncl" => {
            newArgs("valueMost") = if (valueMentionsSorted.isDefined) {
              Seq(valueMentionsSorted.get.last)
            } else arg._2
            inclUpper = Some(true)
          }

          // assumes only one variable argument
          case "variable" => {
            newArgs(arg._1) = if (looksLikeAnIdentifier(arg._2, state).nonEmpty) Seq(copyWithLabel(arg._2.head, "Identifier")) else arg._2
          }
          case _ => newArgs(arg._1) = arg._2
        }
      }

      // required for expansion
      val newPaths = mutable.Map[String, Map[Mention, SynPath]]()

      // this will only need to be done for events, not relation mentions---relation mentions don't have paths
      if (m.paths.nonEmpty) {
        // synpaths for each mention in the picture
        val synPaths = m.paths.flatMap(_._2)
        // we have remapped the args to new names already; now will need to update the paths map to have correct new names and the correct synpaths for switched out min/max values
        for (arg <- newArgs) {
          // for each arg type, get the synpath for its new mention (for now, assume one arg of each type)
          newPaths += (arg._1 -> Map(arg._2.head -> synPaths(newArgs(arg._1).head)))
        }
      }

      val att = new ParamSettingIntAttachment(inclLower, inclUpper, attachedTo, "ParamSettingIntervalAtt")
      val newMen = copyWithArgsAndPaths(m, newArgs.toMap, newPaths.toMap)

      newMentions.append(newMen.withAttachment(att))
    }
    newMentions
  }

  def processUnits(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    val newMentions = new ArrayBuffer[Mention]()
    for (m <- mentions) {
      val newArgs = mutable.Map[String, Seq[Mention]]()
      val attachedTo = if (m.arguments.exists(arg => looksLikeAnIdentifier(arg._2, state).nonEmpty)) {
        newArgs += ("variable" -> Seq(copyWithLabel(m.arguments("variable").head, "Identifier")), "unit" -> m.arguments("unit"))
        "variable"
      } else {
        newArgs += ("variable" -> m.arguments("variable"), "unit" -> m.arguments("unit"))
        "concept"
      }
      val att = new UnitAttachment(attachedTo, "UnitAtt")
      newMentions.append(copyWithArgs(m, newArgs.toMap).withAttachment(att))
    }
    newMentions
  }


  def returnFirstNPInterval(mention: Mention): Option[Interval] = {
    val nPChunks = new ArrayBuffer[Int]()
    for ((chunk, idx) <- mention.sentenceObj.chunks.get.zipWithIndex) {

      if (chunk.contains("NP")) {
        nPChunks.append(idx)
      }
    }
    if (nPChunks.nonEmpty) {
      val contSpan = findContinuousSpan(nPChunks)
      Some(Interval(contSpan.head, contSpan.last + 1))
    } else None
  }

  def findContinuousSpan(indices: Seq[Int]): Seq[Int] = {
    val toReturn = new ArrayBuffer[Int]()
    // append current index
    for ((item, idx) <- indices.zipWithIndex) {
      toReturn.append(item)
      // if reached end of seq or if the next index is more than one step away (that means we have reached the end of the continuous index span), return what we have assembled by now
      if (idx == indices.length - 1 || indices(idx + 1) - item != 1) {
        return toReturn
      }
    }
    toReturn
  }

  def replaceIt(mention: Mention): Mention = {
    val firstBNPInterval = returnFirstNPInterval(mention)

    if (firstBNPInterval.isDefined) {
      val newVarArg = new TextBoundMention(
        mention.labels,
        firstBNPInterval.get,
        mention.sentence,
        mention.document,
        mention.keep,
        "resolving_coref",
        Set.empty
      )
      val newArgs = mutable.Map[String, Seq[Mention]]()
      for (arg <- mention.arguments) {
        if (arg._1 == "variable") {
          newArgs += (arg._1 -> Seq(newVarArg))
        } else {
          newArgs += (arg._1 -> mention.arguments(arg._1))
        }
      }
      copyWithArgs(mention, newArgs.toMap)
    } else mention
  }

  // assume the first NP in a sentence is what `it` resolves to;
  // see "An Investigation of Coreference Phenomena in the Biomedical Domain", Bell et al (2016): "a generally trustworthy heuristic that the earliest named entity in the sentence is likely to be the antecedent of a pronoun if they match grammatically (Hobbs, 1978)." The risk of first NP in our papers of interest not matching grammarically is, probably, low enough to just take the first NP for now
  def resolveCoref(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    val (withIt, woIt) = mentions.partition(m => m.arguments.contains("variable") && m.arguments("variable").head.text == "it")
    val resolved: Seq[Mention] = withIt.map(m => replaceIt(m))
    resolved ++ woIt
  }

  // resolve anaphors with the closest model name that is found within the same block & within 10 sentences
  // the resolved mentions are cross sentence event mention type (associated with two sentences)
  def resolveModelCoref(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    val (models, nonModels) = mentions.partition(m => m.label == "ModelDescr")
    val (theModel, modelNames) = models.partition(m => m.arguments.contains("modelName") && m.arguments("modelName").head.foundBy == "the/this_model" || m.arguments.contains("modelName") && m.arguments("modelName").head.foundBy == "model_pronouns")
    val resolved: Seq[Mention] = theModel.map(m => replaceTheModel(mentions, m).get)
    (resolved ++ modelNames ++ nonModels).distinct
  }

  def replaceTheModel(mentions: Seq[Mention], origModel: Mention): Option[Mention] = {
    val previousModel = returnPreviousModel(mentions, origModel)
    val newArgs = mutable.Map[String, Seq[Mention]]()
    for (arg <- origModel.arguments) {
      if (arg._1 == "modelName") {
        if (previousModel.nonEmpty) { // if there is a previous model name to be resolved with, that model name is attached to newArgs
          newArgs += (arg._1 -> Seq(previousModel.get))
        }
      } else { // if not, original model name is attached to newArgs
        newArgs += (arg._1 -> origModel.arguments(arg._1))
      }
    }
    val finalMen = if (previousModel.nonEmpty) { // create a new cross sentence event mention with the newArgs & sentences
      val sentences = new ArrayBuffer[Int]
      sentences.append(previousModel.get.sentence)
      sentences.append(origModel.sentence)
      val resolvedMen = new CrossSentenceEventMention(
        origModel.labels,
        origModel.tokenInterval,
        origModel.asInstanceOf[EventMention].trigger,
        newArgs.toMap,
        origModel.paths,
        origModel.sentence,
        sentences,
        origModel.document,
        origModel.keep,
        origModel.foundBy ++ "++ resolveModelCoref",
        origModel.attachments
      )
      Some(resolvedMen)
    } else Some(copyWithArgs(origModel, newArgs.toMap))
    finalMen
  }

  // find the closest model name with which an anaphor (i.e., the/this model, pronouns) will be resolved. If there's none, return none.
  def returnPreviousModel(mentions: Seq[Mention], origModel: Mention): Option[Mention] = {
    val (models, nonModels) = mentions.partition(m => m.label == "Model")
    val (theModels, modelNames) = models.partition(m => m.foundBy == "the/this_model" || m.foundBy == "our_model" || m.foundBy == "model_pronouns")
    // previousModels is for cases where model name is given within the same sentence with the anaphor
    // previousModels2 is for cases where model name is given in the previous sentences
    val previousModels = modelNames.filter(_.sentence <= origModel.sentence)
    val previousModels2 = modelNames.filter(_.sentence < origModel.sentence)
    if (previousModels.nonEmpty) {
      val selectedModel = previousModels.maxBy(_.sentence)
      val finalModel = if (selectedModel.sentence == origModel.sentence) {
        // when the model name is given within the same sentence with the anaphor, see if the selected model name comes before the anaphor
        if (selectedModel.startOffset < origModel.startOffset) {
          Some(selectedModel) // if yes, return that
          // if not, return the next closest model name. If there's no such model name, return none.
        } else if (previousModels2.nonEmpty) Some(previousModels2.maxBy(_.sentence)) else None
      } else Some(selectedModel) // if the model name is given in the previous sentence, just return that
      if (finalModel.nonEmpty && origModel.sentence - finalModel.get.sentence < 10) finalModel else None // if the closest model name is located within 10 sentences, return final model. If not, return none.
    } else None // if there's no previous model name, return none.
  }

  def processFunctions(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = { // action for function attachments
    val newMentions = new ArrayBuffer[Mention]()
    for (m <- mentions) {
      val newArgs = mutable.Map[String, Seq[Mention]]()
      val trigger = if (m.isInstanceOf[EventMention]) {
        m.asInstanceOf[EventMention].trigger.text
      }
      else if (m.isInstanceOf[CrossSentenceEventMention]) {
        m.asInstanceOf[CrossSentenceEventMention].trigger.text
      } else "no Trigger"
      val foundBy = m.foundBy
      val att = new FunctionAttachment("FunctionAtt", trigger, foundBy)
      newMentions.append(m.withAttachment(att))
    }
    newMentions
  }

  def processParamSetting(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    val newMentions = new ArrayBuffer[Mention]()
    for (m <- mentions) {
      val firstTokenOfValue = m.arguments("value").head.tokenInterval.start
      // if value is first token in a sentence, that is probably just the section number in a paper
      if (firstTokenOfValue != 0) {
        // assume there's only one arg of each type
        val tokenIntervals = m.arguments.map(_._2.head).map(_.tokenInterval).toSeq
        val labelsOfTextBoundMentions = m.arguments.map(_._2.head.label).toSeq
        // make sure mention labels are no identical (basically, checking if both are Values---they should not be)
        if (labelsOfTextBoundMentions.distinct.length == labelsOfTextBoundMentions.length) {
          // takes care of accidental arg overlap
          if (tokenIntervals.distinct.length == tokenIntervals.length) {
            val newArgs = mutable.Map[String, Seq[Mention]]()
            val attachedTo = if (m.arguments.exists(arg => looksLikeAnIdentifier(arg._2, state).nonEmpty)) {

              newArgs += ("variable" -> Seq(copyWithLabel(m.arguments("variable").head, "Identifier")), "value" -> m.arguments("value"))
              "variable"
            } else {
              newArgs += ("variable" -> m.arguments("variable"), "value" -> m.arguments("value"))
              "concept"
            }
            val att = new ParamSetAttachment(attachedTo, "ParamSetAtt")
            newMentions.append(copyWithArgs(m, newArgs.toMap).withAttachment(att))
          }
        }
      }
    }
    newMentions
  }

  // make contextualized event mentions into attachments.
  def processRuleBasedContextEvent(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    val contextAttachedMens = new ArrayBuffer[Mention]
    for (m <- mentions) {
      val toAttach = m.arguments.getOrElse("event", Seq.empty)
      val contexts = m.arguments.getOrElse("context", Seq.empty)
      val foundBy = m.foundBy
      if (toAttach.nonEmpty) {
        for (t <- toAttach) {
          contextAttachedMens.append(contextToAttachment(t, contexts, foundBy, state))
        }
      }
    }
    contextAttachedMens
  }

  def contextToAttachment(menToAttach: Mention, contexts: Seq[Mention], foundBy: String, state: State = new State()): Mention = {
    val att = new ContextAttachment("ContextAtt", context = contextsToStrings(contexts, state), foundBy)
    menToAttach.withAttachment(att)
  }

  def contextsToStrings(context: Seq[Mention], state: State = new State()): Seq[String] = {
    val contexts = new ArrayBuffer[String]
    if (context.nonEmpty) {
      for (c <- keepLongest(context)) {
        val contextInformation = c.arguments("context")
        for (i <- contextInformation) {
          contexts.append(i.text)
        }
      }
    }
    contexts
  }

  def keepLongestValue(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    {
      // used to avoid values like 27 000 being split into two separate values
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
  }

  def keepLongestIdentifier(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    // used to avoid identifiers like R ( t ) being found as separate R, t, R(t, and so on
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


  // sentence for debugging Bearing in mind , we set our default setting to the refugee move speed is equal to 200 km per day and the awareness of surrounding is 1 link .
  // todo: somehow link resulting events to definitions, maybe in previous three sent window
  def assembleVarsWithParamsAndUnits(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    val (withVar, noVar) = mentions.partition(_.arguments.keys.toList.contains("variable"))
    val groupedBySent = withVar.groupBy(_.sentence)
    val toReturn = new ArrayBuffer[Mention]()
    for (g <- groupedBySent) {
      val groupedByVar = g._2.groupBy(_.arguments("variable"))
      // event mentions grouped by var (so, checking which ones have an overlapping variable mention)
      for (gv <- groupedByVar) {
        // if there are more than two in a group that are distinct by text, that means we can assemble them into an event
        val mentionsInGroup = gv._2
        if (distinctByText(mentionsInGroup).length > 1) {
          // do not exclude component events (param settings and units) from output
          for (v <- mentionsInGroup) toReturn.append(v)
          val newArgs = mutable.Map[String, Seq[Mention]]()
          for (m <- mentionsInGroup) {
            // it's fine if the var mention is overwritten because they are the same; the other args that matter are not gonna get overwritten
            for (arg <- m.arguments) {
              newArgs(arg._1) = arg._2
            }
          }
          val assembledMention = copyWithFoundBy(copyWithLabel(copyWithArgs(gv._2.head, newArgs.toMap), "ParamAndUnit"), gv._2.head.foundBy + "++assembleVarsWithParamsAndUnits")
          toReturn.append(assembledMention)

        } else {
          // since the mentions in the group are not distinct by text, keep all of them
            for (m <- mentionsInGroup) toReturn.append(m)
        }
      }
    }
    toReturn.filter(_.arguments("variable").length == 1).distinct ++ noVar
  }

  def processCommands(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    val groupBySent = mentions.groupBy(_.sentence)
    val toReturn = new ArrayBuffer[Mention]()
    for (g <- groupBySent) {
      val (commands, other) = g._2.partition(_.label == "CommandSequence")
      for (o <- other) toReturn.append(o)
      val otherGroupedByLabel = other.groupBy(_.label)
      val commandStartSameAsSentStart = commands.filter(m => m.tokenInterval.start == 0)
      for (c <- commandStartSameAsSentStart) {
        val curArgs = c.arguments
        val newArgs = mutable.Map[String, Seq[Mention]]()
        // for every other mention group
        for (og <- otherGroupedByLabel.filter(m => (m._1 == "Filename" || m._1 == "Repository" || m._1 == "CommandLineParamValuePair" || m._1 == "CommLineParameter"))) {
          // there could be multiple mentions that we will want to become command args
          val newMentionArgValues = new ArrayBuffer[Mention]()
          for (o <- og._2) {
            // if the other mention is completely subsumed by command mention, add the other mention to command args
            if (o.tokenInterval.intersect(c.tokenInterval).length == o.tokenInterval.length) {
              newMentionArgValues.append(o)
            }
          }

          def firstCharLower(string: String): String = {
            string.head.toLower + string.tail
          }
          if (newMentionArgValues.nonEmpty) {
            newArgs(firstCharLower(og._1)) = newMentionArgValues.distinct
          }

        }

        val (newTrigger, args) = (curArgs ++ newArgs.toMap).partition(_._1 == "command")
        val trigger = newTrigger.values.flatten.head.asInstanceOf[TextBoundMention]
        toReturn.append(copyWithArgs(c, args).asInstanceOf[RelationMention].toEventMention(trigger))
      }
    }
    toReturn
  }

  def intervalParamSettTakesPrecedence(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    val toReturn = new ArrayBuffer[Mention]()
    val groupedBySent = mentions.groupBy(_.sentence)
    for (sg <- groupedBySent) {
      val (intParamSet, paramSet) = sg._2.partition(_.label == "IntervalParameterSetting")
      for (ps <- paramSet) {
        if (!intParamSet.exists(ips => ips.arguments("variable").head.tokenInterval == ps.arguments("variable").head.tokenInterval)) toReturn.append(ps)
      }
      toReturn.appendAll(intParamSet)
    }
    toReturn
  }

  def locationsAreNotVariablesOrModels(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    // makes sure there are no mentions where variables are actually most likely locations
    // currently not used because NER labels identifiers as LOCATION
    val (locations, nonLocations) = mentions.partition(_.label == "Location")
    // everything that is not a location needs to be checked for potential location-likeness
    // we only want to check mentions that are contentful---not just Phrases, which are basically building blocks for other mentions
    val (phrases, nonPhrases) = nonLocations.partition(_.label == "Phrase")
    val noLocations = new ArrayBuffer[Mention]()
    def isInLocations(sent: Int, tokInt: Interval, locations: Seq[Mention]): Boolean = {
      locations.exists(loc => loc.sentence == sent & loc.tokenInterval == tokInt)
    }

    for (m <- nonPhrases) {
      val args = m.arguments.values.flatten
      m match {
        case m: TextBoundMention => {
          // keep standalone identifiers that look like locations, but add info to the foundBy
          val sent = m.sentence
          val tokInt = m.tokenInterval
          if (isInLocations(sent, tokInt, locations)) {
            noLocations.append(m.asInstanceOf[TextBoundMention].copy(foundBy = m.foundBy + "++possibleLocation"))
          } else noLocations.append(m)

        }
        case _ => {
          var noLoc = true
          for (arg <- args) {
            breakable {
              val sent = arg.sentence
              val tokInt = arg.tokenInterval
              if (noLoc) {
                if (isInLocations(sent, tokInt, locations)) {
                  noLoc = false
                }
              } else break
            }
          }
          if (noLoc) {
            noLocations.append(m)
          }
        }
      }
    }
    val toReturn = (noLocations ++ locations ++ phrases).distinct
    toReturn
  }

  /** Keeps the longest mention for each group of overlapping mentions * */
  // note: edited to allow functions to have overlapping inputs/outputs
  def keepLongest(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    val (functions, nonFunctions) = mentions.partition(m => m.label == "Function" && m.arguments.contains("output") && m.arguments("output").nonEmpty)
    val (modelDescrs, other) = nonFunctions.partition(m => m.label == "ModelDescr")
    // distinguish between EventMention and CrossSentenceMention in modelDescr mentions
    val (modelDescrCm, modelDescrEm) = modelDescrs.partition(_.isInstanceOf[CrossSentenceEventMention])
    // distinguish between EventMention and RelationMention in functionMentions
    val (functionEm, functionRm) = functions.partition(_.isInstanceOf[EventMention])
    val mns: Iterable[Mention] = for {
      // find mentions of the same label and sentence overlap
      (k, v) <- other.groupBy(m => (m.sentence, m.label))
      m <- v
      // for overlapping mentions starting at the same token, keep only the longest
      longest = v.filter(_.tokenInterval.overlaps(m.tokenInterval)).maxBy(m => (m.end - m.start) + 0.1 * m.arguments.size)
    } yield longest
    val ems: Iterable[Mention] = for {
      (k, v) <- functionEm.groupBy(m => (m.sentence, m.asInstanceOf[EventMention].trigger.tokenInterval))
      (a, b) <- v.groupBy(m => m.arguments("output").head.tokenInterval)
      m <- b
      longest = b.filter(_.tokenInterval.overlaps(m.tokenInterval)).maxBy(m => (m.end - m.start) + 0.1 * m.arguments.size)
    } yield longest
    val mcs: Iterable[Mention] = for {
      (k, v) <- modelDescrCm.groupBy(m => (m.sentence, m.asInstanceOf[CrossSentenceEventMention].trigger.tokenInterval))
      m <- v
      longest = v.filter(_.tokenInterval.overlaps(m.tokenInterval)).maxBy(m => (m.end - m.start) + 0.1 * m.arguments.size)
    } yield longest
    val mes: Iterable[Mention] = for {
      (k, v) <- modelDescrEm.groupBy(m => (m.sentence, m.asInstanceOf[EventMention].trigger.tokenInterval))
      m <- v
      longest = v.filter(_.tokenInterval.overlaps(m.tokenInterval)).maxBy(m => (m.end - m.start) + 0.1 * m.arguments.size)
    } yield longest

    mns.toVector.distinct ++ ems.toVector.distinct ++ mcs.toVector.distinct ++ mes.toVector.distinct ++ functionRm
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
        val chosenMen = sg._2.filter(m => m.arguments("variable").length == maxNumOfVars & m.arguments.values.flatten.toList.length == maxNumOfArgs).head
        mns.append(chosenMen)
      }
    }

    val mens = mns.toList
    mens.toVector.distinct
  }

  def filterDescrsByOffsets(mentions: Seq[Mention], filterBy: String, state: State = new State()): Seq[Mention] = {
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

  def groupByVarOverlap(mentions: Seq[Mention]): Map[Interval, Seq[Mention]] = {
    val allVarArgs = mentions.flatMap(_.arguments("variable")).map(_.tokenInterval).distinct
    val grouped = mutable.Map[Interval, Seq[Mention]]()
    for (varMenInt <- allVarArgs) {
      val mentionsWithVar = new ArrayBuffer[Mention]()
      for (m <- mentions) {
        if (m.arguments("variable").map(_.tokenInterval).contains(varMenInt))
          mentionsWithVar.append(m)
      }
      grouped += (varMenInt -> mentionsWithVar.distinct)
    }
    grouped.toMap
  }

  def longestAndWithAtt(mentions: Seq[Mention]): Mention = {
    val maxLength = mentions.maxBy(_.tokenInterval.length).tokenInterval.length
    val (ofMaxLength, other) = mentions.partition(_.tokenInterval.length == maxLength)
    if (ofMaxLength.exists(_.attachments.nonEmpty)) {
      val (withAtt, other) = ofMaxLength.partition(_.attachments.nonEmpty)
      return withAtt.head
    } else {
      ofMaxLength.head
    }

  }

  def filterOutOverlappingDescrMen(mentions: Seq[Mention]): Seq[Mention] = {
    // input is only mentions with the label ConjDescription (types 1 and 2) or Description with conjunctions
    // this is to get rid of conj descriptions that are redundant in the presence of a more complete ConjDescription
    val toReturn = new ArrayBuffer[Mention]()
    val groupedBySent = mentions.groupBy(_.sentence)

    for (sentGroup <- groupedBySent) {
      val groupedByTokenOverlap = groupByTokenOverlap(sentGroup._2)
      for (tokOverlapGroup <- groupedByTokenOverlap.values) {
        // we will only be picking the longest one out of the ones that have a variable (identifier) overlap
        for (varOverlapGroup <- groupByVarOverlap(tokOverlapGroup).values) {
          // if there are ConjDescrs among overlapping decsrs, then pick the longest conjDescr
          if (varOverlapGroup.exists(_.label.contains("ConjDescription"))) {
            // type 2 has same num of vars and descriptions (a minimum of two pairs)
            val (type2, type1) = varOverlapGroup.partition(_.label.contains("Type2"))
            if (type2.isEmpty) {
              // use conf descrs type 1 only if there are no overlapping (more complete) type 2 descriptions
              val longestConjDescr = longestAndWithAtt(varOverlapGroup.filter(_.label == "ConjDescription"))
              toReturn.append(longestConjDescr)
            } else {
              val longestConjDescr = longestAndWithAtt(varOverlapGroup.filter(_.label == "ConjDescriptionType2"))
              toReturn.append(longestConjDescr)
            }
          } else {
            for (men <- varOverlapGroup) toReturn.append(men)
          }
        }
      }
    }
    toReturn.distinct
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
        if (!(prevTokenIndex + 1 == tokenInt)) {
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
    val charOffsetsForAttachment = getDiscontCharOffset(m, newTokenInt)
    if (charOffsetsForAttachment.length > 1) {
      val attachment = new DiscontinuousCharOffsetAttachment(charOffsetsForAttachment, "DiscontinuousCharOffset")
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
    val (conjType2, conjType1) = conjDescrs.partition(_.label.contains("Type2"))

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
            m.attachments
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
          val sortedConjNodes = allConjNodes.sorted
          for (int <- sortedConjNodes) {
            // note: this depends on where the conj is in the mention
            // ex. 1: Sl and Sh are the sunlit and shaded leaf contributions.
            // vs
            // ex. 2: Sl and Sh are the leaf contributions of sunlight and shade

            // if conjoined elements are closer to the right-hand side of the head description (ex. 2), , then the new description starts with the head descr start token (leaf contributions)
            val newDescrStartToken = if (math.abs(sortedConjNodes.head - headDescr.tokenInterval.start) > math.abs(sortedConjNodes.last - headDescr.tokenInterval.last)) {
              headDescr.tokenInterval.start
              // else the new description starts with the current conj start (ex 1)
            } else int
            // the new descr token interval is the longest descr available with words like `both` and `either` removed and ...
            var newDescrTokenInt = if (math.abs(sortedConjNodes.head - headDescr.tokenInterval.start) > math.abs(sortedConjNodes.last - headDescr.tokenInterval.last)) {
              // if conjoined elements are closer to the right-hand side of the head description (ex. 2)
              headDescr.tokenInterval.filter(item => (item >= newDescrStartToken & item <= int) & !preconj.contains(item))
            } else {
              headDescr.tokenInterval.filter(item => (item >= int & item <= headDescr.tokenInterval.last) & !preconj.contains(item))
            }
            //...with intervening conj hops removed, e.g., in `a and b are the blah of c and d, respectively`, for the descr of b, we will want to remove `c and ` - which make up the intervening conj hop
            if (previousIndices.nonEmpty) {
              newDescrTokenInt = newDescrTokenInt.filter(ind => ind < previousIndices.head || ind >= int)
            }

            val wordsWIndex = headDescr.sentenceObj.words.zipWithIndex
            //            val descrText = wordsWIndex.filter(w => newDescrTokenInt.contains(w._2)).map(_._1)
            val newDescr = new TextBoundMention(headDescr.labels, Interval(newDescrTokenInt.head, newDescrTokenInt.last + 1), headDescr.sentence, headDescr.document, headDescr.keep, headDescr.foundBy, headDescr.attachments)
            newDescriptions.append(newDescr)
            // store char offsets for discont descr as attachments
            val charOffsetsForAttachment = getDiscontCharOffset(headDescr, newDescrTokenInt.toList)

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
                  mostComplete.attachments
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
                  mostComplete.attachments
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

  def copyWithFoundBy(mention: Mention, newFoundBy: String): Mention = {
    mention match {
      case tb: TextBoundMention => tb.copy(foundBy = newFoundBy)
      case rm: RelationMention => rm.copy(foundBy = newFoundBy)
      case em: EventMention => em.copy(foundBy = newFoundBy)
      case _ => ???
    }
  }

  def copyWithArgsAndPaths(orig: Mention, newArgs: Map[String, Seq[Mention]], newPaths: Map[String, Map[Mention, SynPath]]): Mention = {
    orig match {
      case tb: TextBoundMention => ???
      case rm: RelationMention => rm.copy(arguments = newArgs, paths = newPaths)
      case em: EventMention => em.copy(arguments = newArgs, paths = newPaths)
      case _ => ???
    }
  }

  def copyWithLabel(m: Mention, lab: String): Mention = {
    val newLabels = taxonomy.hypernymsFor(lab)
    val copy = m match {
      case tb: TextBoundMention => tb.copy(labels = newLabels)
      case rm: RelationMention => rm.copy(labels = newLabels)
      case em: EventMention => em.copy(labels = newLabels)
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

  def modelDescrArguments(mentions: Seq[Mention], state: State): Seq[Mention] = {
    val mentionsDisplayOnlyArgs = for {
      m <- mentions
      arg <- m.arguments.values.flatten
    } yield copyWithLabel(arg, "ModelDescr")

    mentionsDisplayOnlyArgs
  }

  def filterFunction(mentions: Seq[Mention], state: State): Seq[Mention] = {
    // this filter is for filtering out function args with the same token interval (within a single mention)
    val toReturn = new ArrayBuffer[Mention]()
    val (functions, other) = mentions.partition(_.label == "Function")
    for (f <- functions) {
      val newInputs = new ArrayBuffer[Mention]()
      val newOutputs = new ArrayBuffer[Mention]()
      val newTrigger = new ArrayBuffer[Mention]()
      for (argType <- f.arguments) {
        val sameInterval = argType._2.groupBy(_.tokenInterval) // group function args by token intervals
        for (s <- sameInterval) {
          val numOfArgs = s._2.toList.length
          if (argType._1 == "input") {
            if (numOfArgs == 1) {
              newInputs ++= s._2
            } // if there's only one input, return that
            // if there are more than one, pick one that has "Identifier" label if available; otherwise, choose the longest
            else if (numOfArgs >= 2) {
              if (s._2.exists(_.label == "Identifier")) {
                newInputs += s._2.filter(_.label.contains("Identifier")).head
              } else {
                newInputs += s._2.maxBy(_.text.length)
              }
            }
            else logger.error(f"Function missing ${argType._1}")
          } else if (argType._1 == "output") {
            if (numOfArgs == 1) {
              newOutputs ++= s._2
            } // if there's only one output, return that
            // if there are more than one, pick one that has "Identifier" label if available; otherwise, choose the longest
            else if (numOfArgs >= 2) {
              if (s._2.exists(_.label == "Identifier")) {
                newOutputs += s._2.filter(_.label.contains("Identifier")).head
              } else {
                newOutputs += s._2.maxBy(_.text.length)
              }

            }
            else logger.error(f"Function missing ${argType._1}")
          }
          // not sure arg type trigger is possible
          else if (argType._1 == "trigger") {
            newTrigger ++= s._2
          }
          else logger.error(f"Arg type ${argType._1} is not expected in functions")
        }
      }
      val newArgs = Map("input" -> newInputs, "output" -> newOutputs)
      val newFunctions = copyWithArgs(f, newArgs)
      toReturn.append(newFunctions)
    }

    toReturn.filter(_.arguments.nonEmpty) ++ other
  }

  def combineFunction(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    // this function is to combine function fragments with the closest function mention.
    val (functions, other) = mentions.partition(_.label == "Function")
    // distinguish mentions that are complete (have both input and output) vs. function fragments (have either input or output)
    val (complete, fragment) = functions.partition(m => m.arguments.getOrElse("input", Seq.empty).nonEmpty && m.arguments.getOrElse("output", Seq.empty).nonEmpty)
    val toReturn = new ArrayBuffer[Mention]()
    for (f <- fragment) {
      val newInputs = new ArrayBuffer[Mention]()
      val newOutputs = new ArrayBuffer[Mention]()
      val prevSentences = complete.filter(_.sentence < f.sentence)
      if (prevSentences.nonEmpty) {
        val menToAttach = prevSentences.maxBy(_.sentence) // find the closest function mention that are complete
        if (f.arguments.contains("input")) { // if function fragment contains input arg, combine it with the input args of the mention to attach
          newInputs ++= menToAttach.arguments.getOrElse("input", Seq.empty) ++ f.arguments.getOrElse("input", Seq.empty)
        } else newInputs ++= menToAttach.arguments.getOrElse("input", Seq.empty) // if not, just append original input args to newInputs
        if (f.arguments.contains("output")) { // if function fragment contains output arg, combine it with the output args of the mention to attach
          newOutputs ++= menToAttach.arguments.getOrElse("output", Seq.empty) ++ f.arguments.getOrElse("output", Seq.empty)
        } else newOutputs ++= menToAttach.arguments.getOrElse("output", Seq.empty) // if not, just append original output args to newInputs
        val newArgs = Map("input" -> newInputs, "output" -> newOutputs) // make new args with the combined inputs and outputs
        val sentences = new ArrayBuffer[Int]
        sentences.append(f.sentence)
        sentences.append(menToAttach.sentence)
        val newFunctions = new CrossSentenceEventMention( // make new cross sentence event mention with the new args and sentences
          menToAttach.labels,
          menToAttach.tokenInterval, // tokenInterval is only for the first sentence
          menToAttach.asInstanceOf[EventMention].trigger,
          newArgs,
          menToAttach.paths, // path is off
          menToAttach.sentence,
          sentences, // contains two sentences (menToAttach's sentence & function fragment's sentence)
          menToAttach.document,
          menToAttach.keep,
          menToAttach.foundBy,
          menToAttach.attachments
        )
        toReturn.append(newFunctions)
      } else toReturn.append(f)
    }
    toReturn.distinct ++ other ++ complete
  }

  def filterFunctionArgs(mentions: Seq[Mention], state: State): Seq[Mention] = {
    // this filter is for filtering out function mentions with illegal arguments (i.e., units, reflexive pronouns, or verbs are not likely to be legal arguments)
    val toReturn = new ArrayBuffer[Mention]()
    val (functions, other) = mentions.partition(_.label == "Function")
    val (complete, fragment) = functions.partition(m => m.arguments.getOrElse("input", Seq.empty).nonEmpty && m.arguments.getOrElse("output", Seq.empty).nonEmpty)
    for (c <- complete) {
      // if a mention contains both input and output, both of them need to be filtered
      val newInputs = c.arguments("input").filter(m => !m.label.contains("Unit") && !m.text.contains("self") && m.tags.get.head != "VB")
      val newOutputs = c.arguments("output").filter(m => !m.label.contains("Unit") && !m.text.contains("self") && m.tags.get.head != "VB" && m.tags.get.head != "VBN")
      if (newInputs.nonEmpty && newOutputs.nonEmpty) {
        val newArgs = Map("input" -> newInputs, "output" -> newOutputs)
        val newFunctions = copyWithArgs(c, newArgs)
        toReturn.append(newFunctions)
      }
    }
    for (f <- fragment) {
      // if a mention contains either input or output only, whichever the mention has needs to be filtered out
      if (f.arguments.contains("input")) {
        val inputFilter = f.arguments("input").filter(!_.label.contains("Unit") && f.arguments.values.head.head.tags.get.head != "PRP" && !f.tags.get.head.contains("VB"))
        if (inputFilter.nonEmpty) {
          val newInputs = Map("input" -> inputFilter, "output" -> Seq.empty)
          val newInputMens = copyWithArgs(f, newInputs)
          toReturn.append(newInputMens)
        }
      }
      if (f.arguments.contains("output")) {
        val outputFilter = f.arguments("output").filter(!_.label.contains("Unit") && f.tags.get.head != "PRP" && !f.tags.get.head.contains("VB"))
        if (outputFilter.nonEmpty) {
          val newOutputs = Map("input" -> Seq.empty, "output" -> outputFilter)
          val newOutputMens = copyWithArgs(f, newOutputs)
          toReturn.append(newOutputMens)
        }
      }
    }
    toReturn ++ other
  }

  def filterInputOverlaps(mentions: Seq[Mention], state: State): Seq[Mention] = {
    // this is for filtering out overlapping input arguments (identifier vs. phrase) within a single function mention
    // todo: see if this action and filterOutputOverlaps can replace filterFunction in all cases. If they do, get rid of filterFunction action.
    val toReturn = new ArrayBuffer[Mention]()
    for (m <- mentions) {
      val identifierInputs = new ArrayBuffer[Mention]()
      val phraseInputs = new ArrayBuffer[Mention]()
      val newInputs = new ArrayBuffer[Mention]()
      val outputs = new ArrayBuffer[Mention]()

      for (arg <- m.arguments) {
        if (arg._1 == "input") {
          // if the argument is an input, distinguish between identifier inputs and phrase inputs
          if (arg._2.exists(_.label == "Identifier")) {
            identifierInputs ++= arg._2.filter(_.label.contains("Identifier"))
            phraseInputs ++= arg._2.filterNot(_.label.contains("Identifier"))
          } else phraseInputs ++= arg._2
          // if there is an identifier input, check if there's an overlap between the identifier input and other phrase inputs
          if (identifierInputs.nonEmpty) {
            for (i <- identifierInputs) {
              val inputNumCheck = new ArrayBuffer[Mention]
              if (phraseInputs.nonEmpty) {
                for (p <- phraseInputs) {
                  newInputs.append(p)
                  val overlappingInterval = i.tokenInterval.overlaps(p.tokenInterval)
                  // if there's no overlap, append the identifier input to the inputNumCheck
                  if (!overlappingInterval) {
                    inputNumCheck.append(i)
                  }
                }
                // if the number of identifier inputs appended to the inputNumCheck is the same as the number of phrase inputs,
                // it means that there is no overlap, so attach the identifier input to newInputs.
                // if the number is not the same, it means there is an overlap, so don't attach.
                if (inputNumCheck.length == phraseInputs.length) newInputs.append(i)
                // if there's no phrase inputs, just append the identifier inputs to the newInputs.
              } else newInputs.append(i)
            }
            // if there's no identifier inputs, just append the phrase inputs to the newInputs.
          } else newInputs ++= phraseInputs
        } else outputs ++= arg._2
      }
      // make new arguments with newInputs and outputArgs
      val newArgs = Map("input" -> newInputs.distinct, "output" -> outputs)
      val newFunctions = copyWithArgs(m, newArgs)
      toReturn.append(newFunctions)
    }
    toReturn
  }

  def filterOutputOverlaps(mentions: Seq[Mention], state: State): Seq[Mention] = {
    // this is for filtering out function mentions with overlapping output arguments (identifier output vs. phrase output)
    val newMentions = new ArrayBuffer[Mention]
    // group function mentions by sentence, trigger, foundBy
    val groupMens = mentions.groupBy(m => (m.sentence, m.asInstanceOf[EventMention].trigger.tokenInterval, m.foundBy))
    for (group <- groupMens) {
      if (group._2.head.arguments("output").nonEmpty) {
        // distinguish identifier output vs. phrase output
        val (identOutputMen, phraseOutputMen) = group._2.partition(_.arguments("output").head.label.contains("Identifier"))
        if (identOutputMen.nonEmpty) {
          for (i <- identOutputMen) {
            val outputNumCheck = new ArrayBuffer[Mention]
            if (phraseOutputMen.nonEmpty) {
              for (p <- phraseOutputMen) {
                // see if identifier output overlaps with phrase output(s)
                val overlappingInterval = i.arguments("output").head.tokenInterval.overlaps(p.arguments("output").head.tokenInterval)
                if (!overlappingInterval) { // if there's no overlap, append the mention to outputNumCheck
                  outputNumCheck.append(i)
                }
                else Seq.empty
              }
              // if the length of outputNumCheck and the length of phraseOutputMen are the same,
              // it means that the identifier output don't overlap with any phrase output. So append the mention with identifier output to newMentions
              // if the length is different, that means there have been at least one overlap between identifier output and phrase output.
              if (outputNumCheck.length == phraseOutputMen.length) newMentions.append(i) else Seq.empty
            }
          }
        }
        newMentions ++= phraseOutputMen // if there is no identifier output, just append all the mentions with phrase outputs
      } else newMentions ++= group._2 // if there is no output, just append all the mentions to the newMentions
    }
    newMentions
  }

  def filterModelDescrs(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    // this is for filtering out modelDescr mentions with same sentence, same trigger, and same args (modelName, modelDescr)
    val newModelDescr = new ArrayBuffer[Mention]
    val groupBySentence = mentions.groupBy(_.sentence) // group by sentence
    for (s <- groupBySentence) {
      val groupByModelInt = s._2.groupBy(_.arguments("modelName").head.tokenInterval) // group again by model name token interval
      for (m <- groupByModelInt) {
        val groupByTrigInt = m._2.groupBy(_.asInstanceOf[EventMention].trigger.tokenInterval) // group again by trigger token interval
        for (d <- groupByTrigInt) {
         val groupByModelDescr = d._2.groupBy(_.arguments("modelDescr").head.tokenInterval)
          for (g <- groupByModelDescr) {
            newModelDescr.append(g._2.head)
            }
          }
        }
      }
    newModelDescr
  }

  def filterModelNames(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    // this is to filter out unwanted model names. (i.e., anaphors that were not associated with any modelDescrs or "flee" as general verb "flee", not model "Flee"
    // this method has to be applied after all modelDescr extractions are done
    val filter1 = mentions.filterNot(m => m.foundBy == "model_pronouns" || m.foundBy == "the/this_model" || m.foundBy == "our_model")
    val filter2 = filter1.filterNot(m => m.text == "flee") // couldn't get rid of verb "flee" by using VB tag, because real model name "Flee" also got VB tag.
    filter2
  }

  def compoundModelCompletion(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    // this method is for completing model names that were extracted by "model_compound" rule.
    // without this method, the word "model", which is a trigger of the "model_compound" rule, is not captured as a part of the model name.
    // And it sometimes makes the model name look weird (i.e., "standard" can be extracted as a model name, without the word "model")
    val newMentions = new ArrayBuffer[Mention]
    for (m <- mentions) {
      val completion = new TextBoundMention(
        m.labels,
        m.tokenInterval,
        m.sentence,
        m.document,
        m.keep,
        "compoundModelCompletion",
        m.attachments
      )
      newMentions.append(completion)
    }
    newMentions
  }

  def makeNewMensWithContexts(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    // this method is used to attach contexts to function mentions and parameter setting mentions
    // If the token interval of a context overlaps with the token interval of a mention, attach the context to the mention
    val contextTokInt = new ArrayBuffer[Interval]
    val mensSelected = new ArrayBuffer[Mention]
    val contextSelected = new ArrayBuffer[Mention]
    val toReturn = new ArrayBuffer[Mention]
    val (mensToAttach, mensNotToAttach) = mentions.partition(m => m.label == "Function" || m.label.contains("ParameterSetting"))
    // note: attachment to description creates too many false positives - needs to be revised to be applied to description mentions
    val contextMens = mentions.filter(_.label == "Context")
    if (mensToAttach.nonEmpty) {
      for (m <- mensToAttach) {
        val contextSameSntnce = contextMens.filter(c => c.sentence == m.sentence) // find any contexts that are within the same sentence with the mention
        if (contextSameSntnce.nonEmpty) { // if there are, attach their token intervals to contextTokInt
          for (c <- contextSameSntnce) contextTokInt += c.tokenInterval
          if (findOverlappingInterval(m.tokenInterval, contextTokInt.toList) != None) { // if there is an overlap between the context and the mention, attach mention to mensSelected
            mensSelected.append(m)
          } else toReturn.append(m) // if not, append the mention to toReturn
          if (mensSelected.nonEmpty) {
            for (m <- mensSelected) {
              for (c <- contextSameSntnce) {
                if (m.sentence == c.sentence && m.tokenInterval.overlaps(c.tokenInterval)) {
                  contextSelected.append(c) // for each mentions in mensSelected, find contexts to append (within same sentence, token interval overlaps)
                }
              }
              val filteredContext = filterContextSelected(contextSelected, m) // filter unwanted contexts before attaching to the mention
              if (filteredContext.nonEmpty) {
                val newMen = contextToAttachment(m, filteredContext, foundBy = "tokenInterval overlap", state) // attach the context(s) to the mention
                toReturn.append(newMen)
              } else toReturn.append(m) // if all contexts were filtered, just append the original mention to toReturn
            }
          }
        } else toReturn.append(m)
      }
    }
    toReturn.distinct ++ mensNotToAttach
  }

  def filterContextSelected(contexts: Seq[Mention], mention: Mention): Seq[Mention] = {
    // filter contexts that overlaps with the mentions' arguments or triggers
    // also filter out contexts of which token interval is the same with the mention's token interval
    val filteredContext = new ArrayBuffer[Mention]
    val contextNumCheck = new ArrayBuffer[Mention]
    val completeFilterContext = new ArrayBuffer[Mention]
    val trigger = if (mention.isInstanceOf[EventMention]) mention.asInstanceOf[EventMention].trigger.tokenInterval else null
    for (c <- contexts) {
      for (argType <- mention.arguments) {
        for {
          arg <- argType._2
          newMention = mention match {
            case rm: RelationMention => if (!c.tokenInterval.overlaps(arg.tokenInterval)) contextNumCheck.append(c)
            case em: EventMention => if (!c.tokenInterval.overlaps(arg.tokenInterval) && !c.tokenInterval.overlaps(trigger)) contextNumCheck.append(c)
            case _ => ???
          }
        } yield contextNumCheck
        if (contextNumCheck.nonEmpty && contextNumCheck.length == argType._2.length) {
          filteredContext.append(c)
        }
        completeFilterContext ++= filteredContext.filter(c => c.tokenInterval != mention.tokenInterval)
      }
    }
    completeFilterContext.distinct
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
          foundBy = foundBy(rm.foundBy),
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

  def allCaps(string: String): Boolean = {
    // assume it's true, but return false if find evidence to the contrary
    for (ch <- string) {
      if (!ch.isUpper) {
        return false
      }
    }
    true
  }

  def looksLikeAnIdentifier(mentions: Seq[Mention], state: State): Seq[Mention] = {

    // here, can add different characters we want to allow in identifiers; use with caution
    val compoundIdentifierComponents = Seq("(", ")")

    //returns mentions that look like an identifier
    def passesFilters(v: Mention, isArg: Boolean): Boolean = {
      // If the variable/identifier was found with a Gazetteer passed through the webservice, keep it
      if (v == null) return false
      if ((v matches OdinEngine.VARIABLE_GAZETTEER_LABEL) && isArg) return true
      // to allow vars like R(t) and e°(Tmax)---to pass, there have to be at least four chars and the paren can't be the first char
      if (v.words.exists(_ == "and")) return false
      if (v.words.length > 3 && v.words.tail.intersect(compoundIdentifierComponents).nonEmpty) return true
      if (v.words.length < 3 && v.entities.exists(ent => ent.exists(_ == "B-GreekLetter"))) return true
      if (v.entities.get.exists(_ == "B-unit")) return false
      if (allCaps(v.words.mkString("").replace(" ", ""))) return true
      // account for all caps variables, e.g., EORATIO
      if (v.words.length == 1 && allCaps(v.words.head)) return true
      if (v.words.length == 1 && !(v.words.head.count(_.isLetter) > 0)) return false
      if ((v.words.length >= 1) && v.entities.get.exists(m => m matches "B-GreekLetter")) return true //account for identifiers that include a greek letter---those are found as separate words even if there is not space
      if (v.words.length != 1) return false
      if (v.words.head.contains("-") & v.words.head.last.isDigit) return false
      // Else, the identifier candidate has length 1
      val word = v.words.head
      if (word.contains("_")) return true
      if (freqWords.contains(word.toLowerCase())) return false //filter out potential variables that are freq words
      if (word.length > 6) return false
      // an identifier/variable cannot be a unit

      val tag = v.tags.get.head
      if (tag == "POS") return false
      return (
        word.toLowerCase != word // mixed case or all UPPER
          |
          v.entities.exists(ent => ent.contains("B-GreekLetter")) //or is a greek letter
          |
          word.length == 1 && (tag.startsWith("NN") | tag == "FW") //or the word is one character long and is a noun or a foreign word (the second part of the constraint helps avoid standalone one-digit numbers, punct, and the article 'a'
          |
          word.length < 3 && word.exists(_.isDigit) && !word.contains("-") && word.replaceAll("\\d|\\s", "").length > 0 //this is too specific; trying to get to single-letter identifiers with a subscript (e.g., u2) without getting units like m-2
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
        case em: EventMention => (m.arguments.getOrElse("variable", Seq.empty).head, true)
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
        case rm: RelationMention => m.arguments.getOrElse("variable", Seq.empty).head
        case em: EventMention => m.arguments.getOrElse("variable", Seq.empty).head
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

      variableMention = m.arguments.getOrElse("variable", Seq.empty)
      descrMention = m.arguments.getOrElse("description", Seq.empty)
      if descrMention.nonEmpty //there has to be a description
      descrMen = descrMention.head
      if (
        looksLikeADescr(descrMention, state).nonEmpty && //make sure the descr looks like a descr
          descrMen.text.length > 4 && //the descr can't be the length of a var
          !descrMention.head.text.contains("=") &&
          looksLikeAnIdentifier(descrMention, state).isEmpty //makes sure the description is not another variable (or does not look like what could be an identifier)
          &&
          descrMen.tokenInterval.intersect(variableMention.head.tokenInterval).isEmpty //makes sure the variable and the description don't overlap
        ) || (descrMention.nonEmpty && freqWords.contains(descrMen.text)) //the description can be one short, frequent word: fixme: should be looking at lemmas, not head text bc frequent words are (for the most part) not plural
      // make sure there's at least one noun or participle/gerund; there may be more nominal pos that will need to be included - revisit: excluded descr like "Susceptible (S)"
      if descrMen.tags.get.exists(t => (t.startsWith("N") || t == "VBN") || descrMen.words.exists(w => capitalized(w)))
    } yield m
  }

  def compoundIdentifierActionFlow(mentions: Seq[Mention], state: State): Seq[Mention] = {
    val toReturn = looksLikeAnIdentifier(mentions, state)
    toReturn
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

  def functionActionFlow(mentions: Seq[Mention], state: State): Seq[Mention] = {
    val filteredMen = filterFunction(mentions, state)
    val filteredOutputs = if (filteredMen.nonEmpty) filterOutputOverlaps(filteredMen, state) else Seq.empty
    val filteredInputs = if (filteredOutputs.nonEmpty) filterInputOverlaps(filteredOutputs, state) else Seq.empty
    val filteredArgs = if (filteredInputs.nonEmpty) filterFunctionArgs(filteredInputs, state) else Seq.empty
    val toReturn = if (filteredArgs.nonEmpty) processFunctions(filteredArgs, state) else Seq.empty

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
          val unitArgs = m.arguments.getOrElse("unit", Seq.empty)
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
      // fixme: there should be a better way to do this...
      durationUnitPattern = "day|month|year|per|people".r
      //the length constraints: the unit should consist of no more than 5 words and the first word of the unit should be no longer than 3 characters long (heuristics)
      if durationUnitPattern.findFirstIn(unitTextSplit.mkString(" ")).nonEmpty || (((unitTextSplit.length <= 5 && unitTextSplit.head.length <= 3) || pattern.findFirstIn(unitTextSplit.mkString(" ")).nonEmpty) && negPattern.findFirstIn(unitTextSplit.mkString(" ")).isEmpty)
    } yield m
  }

  def looksLikeADescr(mentions: Seq[Mention], state: State): Seq[Mention] = {
    val valid = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ "
    val singleCapitalWord = """^[A-Z]+$""".r
    for {
      m <- mentions
      descrText = m match {
        case tb: TextBoundMention => tb
        case rm: RelationMention => rm.arguments.getOrElse("description", Seq()).head
        case em: EventMention => em.arguments.getOrElse("description", Seq()).head
        case _ => ???
      }

      if descrText.text.filter(c => valid contains c).length.toFloat / descrText.text.length > 0.75
      if (descrText.words.exists(_.length > 1))
      if singleCapitalWord.findFirstIn(descrText.text).isEmpty
      if !descrText.text.startsWith(")")

    } yield m
  }

  def capitalized(string: String): Boolean = {
    string.head.isUpper && !allCaps(string.tail)
  }

  def changeLabel(orig: Mention, label: String): Mention = {
    orig match {
      case tb: TextBoundMention => tb.copy(labels = taxonomy.hypernymsFor(label))
      case rm: RelationMention => rm.copy(labels = taxonomy.hypernymsFor(label))
      case em: EventMention => em.copy(labels = taxonomy.hypernymsFor(label))
    }
  }

  def relabelLocation(mentions: Seq[Mention], state: State): Seq[Mention] = {
    val (locationMentions, other) = mentions.partition(_.label matches "Location")
    val onlyNewLocation = locationMentions.map(m => copyWithLabel(m.arguments("loc").head, "Location").asInstanceOf[TextBoundMention].copy(foundBy = m.foundBy + "++relabelLocation"))
    onlyNewLocation ++ other
  }


  def paramSettingVarToModelParam(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    // this is for creating Parameter mentions from variable args in paramSetting mentions
    val paramSettingMens = mentions.filter(m => m.labels.contains("ParameterSetting"))
    val modelParams = new ArrayBuffer[Mention]
    for (p <- paramSettingMens) {
      val paramSettingVars = p.arguments.filter(m => m._1 == "variable")
      for (vars <- paramSettingVars.values) {
        val variable = vars.head
        val newLabels = List("Parameter", "Model", "Phrase", "Entity").toSeq

        val modelParam = new TextBoundMention(
          newLabels,
          variable.tokenInterval,
          variable.sentence,
          variable.document,
          variable.keep,
          "paramSettingVarToModelParam",
          variable.attachments)
        modelParams.append(modelParam)
      }
    }
    modelParams
  }

  def functionArgsToModelParam(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    // this is for creating Parameter mentions from Function arguments (inputs, outputs)
    val functionMens = mentions.filter(_.label == "Function")
    val modelParams = new ArrayBuffer[Mention]
    for (f <- functionMens) {
      for (args <- f.arguments.values) {
        val newLabels = List("Parameter", "Model", "Phrase", "Entity").toSeq
        for (arg <- args) {
          val modelParam = new TextBoundMention(
            newLabels,
            arg.tokenInterval,
            arg.sentence,
            arg.document,
            arg.keep,
            "functionArgsToModelParam",
            arg.attachments)
          modelParams.append(modelParam)
        }
      }
    }
    modelParams
  }

  def filterModelParam(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    // this method is for filtering out illegal parameters
    val filter1 = mentions.filterNot(m => m.text.length > 40 && !m.text.contains("_")) // Note: Too long args are unlikely to be a model parameter. length can be adjusted later.
    val filter2 = filter1.filterNot(m => m.tags.head.contains("CD") || m.tags.head.contains("PRP")) // Note: arg with a numeric value is unlikely to be a model parameter.
    val filter3 = filter2.filterNot(m => m.entities.head.contains("LOCATION")) // Note: arg with LOCATION entity is unlikely to be a model parameter.
    val filter4 = filter3.filterNot(m => m.text.contains("data"))
    // more filters can be added here
    filter4
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
