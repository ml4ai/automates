package org.clulab.aske.automates

import com.typesafe.scalalogging.LazyLogging
import org.clulab.aske.automates.actions.ExpansionHandler
import org.clulab.odin._
import org.clulab.odin.impl.Taxonomy
import org.clulab.utils.FileUtils
import org.yaml.snakeyaml.Yaml
import org.yaml.snakeyaml.constructor.Constructor
import org.clulab.aske.automates.OdinEngine._
import org.clulab.aske.automates.entities.EntityHelper
import org.clulab.struct.Interval



class OdinActions(val taxonomy: Taxonomy, expansionHandler: Option[ExpansionHandler], validArgs: List[String]) extends Actions with LazyLogging {

  def globalAction(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {

    if (expansionHandler.nonEmpty) {
      // expand arguments
      //val (textBounds, expandable) = mentions.partition(m => m.isInstanceOf[TextBoundMention])
      //val expanded = expansionHandler.get.expandArguments(expandable, state)
      //keepLongest(expanded) ++ textBounds

      val (expandable, other) = mentions.partition(m => m matches "Definition")
      val expanded = expansionHandler.get.expandArguments(expandable, state, validArgs) //todo: check if this is the best place for validArgs argument
      keepLongest(expanded) ++ other


      //val mostComplete = keepMostCompleteEvents(expanded, state.updated(expanded))
      //val result = mostComplete ++ textBounds
    } else {
      mentions
    }
  }

  /** Keeps the longest mention for each group of overlapping mentions **/
  def keepLongest(mentions: Seq[Mention], state: State = new State()): Seq[Mention] = {
    val mns: Iterable[Mention] = for {
      // find mentions of the same label and sentence overlap
      (k, v) <- mentions.groupBy(m => (m.sentence, m.label))
      m <- v
      // for overlapping mentions starting at the same token, keep only the longest
      longest = v.filter(_.tokenInterval.overlaps(m.tokenInterval)).maxBy(m => ((m.end - m.start) + 0.1 * m.arguments.size))
    } yield longest
    mns.toVector.distinct
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

  def selectShorterAsVariable(mentions: Seq[Mention], state: State): Seq[Mention] = {
    def foundBy(base: String) = s"$base++selectShorter"

    def mkDefinitionMention(m: Mention): Seq[Mention] = {
      val outer = m.arguments("c1").head
      val inner = m.arguments("c2").head
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
    val greek = Array("alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta", "iota", "kappa", "lambda", "mu", "nu", "xi", "omicron", "pi", "rho", "sigma", "tau", "upsilon", "phi", "chi", "psi", "omega") //todo: read from tsv?
    for {
      m <- mentions
      words = m match {
      case tb: TextBoundMention => m.words
      case rm: RelationMention => m.arguments.getOrElse("variable", Seq()).head.words
      case em: EventMention => m.arguments.getOrElse("variable", Seq()).head.words
      case _ => ???
    }
      if words.length == 1
      word = m.words.head
      if word.length <= 6
      if (word.toLowerCase != word | greek.contains(word) ) // mixed case or all UPPER or is a greek letter todo: try this constraint--- the word is one letter long and tag != CD/DT
    } yield m
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

  def changeLabel(orig: Mention, label: String): Mention = {
    orig match {
      case tb: TextBoundMention => tb.copy(labels = taxonomy.hypernymsFor(label))
      case rm: RelationMention => rm.copy(labels = taxonomy.hypernymsFor(label))
      case em: EventMention => em.copy(labels = taxonomy.hypernymsFor(label))
    }
  }

}

object OdinActions {

  def apply(taxonomyPath: String, enableExpansion: Boolean, validArgs: List[String]) =
    {
      val expansionHandler = if(enableExpansion) {
      Some(ExpansionHandler())
      } else None
      new OdinActions(readTaxonomy(taxonomyPath), expansionHandler, validArgs)
    }

  def readTaxonomy(path: String): Taxonomy = {
    val input = FileUtils.getTextFromResource(path)
    val yaml = new Yaml(new Constructor(classOf[java.util.Collection[Any]]))
    val data = yaml.load(input).asInstanceOf[java.util.Collection[Any]]
    Taxonomy(data)
  }
}
