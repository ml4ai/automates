package org.clulab.aske.automates.entities

import com.typesafe.config.Config
import com.typesafe.scalalogging.LazyLogging
import org.clulab.odin.{ExtractorEngine, Mention, State, TextBoundMention}
import org.clulab.processors.{Document, Sentence}
import org.clulab.struct.Interval
import org.clulab.utils.FileUtils
import ai.lum.common.ConfigUtils._


import scala.annotation.tailrec

// This file was copied from processors.  scaladoc comments in eidos cannot refer
// directly to [[org.clulab.processors.Document]] without causing an error during
// the release processes.  The links have therefore been removed.

/**
  * Finds Open IE-style entities from an org.clulab.processors.Document.
  *
  * @param entityEngine an ExtractorEngine for entities.  Runs AFTER avoidEngine.
  * @param avoidEngine an ExtractorEngine for tokens/spans to be avoided. Runs BEFORE entityEngine.
  * @param maxHops the maximum number of dependencies relations to follow during expansion.
  * @param maxLength the maximum allowed length of an entity in tokens.
  */
class RuleBasedEntityFinder(
  val entityEngine: ExtractorEngine,
  val avoidEngine: ExtractorEngine,
  val maxHops: Int,
  val maxLength: Int = RuleBasedEntityFinder.DEFAULT_MAX_LENGTH
) extends EntityFinder with LazyLogging {

  // avoid expanding along these dependencies
  val INVALID_OUTGOING = Set[scala.util.matching.Regex](
    "^nmod_including$".r,
    "^nmod_without$".r,
    "^nmod_except".r,
    "^nmod_since".r,
    "^nmod_among".r
  )

  val INVALID_INCOMING = Set[scala.util.matching.Regex](
    //"^nmod_with$".r,
    "^nmod_without$".r,
    "^nmod_except$".r,
    "^nmod_despite$".r
  )

  // regexes describing valid outgoing dependencies
  val VALID_OUTGOING = Set[scala.util.matching.Regex](
    "^amod$".r, //"^advmod$".r,
    "^dobj$".r,
    "^compound".r, // replaces nn
    "^name".r, // this is equivalent to compound when NPs are tagged as named entities, otherwise unpopulated
    // ex.  "isotonic fluids may reduce the risk" -> "isotonic fluids may reduce the risk associated with X.
    "^acl_to".r, // replaces vmod
    "xcomp".r, // replaces vmod
    // Changed from processors......
    "^nmod".r, // replaces prep_
    //    "case".r
    "^ccomp".r
  )

  /**
    * Performs rule-based entity extraction with selective expansion along syntactic dependencies.
    * For filtering, see filterEntities.
    * @param doc an org.clulab.processors.Document
    */
  def extract(doc: Document): Seq[Mention] = {
    // avoid refs, etc.
    val avoid = avoidEngine.extractFrom(doc)
    val stateFromAvoid = State(avoid)
    val baseEntities = entityEngine.extractFrom(doc, stateFromAvoid).filter{ entity => ! stateFromAvoid.contains(entity) }
    //val expandedEntities: Seq[Mention] = baseEntities.map(entity => expand(entity, maxHops))
    // split entities on likely coordinations
    //val splitEntities = (baseEntities ++ expandedEntities).flatMap(EntityHelper.splitCoordinatedEntities)
    // remove entity duplicates introduced by splitting expanded
    val distinctEntities = baseEntities.distinct
    val trimmedEntities = distinctEntities.map(EntityHelper.trimEntityEdges)
    // if there are no avoid mentions, no need to filter
    val res = if (avoid.isEmpty) {
      trimmedEntities
    } else {
      // check that our expanded entities haven't swallowed any avoid mentions
      val avoidLabel = avoid.head.labels.last
      trimmedEntities.filter{ m => stateFromAvoid.mentionsFor(m.sentence, m.tokenInterval, avoidLabel).isEmpty }
    }
//        println(s"AVOID  -- \n\t${avoid.map(m => m.text + "__" + m.foundBy).mkString("\n\t")}")
//        println(s"Base-entities  -- \n\t${baseEntities.map(m => m.text).mkString("\n\t")}")
//        println(s"distinct-Entities -- \n\t${distinctEntities.map(m => m.text).mkString("\n\t")}")
//        println(s"Entities finally returned -- \n\t${res.map(m => m.text).mkString("\n\t")}")
    res
  }

  def extractAndFilter(doc: Document): Seq[Mention] = {
    val entities = extract(doc)
    filterEntities(entities)
  }

  /** Extracts entities without expanding or applying validation filters **/
  def extractBaseEntities(doc: Document): Seq[Mention] = {
    // avoid refs, etc.
    val avoid = avoidEngine.extractFrom(doc)
    val entities = entityEngine.extractFrom(doc, State(avoid))
    entities.filter(entity => ! avoid.contains(entity))
  }

  /**
    * Selects longest mentions among groups of overlapping entities
    * before applying a series of filtering constraints
    * Filter criteria: PoS tag validation of final token, bracket matching, and max length
    * @param entities entities to filter
    */
  private def filterEntities(entities: Seq[Mention]): Seq[Mention] = {
    // ignore citations and remove any entity that is too long given our criteria
    val filteredEntities = entities.filter(m => EntityConstraints.withinMaxLength(m, maxLength))
    val longest = RuleBasedEntityFinder.keepLongest(filteredEntities, new State())
    for {
      m <- filteredEntities
      if EntityConstraints.validFinalTag(m)
      if EntityConstraints.matchingBrackets(m)
    } yield m
  }


  /**
    * Expands an entity up to the specified number of hops along valid grammatical relations.
    */
  def expand(entity: Mention, maxHops: Int): Mention = {
    val interval = traverseOutgoing(entity, maxHops)
    new TextBoundMention(entity.labels, interval, entity.sentence, entity.document, entity.keep, entity.foundBy)
  }

  /** Used by expand to selectively traverse the provided syntactic dependency graph **/
  @tailrec
  private def traverseOutgoing(
    tokens: Set[Int],
    newTokens: Set[Int],
    outgoingRelations: Array[Array[(Int, String)]],
    incomingRelations: Array[Array[(Int, String)]],
    remainingHops: Int
  ): Interval = {
    if (remainingHops == 0) {
      val allTokens = tokens ++ newTokens
      Interval(allTokens.min, allTokens.max + 1)
    } else {
      val newNewTokens = for {
        tok <- newTokens
        if outgoingRelations.nonEmpty && tok < outgoingRelations.length
        (nextTok, dep) <- outgoingRelations(tok)
        if isValidOutgoingDependency(dep)
        if hasValidIncomingDependencies(nextTok, incomingRelations)
      } yield nextTok
      traverseOutgoing(tokens ++ newTokens, newNewTokens, outgoingRelations, incomingRelations, remainingHops - 1)
    }
  }
  private def traverseOutgoing(m: Mention, numHops: Int): Interval = {
    val outgoing = outgoingEdges(m.sentenceObj)
    val incoming = incomingEdges(m.sentenceObj)
    traverseOutgoing(Set.empty, m.tokenInterval.toSet, outgoingRelations = outgoing, incomingRelations = incoming, numHops)
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
  def isValidOutgoingDependency(dep: String): Boolean = {
    VALID_OUTGOING.exists(pattern => pattern.findFirstIn(dep).nonEmpty) &&
      ! INVALID_OUTGOING.exists(pattern => pattern.findFirstIn(dep).nonEmpty)
  }

  /** Ensure current token does not have any incoming dependencies that are invalid **/
  def hasValidIncomingDependencies(tokenIdx: Int, incomingDependencies: Array[Array[(Int, String)]]): Boolean = {
    if (incomingDependencies.nonEmpty && tokenIdx < incomingDependencies.length) {
      incomingDependencies(tokenIdx).forall(pair => ! INVALID_INCOMING.exists(pattern => pattern.findFirstIn(pair._2).nonEmpty))
    } else true
  }
}

object RuleBasedEntityFinder extends LazyLogging {

  def fromConfig(config: Config): RuleBasedEntityFinder = {
    val entityRulesPath = config[String]("entityRulesPath")
    val avoidRulesPath = config[String]("avoidRulesPath")
    val maxHops = config[Int]("maxHops")
    RuleBasedEntityFinder(entityRulesPath, avoidRulesPath, maxHops = maxHops)
  }

  val DEFAULT_MAX_LENGTH = 50 // maximum length (in tokens) for an entity

  def apply(entityRulesPath: String, avoidRulesPath: String, maxHops: Int, maxLength: Int = DEFAULT_MAX_LENGTH): RuleBasedEntityFinder = {
    val entityRules = FileUtils.getTextFromResource(entityRulesPath)
    val entityEngine = ExtractorEngine(entityRules)

    val avoidRules = FileUtils.getTextFromResource(avoidRulesPath)
    val avoidEngine = ExtractorEngine(avoidRules)

    new RuleBasedEntityFinder(entityEngine = entityEngine, avoidEngine = avoidEngine, maxHops = maxHops)
  }


  /** Keeps the longest mention for each group of overlapping mentions **/
  def keepLongest(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    val mns: Iterable[Mention] = for {
    // find mentions of the same label and sentence overlap
      (k, v) <- mentions.groupBy(m => (m.sentence, m.label))
      m <- v
      // for overlapping mentions starting at the same token, keep only the longest
      longest = v.filter(_.tokenInterval.overlaps(m.tokenInterval)).maxBy(m => m.end - m.start)
    } yield longest
    mns.toVector.distinct
  }

}
