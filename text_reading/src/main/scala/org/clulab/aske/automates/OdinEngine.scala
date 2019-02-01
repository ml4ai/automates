package org.clulab.aske.automates

import com.typesafe.config.Config
import com.typesafe.config.ConfigFactory
import org.clulab.odin.{ExtractorEngine, Mention, State}
import org.clulab.processors.{Document, Processor, Sentence}
import org.clulab.processors.fastnlp.FastNLPProcessor
import org.clulab.aske.automates.entities.{EntityFinder, GrobidEntityFinder, RuleBasedEntityFinder}
import org.clulab.sequences.LexiconNER
import org.clulab.utils.{DocumentFilter, FileUtils, FilterByLength, PassThroughFilter}
import org.slf4j.LoggerFactory
import ai.lum.common.ConfigUtils._
import org.clulab.aske.automates.actions.ExpansionHandler


class OdinEngine(val config: Config = ConfigFactory.load("automates")) {

  val odinConfig: Config = config[Config]("OdinEngine")

  val proc: Processor = new FastNLPProcessor()
  // Document Filter, prunes sentences form the Documents to reduce noise/allow reasonable processing time
  val filterType: String = odinConfig[String]("documentFilter")
  val documentFilter: DocumentFilter = filterType match {
    case "none" => PassThroughFilter()
    case "length" => FilterByLength(proc, cutoff = 150)
    case _ => throw new NotImplementedError(s"Invalid DocumentFilter type specified: $filterType")
  }



  class LoadableAttributes(
    // These are the values which can be reloaded.  Query them for current assignments.
    val actions: OdinActions,
    val engine: ExtractorEngine,
    val entityFinders: Seq[EntityFinder],
    val lexiconNER: Option[LexiconNER]
  )

  object LoadableAttributes {
    def masterRulesPath: String = odinConfig[String]("masterRulesPath")
    def taxonomyPath: String = odinConfig[String]("taxonomyPath")
    def enableEntityFinder: Boolean = odinConfig[Boolean]("enableEntityFinder")
    def enableLexiconNER: Boolean = odinConfig[Boolean]("enableLexiconNER")
    def enableExpansion: Boolean = odinConfig[Boolean]("enableExpansion")

    def apply(): LoadableAttributes = {
      // Reread these values from their files/resources each time based on paths in the config file.
      val masterRules = FileUtils.getTextFromResource(masterRulesPath)
      val actions = OdinActions(taxonomyPath, enableExpansion)
      val extractorEngine = ExtractorEngine(masterRules, actions, actions.globalAction)

      // EntityFinder(s)
      val entityFinders: Seq[EntityFinder] = if (enableEntityFinder) {
        val entityFinderConfig: Config = config[Config]("entityFinder")
        val finderTypes: List[String] = entityFinderConfig[List[String]]("finderTypes")
        finderTypes.map(finderType => EntityFinder.loadEntityFinder(finderType, entityFinderConfig))
      } else Seq.empty[EntityFinder]

      // LexiconNER files
      val lexiconNER = if(enableLexiconNER) {
        val lexiconNERConfig = config[Config]("lexiconNER")
        val lexicons = lexiconNERConfig[List[String]]("lexicons")
        Some(LexiconNER(lexicons, caseInsensitiveMatching = true))
      } else None


      new LoadableAttributes(
        actions,
        extractorEngine, // ODIN component,
        entityFinders,
        lexiconNER
      )
    }
  }

  var loadableAttributes = LoadableAttributes()

  // These public variables are accessed directly by clients which
  // don't know they are loadable and which had better not keep copies.
  def engine = loadableAttributes.engine

  def reload() = loadableAttributes = LoadableAttributes()


  // MAIN PIPELINE METHOD
  def extractFromText(text: String, keepText: Boolean = false, filename: Option[String]): Seq[Mention] = {
    val doc = annotate(text, keepText, filename)   // CTM: processors runs (sentence splitting, tokenization, POS, dependency parse, NER, chunking)
    val odinMentions = extractFrom(doc)  // CTM: runs the Odin grammar
    //println(s"\nodinMentions() -- entities : \n\t${odinMentions.map(m => m.text).sorted.mkString("\n\t")}")

    odinMentions  // CTM: collection of mentions ; to be converted to some form (json)
  }


  def extractFrom(doc: Document): Vector[Mention] = {
    // Prepare the initial state -- if you are using the entity finder then it contains the found entities,
    // else it is empty
    val initialState = loadableAttributes.entityFinders match {
      case efs => State(efs.flatMap(ef => ef.extract(doc)))
      case _ => new State()
    }
    // println(s"In extractFrom() -- res : ${initialState.allMentions.map(m => m.text).mkString(",\t")}")

    // Run the main extraction engine, pre-populated with the initial state
    val events =  engine.extractFrom(doc, initialState).toVector
    //println(s"In extractFrom() -- res : ${res.map(m => m.text).mkString(",\t")}")

    // todo: some appropriate version of "keepMostComplete"
    loadableAttributes.actions.keepLongest(events).toVector
  }

  // ---------- Helper Methods -----------

  // Annotate the text using a Processor and then populate lexicon labels
  def annotate(text: String, keepText: Boolean = false, filename: Option[String]= None): Document = {
    val tokenized = proc.mkDocument(text, keepText = true)  // Formerly keepText, must now be true
    val filtered = documentFilter.filter(tokenized)         // Filter noise from document if enabled (else "pass through")
    val doc = proc.annotate(filtered)
    if (loadableAttributes.lexiconNER.nonEmpty) {           // Add any lexicon/gazetteer tags
      doc.sentences.foreach(addLexiconNER)
    }
    doc.id = filename
    doc
  }

  // Add tags to flag tokens that are found in the provided lexicons/gazetteers
  protected def addLexiconNER(s: Sentence) = {
    // Not all parsers generate entities (e.g., Portuguese clulab processor), so we want to create an empty list here
    // for further processing and filtering operations that expect to be able to query the entities
    if (s.entities.isEmpty) s.entities = Some(Array.fill[String](s.words.length)("O"))
    for {
      (lexiconNERTag, i) <- loadableAttributes.lexiconNER.get.find(s).zipWithIndex
      if lexiconNERTag != OdinEngine.NER_OUTSIDE
    } s.entities.get(i) = lexiconNERTag
  }

}

object OdinEngine {

  // Mention labels
  val DEFINITION_LABEL: String = "Definition"
  val PARAMETER_SETTING_LABEL: String = "ParameterSetting"
  val VALUE_LABEL: String = "Value"
  val VARIABLE_LABEL: String = "Variable"
  // Mention argument types
  val VARIABLE_ARG: String = "variable"
  val DEFINITION_ARG: String = "definition"
  val VALUE_ARG: String = "value"

  val logger = LoggerFactory.getLogger(this.getClass())
  // Used by LexiconNER
  val NER_OUTSIDE = "O"


}
