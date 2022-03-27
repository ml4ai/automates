package org.clulab.aske.automates

import com.typesafe.config.Config
import com.typesafe.config.ConfigFactory
import com.typesafe.config.ConfigValueFactory
import org.clulab.odin.{ExtractorEngine, Mention, State}
import org.clulab.processors.{Document, Processor}
import org.clulab.processors.fastnlp.FastNLPProcessor
import org.clulab.aske.automates.entities.{EntityFinder,StringMatchEntityFinder}
import org.clulab.utils.{DocumentFilter, FileUtils, FilterByLength, PassThroughFilter}
import org.slf4j.LoggerFactory
import ai.lum.common.ConfigUtils._
import org.clulab.aske.automates.data.{EdgeCaseParagraphPreprocessor, LightPreprocessor, PassThroughPreprocessor, Preprocessor}


class OdinEngine(
                  val proc: Processor,
                  masterRulesPath: String,
                  taxonomyPath: String,
                  var entityFinders: Seq[EntityFinder],
                  enableExpansion: Boolean,
                  validArgs: List[String],
                  freqWords: Array[String],
                  filterType: Option[String],
                  preprocessorType: String) {

  val documentFilter: DocumentFilter = filterType match {
    case None => PassThroughFilter()
    case Some("length") => FilterByLength(proc, cutoff = 150)
    case _ => throw new NotImplementedError(s"Invalid DocumentFilter type specified: $filterType")
  }

  val edgeCaseFilter: Preprocessor = preprocessorType match {
    case "Light" => LightPreprocessor()
    case "EdgeCase" => EdgeCaseParagraphPreprocessor()
    case "PassThrough" => PassThroughPreprocessor()
  }

  class LoadableAttributes(
    // These are the values which can be reloaded.  Query them for current assignments.
    val actions: OdinActions,
    val engine: ExtractorEngine,

  )

  object LoadableAttributes {

    def apply(): LoadableAttributes = {
      // Reread these values from their files/resources each time based on paths in the config file.
      val masterRules = FileUtils.getTextFromResource(masterRulesPath)
      val actions = OdinActions(taxonomyPath, enableExpansion, validArgs, freqWords)
      val extractorEngine = ExtractorEngine(masterRules, actions, actions.globalAction)
      new LoadableAttributes(
        actions,
        extractorEngine
      )
    }
  }

  var loadableAttributes = LoadableAttributes()
  val actions = loadableAttributes.actions

  // These public variables are accessed directly by clients which
  // don't know they are loadable and which had better not keep copies.
  def engine = loadableAttributes.engine
  def reload() = loadableAttributes = LoadableAttributes()

  // MAIN PIPELINE METHOD
  def cleanAndAnnotate(text: String, keepText: Boolean = false, filename: Option[String]): Document = {
    val filteredText = edgeCaseFilter.cleanUp(text)
    val doc = annotate(filteredText, keepText, filename)   // CTM: processors runs (sentence splitting, tokenization, POS, dependency parse, NER, chunking)
    doc
  }

  def extractFrom(doc: Document): Vector[Mention] = {
    var initialState = new State()
    // Add any mentions from the entityFinders to the initial state
    if (entityFinders.nonEmpty) {
      initialState = initialState.updated(entityFinders.flatMap(ef => ef.extract(doc)))
    }
    // println(s"In extractFrom() -- res : ${initialState.allMentions.map(m => m.text).mkString(",\t")}")

    // Run the main extraction engine, pre-populated with the initial state
    val events = actions.processCommands(engine.extractFrom(doc, initialState).toVector)
    val (paramSettings, nonParamSettings) = events.partition(_.label.contains("ParameterSetting")) // `paramSettings` includes interval param setting
    val noOverlapParamSettings = actions.intervalParamSettTakesPrecedence(paramSettings)
    val paramSettingsAndOthers = noOverlapParamSettings ++ nonParamSettings
    val newModelParams1 = actions.paramSettingVarToModelParam(paramSettingsAndOthers)
    val modelCorefResolve = actions.resolveModelCoref(paramSettingsAndOthers)

    // process context attachments to the initially extracted mentions
    val newEventsWithContexts = actions.makeNewMensWithContexts(modelCorefResolve)
    val (contextEvents, nonContexts) = newEventsWithContexts.partition(_.label.contains("ContextEvent"))
    val mensWithContextAttachment = actions.processRuleBasedContextEvent(contextEvents)

    // post-process the mentions with untangleConj and combineFunction
    val (descriptionMentions, nonDescrMens) = (mensWithContextAttachment ++ nonContexts).partition(_.label.contains("Description"))

    val (functionMentions, nonFunctions) = nonDescrMens.partition(_.label.contains("Function"))
    val (modelDescrs, nonModelDescrs) = nonFunctions.partition(_.labels.contains("ModelDescr"))
    val (modelNames, other) = nonModelDescrs.partition(_.label == "Model")
    val modelFilter = actions.filterModelNames(modelNames)
    val untangled = actions.untangleConj(descriptionMentions)
    val combining = actions.combineFunction(functionMentions)
    val newModelParams2 = actions.functionArgsToModelParam(combining)
    val finalModelDescrs = modelDescrs.filter(_.arguments.contains("modelName"))
    val finalModelParam = actions.filterModelParam(newModelParams1 ++ newModelParams2)

    actions.assembleVarsWithParamsAndUnits(actions.replaceWithLongerIdentifier(actions.keepLongest(other ++ combining ++ modelFilter ++ finalModelParam  ++ finalModelDescrs) ++ untangled)).toVector.distinct

  }

  def extractFromText(text: String, keepText: Boolean = false, filename: Option[String]): Seq[Mention] = {
    val doc = cleanAndAnnotate(text, keepText, filename)
    val odinMentions = extractFrom(doc)  // CTM: runs the Odin grammar
    odinMentions  // CTM: collection of mentions ; to be converted to some form (json)
  }

  // Supports web service, when existing entities are already known but from outside the project
  def extractFromDocWithGazetteer(doc: Document, gazetteer: Seq[String]): Seq[Mention] = {
    val label = OdinEngine.VARIABLE_GAZETTEER_LABEL
    val providedFinder = StringMatchEntityFinder.fromStrings(gazetteer, label)
    entityFinders = entityFinders ++ Seq(providedFinder)
    val results = extractFrom(doc)
    // cleanup -- remove the finder from this query
    entityFinders = entityFinders.diff(Seq(providedFinder))

    // return results
    results
  }

  // ---------- Helper Methods -----------

  // Annotate the text using a Processor and then populate lexicon labels
  def annotate(text: String, keepText: Boolean = false, filename: Option[String]= None): Document = {
    val tokenized = proc.mkDocument(text, keepText = true)  // Formerly keepText, must now be true
    val filtered = documentFilter.filter(tokenized)         // Filter noise from document if enabled (else "pass through")
    val doc = proc.annotate(filtered)
    doc.id = filename
    doc
  }

}

object OdinEngine {

  // todo: ability to load/use diff processors
  lazy val proc: Processor = new FastNLPProcessor()

  // Mention labels
  val DESCRIPTION_LABEL: String = "Description"
  val MODEL_DESCRIPTION_LABEL: String = "ModelDescr"
  val MODEL_LIMITATION_LABEL: String = "ModelLimitation"
  val CONJ_DESCRIPTION_LABEL: String = "ConjDescription"
  val CONJ_DESCRIPTION_TYPE2_LABEL: String = "ConjDescriptionType2"
  val INTERVAL_PARAMETER_SETTING_LABEL: String = "IntervalParameterSetting"
  val PARAMETER_SETTING_LABEL: String = "ParameterSetting"
  val VALUE_LABEL: String = "Value"
  val IDENTIFIER_LABEL: String = "Identifier"
  val VARIABLE_GAZETTEER_LABEL: String = "VariableGazetteer"
  val UNIT_LABEL: String = "UnitRelation"
  val MODEL_LABEL: String = "Model"
  val FUNCTION_LABEL: String = "Function"
  val CONTEXT_LABEL: String = "Context"
  val CONTEXT_EVENT_LABEL: String = "ContextEvent"
  // Mention argument types
  val VARIABLE_ARG: String = "variable"
  val VALUE_LEAST_ARG: String = "valueLeast"
  val VALUE_MOST_ARG: String = "valueMost"
  val DESCRIPTION_ARG: String = "description"
  val VALUE_ARG: String = "value"
  val UNIT_ARG: String = "unit"
  val FUNCTION_INPUT_ARG: String = "input"
  val FUNCTION_OUTPUT_ARG: String = "output"
  val MODEL_NAME_ARG: String = "modelName"
  val MODEL_DESCRIPTION_ARG: String = "modelDescr"
  val CONTEXT_ARG: String = "context"
  val CONTEXT_EVENT_ARG: String = "event"

  val logger = LoggerFactory.getLogger(this.getClass())
  // Used by LexiconNER
  val NER_OUTSIDE = "O"

  def fromConfigSection(configSection: String) = OdinEngine.fromConfig(ConfigFactory.load()[Config](configSection))
  def fromConfigSectionAndGrFN(configSection: String, grfnFile: String) = {
    val config:Config = ConfigFactory.load()[Config](configSection)
    OdinEngine.fromConfig(config.withValue("entityFinder.grfnFile", ConfigValueFactory.fromAnyRef(grfnFile)))
  }
  def fromConfig(odinConfig: Config = ConfigFactory.load()[Config]("TextEngine")): OdinEngine = {
//    // The config with the main settings
//    val odinConfig: Config = config[Config]("TextEngine")


    // document filter: used to clean the input ahead of time
    // fixme: should maybe be moved?
    val filterType = odinConfig.get[String]("documentFilter")
    val preprocessorType = odinConfig.get[String](path = "preprocessorType").getOrElse("PassThrough")

    // Odin Grammars
    val masterRulesPath: String = odinConfig[String]("masterRulesPath")
    val taxonomyPath: String = odinConfig[String]("taxonomyPath")

    // EntityFinders: used to find entities ahead of time
    val enableEntityFinder: Boolean = odinConfig.get[Boolean]("entityFinder.enabled").getOrElse(false)
    val entityFinders: Seq[EntityFinder] = if (enableEntityFinder) {
      val entityFinderConfig: Config = odinConfig[Config]("entityFinder")
      val finderTypes: List[String] = entityFinderConfig[List[String]]("finderTypes")
      finderTypes.map(finderType => EntityFinder.loadEntityFinder(finderType, entityFinderConfig))
    } else Seq.empty[EntityFinder]

    // LexiconNER: Used to annotate the documents with info from a gazetteer
//    val enableLexiconNER: Boolean = odinConfig.get[Boolean]("lexiconNER.enable").getOrElse(false)
//    val lexiconNER = if(enableLexiconNER) {
//      val lexiconNERConfig = odinConfig[Config]("lexiconNER")
//      val lexicons = lexiconNERConfig[List[String]]("lexicons")
//      Some(LexiconNER(lexicons, caseInsensitiveMatching = true))
//    } else None

    // expansion: used to optionally expand mentions in certain situations to get more complete text spans
    val validArgs: List[String] = odinConfig[List[String]]("validArgs")
    val enableExpansion: Boolean = odinConfig[Boolean]("enableExpansion")
    val freqWords = FileUtils.loadFromOneColumnTSV(odinConfig[String]("freqWordsPath"))

    new OdinEngine(proc, masterRulesPath, taxonomyPath, entityFinders, enableExpansion, validArgs, freqWords, filterType, preprocessorType)
  }

}
