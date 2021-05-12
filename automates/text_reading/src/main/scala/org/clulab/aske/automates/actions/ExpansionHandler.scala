package org.clulab.aske.automates.actions

// ported from eidos

import com.typesafe.scalalogging.LazyLogging
import org.clulab.aske.automates.entities.{EntityConstraints, EntityHelper}
import org.clulab.odin._
import org.clulab.processors.Sentence
import org.clulab.struct.Interval
import org.clulab.aske.automates.actions.ExpansionHandler._
import org.clulab.utils.DisplayUtils

import scala.annotation.tailrec
import scala.collection.mutable.ArrayBuffer

// todo: currently the language doesn't do anything special, but in the future will allow the handler to do
// things diff for diff languages
class ExpansionHandler() extends LazyLogging {

  def expandArguments(mentions: Seq[Mention], state: State, validArgs: List[String]): Seq[Mention] = {
    // Yields not only the mention with newly expanded arguments, but also yields the expanded argument mentions
    // themselves so that they can be added to the state (which happens when the Seq[Mentions] is returned at the
    // end of the action
    // TODO: alternate method if too long or too many weird characters ([\w.] is normal, else not)
    val res = mentions.flatMap(expandArgs(_, state, validArgs))

    // Useful for debug
    res
  }

  def expandArgs(mention: Mention, state: State, validArgs: List[String]): Seq[Mention] = {
    val valid = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "
    val sentLength: Double = mention.sentenceObj.getSentenceText.length
    val normalChars: Double = mention.sentenceObj.getSentenceText.filter(c => valid contains c).length
    val proportion = normalChars / sentLength
    val threshold = 0.8 // fixme: tune
//    println(s"$proportion --> ${mention.sentenceObj.getSentenceText}")
    if (proportion > threshold) {
      expandArgsWithSyntax(mention, state, validArgs)
    } else {
      expandArgsWithSurface(mention, state, validArgs)
    }
  }

  // fixme: not expanding!
  def expandArgsWithSurface(m: Mention, state: State, validArgs: List[String]): Seq[Mention] = {
    Seq(m)
  }

  def expandArgsWithSyntax(m: Mention, state: State, validArgs: List[String]): Seq[Mention] = {
    // Helper method to figure out which mentions are the closest to the trigger
    def distToTrigger(trigger: Option[TextBoundMention], m: Mention): Int = {
      if (trigger.isDefined) {
        // get the trigger
        val t = trigger.get
        if (m.start < t.start) {
          // mention to the left of the trigger
          math.abs(t.start - m.end)
        } else if (m.start > t.end) {
          // mention to the right of the trigger
          math.abs(m.start - t.end)
        } else {
          logger.debug(s"distToTrigger: Unexpected overlap of trigger and argument: \n\t" +
            s"sent: [${m.sentenceObj.getSentenceText}]\n\tRULE: " +
            s"${m.foundBy}\n\ttrigger: ${t.text}\torig: [${m.text}]\n")
          m.start
        }
      } else {
        m.start
      }
    }
    // Get the trigger of the mention, if there is one
    val trigger = m match {
      case rm: RelationMention => None
      case em: EventMention => Some(em.trigger)
      case _ => throw new RuntimeException("Trying to get the trigger from a mention with no trigger")
    }
    var stateToAvoid = if (trigger.nonEmpty) State(Seq(trigger.get)) else new State()

    // Make the new arguments
    val newArgs = scala.collection.mutable.HashMap[String, Seq[Mention]]()
    for ((argType, argMentions) <- m.arguments) {
      if (validArgs.contains(argType)) {
        // Sort, because we want to expand the closest first so they don't get subsumed
        val sortedClosestFirst = argMentions.sortBy(distToTrigger(trigger, _))
        val expandedArgs = new ArrayBuffer[Mention]
        // Expand each one, updating the state as we go
        for (argToExpand <- sortedClosestFirst) {
//          println("arg to expand: " + argToExpand.text + " " + argToExpand.foundBy + " " + argToExpand.labels)
          val expanded = expandIfNotAvoid(argToExpand, ExpansionHandler.MAX_HOPS_EXPANDING, stateToAvoid, m)
//          println("expanded arg: " + expanded.text + " " + expanded.foundBy + " " + expanded.labels)
          expandedArgs.append(expanded)
          // Add the mention to the ones to avoid so we don't suck it up
          stateToAvoid = stateToAvoid.updated(Seq(expanded))
        }
        // Handle attachments
        // todo: here we aren't really using attachments, but we can add them back in as needed
        val attached = expandedArgs
          //.map(addSubsumedAttachments(_, state))
          //.map(attachDCT(_, state))
          //.map(addOverlappingAttachmentsTextBounds(_, state))
          .map(EntityHelper.trimEntityEdges)
        // Store
        newArgs.put(argType, attached)
      } else {
        newArgs.put(argType, argMentions)
      }

    }
    // Return the event with the expanded args as well as the arg mentions themselves
    Seq(copyWithNewArgs(m, newArgs.toMap)) ++ newArgs.values.toSeq.flatten
  }



  /*
      Entity Expansion Helper Methods
   */

  // Do the expansion, but if the expansion causes you to suck up something we wanted to avoid, split at the
  // avoided thing and keep the half containing the original (pre-expansion) entity.
  // todo: Currently we are only expanding TextBound Mentions, if another type is passed we return it un-expanded
  // we should perhaps revisit this
  def expandIfNotAvoid(orig: Mention, maxHops: Int, stateToAvoid: State, m: Mention): Mention = {

//    println("ORIGINAL: " + orig.text + " " + orig.labels + " " + orig.foundBy)
    val expanded = orig match {
      case tbm: TextBoundMention => expand(orig, maxHops = ExpansionHandler.MAX_HOPS_EXPANDING, maxHopLength = ExpansionHandler.MAX_HOP_LENGTH, stateToAvoid)
      case _ => orig
    }

//    println("EXPANDED: " + expanded.text + " " + expanded.labels + " " + expanded.foundBy)
    //println(s"orig: ${orig.text}\texpanded: ${expanded.text}")

    // split expanded at trigger (only thing in state to avoid)
    val triggerOption = stateToAvoid.mentionsFor(orig.sentence).headOption
    triggerOption match {
      case None => expanded
      case Some(trigger) =>
        // keep the half that is on the same side as original Mention
        if (trigger.tokenInterval overlaps expanded.tokenInterval) {
          if (orig.tokenInterval.end <= trigger.tokenInterval.start) {
            // orig is to the left of trigger
            replaceMentionsInterval(expanded, Interval(expanded.start, trigger.start))
          } else if (orig.tokenInterval.start >= trigger.tokenInterval.end) {
            // orig is to the right of trigger
            replaceMentionsInterval(expanded, Interval(trigger.end, expanded.end))
          } else {
            //throw new RuntimeException("original mention overlaps trigger")
            // This shouldn't happen, but Odin seems to handle this situation gracefully (by not extracting anything),
            // I guess here we'll do the same (i.e., not throw an exception)
            logger.debug(s"ExpandIfNotAvoid: Unexpected overlap of trigger and argument: \n\t" +
              s"sent: [${orig.sentenceObj.getSentenceText}]\n\tRULE: " +
              s"${trigger.foundBy}\n\ttrigger: ${trigger.text}\torig: [${orig.text}]\n")
            logger.debug(s"Trigger sent: [${trigger.sentenceObj.getSentenceText}]")
            logger.debug(DisplayUtils.mentionToDisplayString(m))

            stateToAvoid.allMentions.foreach(DisplayUtils.displayMention)
            orig
          }
        } else {
          expanded
        }
    }

  }

  private def replaceMentionsInterval(m: Mention, i: Interval): Mention = m match {
    case m: TextBoundMention => m.copy(tokenInterval = i)
    case _ => sys.error("M is not a textboundmention, I don't know what to do")
  }

  //-- Entity expansion methods (brought in from EntityFinder)
  def expand(entity: Mention, maxHops: Int, maxHopLength: Int, stateFromAvoid: State): Mention = {
    // Expand the incoming to recapture any triggers which were avoided
    val interval1 = traverseIncomingLocal(entity, maxHops, maxHopLength, stateFromAvoid, entity.sentenceObj)
    val incomingExpanded = entity.asInstanceOf[TextBoundMention].copy(tokenInterval = interval1)
    // Expand on outgoing deps
    val interval2 = traverseOutgoingLocal(incomingExpanded, maxHops, maxHopLength, stateFromAvoid, entity.sentenceObj)

    val outgoingExpanded = incomingExpanded.asInstanceOf[TextBoundMention].copy(tokenInterval = interval2)
//    println("\noriginal:  " + entity.text + " " + entity.labels.mkString("") + " " + entity.foundBy)
//    println("expanded:  " + incomingExpanded.text + " " + incomingExpanded.labels.mkString("") ++ incomingExpanded.foundBy)

    outgoingExpanded
  }

  /** Used by expand to selectively traverse the provided syntactic dependency graph **/
  @tailrec
  private def traverseOutgoingLocal(
                                     tokens: Set[Int],
                                     newTokens: Set[Int],
                                     outgoingRelations: Array[Array[(Int, String)]],
                                     incomingRelations: Array[Array[(Int, String)]],
                                     remainingHops: Int,
                                     maxHopLength: Int,
                                     sent: Int,
                                     state: State,
                                     sentence: Sentence

                                   ): Interval = {
    if (remainingHops == 0) {
      val allTokens = tokens ++ newTokens
      Interval(allTokens.min, allTokens.max + 1)
    } else {
      val newNewTokens = for{
        tok <- newTokens
        if outgoingRelations.nonEmpty && tok < outgoingRelations.length
        (nextTok, dep) <- outgoingRelations(tok)
        if isValidOutgoingDependency(dep, sentence.words(nextTok), remainingHops)
        if math.abs(tok - nextTok) < maxHopLength //limit the possible length of hops (in tokens)---helps with bad parses
        if state.mentionsFor(sent, nextTok).isEmpty
        if hasValidIncomingDependencies(nextTok, incomingRelations)
        // avoid expanding if there is a stray opening paren
        if !sentence.words.slice(tok, nextTok).contains(")")
      } yield nextTok
      traverseOutgoingLocal(tokens ++ newTokens, newNewTokens, outgoingRelations, incomingRelations, remainingHops - 1, maxHopLength, sent, state, sentence)
    }
  }
  private def traverseOutgoingLocal(m: Mention, numHops: Int, maxHopLength: Int, stateFromAvoid: State, sentence: Sentence): Interval = {
    val outgoing = outgoingEdges(m.sentenceObj)
    val incoming = incomingEdges(m.sentenceObj)
    traverseOutgoingLocal(Set.empty, m.tokenInterval.toSet, outgoingRelations = outgoing, incomingRelations = incoming, numHops, maxHopLength, m.sentence, stateFromAvoid, sentence)
  }

  /** Used by expand to selectively traverse the provided syntactic dependency graph **/
  @tailrec
  private def traverseIncomingLocal(
                                     tokens: Set[Int],
                                     newTokens: Set[Int],
                                     incomingRelations: Array[Array[(Int, String)]],
                                     remainingHops: Int,
                                     maxHopLength: Int,
                                     sent: Int,
                                     state: State,
                                     sentence: Sentence,
                                     deps: Set[String]

                                   ): Interval = {
    if (remainingHops == 0 || deps.contains("acl:relcl")) { //stop expanding if the previous expansion was on rel clause - expands too much otherwise
      val allTokens = tokens ++ newTokens
      Interval(allTokens.min, allTokens.max + 1)
    } else {
      val yielded = for{
        tok <- newTokens
        if incomingRelations.nonEmpty && tok < incomingRelations.length
        (nextTok, dep) <- incomingRelations(tok)
        if isValidIncomingDependency(dep)
        if math.abs(tok - nextTok) < maxHopLength //limit the possible length of hops (in tokens)---helps with bad parses
        if state.mentionsFor(sent, nextTok).isEmpty
      } yield (nextTok, dep)
      val newNewTokens = yielded.map(_._1)
      val deps = yielded.map(_._2)
      traverseIncomingLocal(tokens ++ newTokens, newNewTokens, incomingRelations, remainingHops - 1, maxHopLength, sent, state, sentence, deps)
    }
  }
  private def traverseIncomingLocal(m: Mention, numHops: Int, maxHopLength: Int, stateFromAvoid: State, sentence: Sentence): Interval = {
    val incoming = incomingEdges(m.sentenceObj)
    traverseIncomingLocal(Set.empty, m.tokenInterval.toSet, incomingRelations = incoming, numHops, maxHopLength, m.sentence, stateFromAvoid, sentence, Set.empty)
  }

  def outgoingEdges(s: Sentence): Array[Array[(Int, String)]] = s.universalEnhancedDependencies match {
    case None => sys.error("sentence has no dependencies")
    case Some(dependencies) => dependencies.outgoingEdges
  }

  def incomingEdges(s: Sentence): Array[Array[(Int, String)]] = s.universalEnhancedDependencies match {
    case None => sys.error("sentence has no dependencies")
    case Some(dependencies) => dependencies.incomingEdges
  }

  /** Ensure dependency may be safely traversed */
  def isValidOutgoingDependency(dep: String, token: String, remainingHops: Int): Boolean = {
    (
      VALID_OUTGOING.exists(pattern => pattern.findFirstIn(dep).nonEmpty) &&
        ! INVALID_OUTGOING.exists(pattern => pattern.findFirstIn(dep).nonEmpty)
      ) // || (
//      // Allow exception to close parens, etc.
//      dep == "punct" && Seq(")", "]", "}", "-RRB-").contains(token)
//      )
  }

  /** Ensure incoming dependency may be safely traversed */
  def isValidIncomingDependency(dep: String): Boolean = {
    VALID_INCOMING.exists(pattern => pattern.findFirstIn(dep).nonEmpty)
  }

  def notInvalidConjunction(dep: String, hopsRemaining: Int): Boolean = {
    // If it's not a coordination/conjunction, don't worry
    if (EntityConstraints.COORD_DEPS.exists(pattern => pattern.findFirstIn(dep).isEmpty)) {
      return true
    } else if (hopsRemaining < ExpansionHandler.MAX_HOPS_EXPANDING) {
      // if it has a coordination/conjunction, check to make sure not at the top level (i.e. we've traversed
      // something already
      return true
    }

    false
  }

  /** Ensure current token does not have any incoming dependencies that are invalid **/
  def hasValidIncomingDependencies(tokenIdx: Int, incomingDependencies: Array[Array[(Int, String)]]): Boolean = {
    if (incomingDependencies.nonEmpty && tokenIdx < incomingDependencies.length) {
      incomingDependencies(tokenIdx).forall(pair => ! INVALID_INCOMING.exists(pattern => pattern.findFirstIn(pair._2).nonEmpty))
    } else true
  }

  // Return a copy of the orig EventMention, but with the expanded arguments
  // The changes made to the mention are the args, the token interval, foundby, and the paths.
  def copyWithNewArgs(orig: Mention, expandedArgs: Map[String, Seq[Mention]], foundByAffix: Option[String] = None, mkNewInterval: Boolean = true): Mention = {
    // Helper method to get a token interval for the new event mention with expanded args
    def getNewTokenInterval(intervals: Seq[Interval]): Interval = Interval(intervals.minBy(_.start).start, intervals.maxBy(_.end).end)

    val newTokenInterval = if (mkNewInterval) {
      // All involved token intervals, both for the original event and the expanded arguments
      val allIntervals = Seq(orig.tokenInterval) ++ expandedArgs.values.flatten.map(arg => arg.tokenInterval)
      // Find the largest span from these intervals
      getNewTokenInterval(allIntervals)
    }
    else orig.tokenInterval

    val paths = for {
      (argName, argPathsMap) <- orig.paths
      origPath = argPathsMap(orig.arguments(argName).head)
    } yield (argName, Map(expandedArgs(argName).head -> origPath))

    // Make the copy based on the type of the Mention
    val copyFoundBy = if (foundByAffix.nonEmpty) s"${orig.foundBy}_$foundByAffix" else orig.foundBy

    orig match {
      case tb: TextBoundMention => throw new RuntimeException("Textbound mentions are incompatible with argument expansion")
      case rm: RelationMention => rm.copy(arguments = expandedArgs, tokenInterval = newTokenInterval, foundBy = copyFoundBy)
      case em: EventMention => em.copy(arguments = expandedArgs, tokenInterval = newTokenInterval, foundBy = copyFoundBy, paths = paths)
    }
  }


  /*
      Attachments helper methods
   */

  // During expansion, sometimes there are attachments that got sucked up, here we add them to the expanded argument mention
//  def addSubsumedAttachments(expanded: Mention, state: State): Mention = {
//    def addAttachments(mention: Mention, attachments: Seq[Attachment], foundByName: String): Mention = {
//      val out = MentionUtils.withMoreAttachments(mention, attachments)
//
//      out match {
//        case tb: TextBoundMention => tb.copy(foundBy=foundByName)
//        case rm: RelationMention => rm.copy(foundBy=foundByName)
//        case em: EventMention => em.copy(foundBy=foundByName)
//      }
//    }
//
//    def compositionalFoundBy(ms: Seq[Mention]): String = {
//      ms.map(_.foundBy).flatMap(ruleName => ruleName.split("\\+\\+")).distinct.mkString("++")
//    }
//
//    // find mentions of the same label and sentence overlap
//    val overlapping = state.mentionsFor(expanded.sentence, expanded.tokenInterval)
//    //    println("Overlapping:")
//    //    overlapping.foreach(ov => println("  " + ov.text + ", " + ov.foundBy))
//    val completeFoundBy = compositionalFoundBy(overlapping)
//
//    val allAttachments = overlapping.flatMap(m => m.attachments).distinct
//    //    println(s"allAttachments: ${allAttachments.mkString(", ")}")
//    // Add on all attachments
//    addAttachments(expanded, allAttachments, completeFoundBy)
//  }
//
//  // Add the document creation time (dct) attachment if there is no temporal attachment
//  // i.e., a backoff
//  def attachDCT(m: Mention, state: State): Mention = {
//    val dct = m.document.asInstanceOf[EidosDocument].dct
//    if (dct.isDefined && m.attachments.filter(_.isInstanceOf[Time]).isEmpty)
//      m.withAttachment(DCTime(dct.get))
//    else
//      m
//  }
//
//  def addOverlappingAttachmentsTextBounds(m: Mention, state: State): Mention = {
//    m match {
//      case tb: TextBoundMention =>
//        val attachments = getOverlappingAttachments(tb, state)
//        if (attachments.nonEmpty) tb.copy(attachments = tb.attachments ++ attachments) else tb
//      case _ => m
//    }
//  }
//
//
//  def getOverlappingAttachments(m: Mention, state: State): Set[Attachment] = {
//    val interval = m.tokenInterval
//    // TODO: Currently this is only Property attachments, but we can do more too
//    val overlappingProps = state.mentionsFor(m.sentence, interval, label = "Property")
//    overlappingProps.map(pm => Property(pm.text, None)).toSet
//  }



}

object ExpansionHandler {
  val MAX_HOPS_EXPANDING = 5
  val MAX_HOP_LENGTH = 16 //max length of hop (in tokens); helps with bad parses
  val AVOID_LABEL = "Avoid-Strict"

  // avoid expanding along these dependencies
  val INVALID_OUTGOING = Set[scala.util.matching.Regex](
    //    "^nmod_including$".r,
    "acl:relcl".r,
    "acl_until".r,
    "advcl_to".r,
    "^advcl_because".r,
    "advmod".r,
    //"amod".r,
    "^case".r,
    "^cc$".r,
    "ccomp".r,
    "compound".r, //note: needed because of description test t1h
    "^conj".r,
    "cop".r,
    "dep".r, //todo: expansion on dep is freq too broad; check which tests fail if dep is included as invalid outgoing,
    "nmod_at".r,
    "^nmod_as".r,
    "^nmod_because".r,
    "^nmod_due_to".r,
    "^nmod_except".r,
    "^nmod_given".r,
    "^nmod_since".r,
    "^nmod_without$".r,
    "nummod".r,
    "^nsubj".r,
    "^punct".r,
    "^ref$".r,
    "appos".r
    //"nmod_for".r,
//    "nmod".r
  )

  val INVALID_INCOMING = Set[scala.util.matching.Regex](
    //"^nmod_with$".r,
    //    "^nmod_without$".r,
    //    "^nmod_except$".r
    //    "^nmod_despite$".r
  )

  // regexes describing valid outgoing dependencies
  val VALID_OUTGOING = Set[scala.util.matching.Regex](
    //    "^amod$".r, "^advmod$".r,
    //    "^dobj$".r,
    //    "^compound".r, // replaces nn
    //    "^name".r, // this is equivalent to compound when NPs are tagged as named entities, otherwise unpopulated
    //    // ex.  "isotonic fluids may reduce the risk" -> "isotonic fluids may reduce the risk associated with X.
    //    "^acl_to".r, // replaces vmod
    //    "xcomp".r, // replaces vmod
    //    // Changed from processors......
//        "^nmod_at".r, // replaces prep_
    //    //    "case".r
    //    "^ccomp".r
    ".+".r
  )

  val VALID_INCOMING = Set[scala.util.matching.Regex](
    "acl:relcl".r,
    "^nmod_for".r,
//    "amod".r,
//    "^compound$".r//,
    "nmod_at".r,
    "^nmod_of".r,
    "nmod_under".r,
    "nmod_in".r//,
//    "dobj".r
  )

  def apply() = new ExpansionHandler()
}
