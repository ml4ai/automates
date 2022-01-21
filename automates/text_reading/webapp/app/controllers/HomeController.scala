package controllers

import java.io.File
import ai.lum.common.ConfigUtils._
import ai.lum.common.FileUtils._
import com.typesafe.config.{Config, ConfigFactory, ConfigValueFactory}

import javax.inject._
import org.clulab.aske.automates.OdinEngine
import org.clulab.aske.automates.alignment.{Aligner, AlignmentHandler}
import org.clulab.aske.automates.apps.ExtractAndAlign.config
import org.clulab.aske.automates.apps.{AutomatesExporter, ExtractAndAlign}
import org.clulab.aske.automates.attachments.MentionLocationAttachment
import org.clulab.aske.automates.data.CosmosJsonDataLoader
import org.clulab.aske.automates.data.ScienceParsedDataLoader
import org.clulab.aske.automates.scienceparse.ScienceParseClient
import org.clulab.aske.automates.serializer.AutomatesJSONSerializer
import org.clulab.grounding.{SVOGrounder, WikidataGrounder, sparqlWikiResult}
import org.clulab.odin.serialization.json.JSONSerializer
import upickle.default._

import scala.collection.mutable.ArrayBuffer
import ujson.json4s.Json4sJson
import org.clulab.odin.{EventMention, Mention, RelationMention, TextBoundMention}
import org.clulab.processors.{Document, Sentence}
import org.clulab.utils.AlignmentJsonUtils.SeqOfGlobalVariables
import org.clulab.utils.{AlignmentJsonUtils, DisplayUtils}
import org.slf4j.{Logger, LoggerFactory}
import org.json4s
import play.api.mvc._
import play.api.libs.json._


/**
  * This controller creates an `Action` to handle HTTP requests to the
  * application's home page.
  */
@Singleton
class HomeController @Inject()(cc: ControllerComponents) extends AbstractController(cc) {

  // -------------------------------------------------
  logger.info("Initializing the OdinEngine ...")
  val generalConfig: Config = ConfigFactory.load()
  val readerType: String = generalConfig[String]("ReaderType")
  val defaultConfig: Config = generalConfig[Config](readerType)
  val config: Config = defaultConfig.withValue("preprocessorType", ConfigValueFactory.fromAnyRef("PassThrough"))
  val ieSystem = OdinEngine.fromConfig(config)
  var proc = ieSystem.proc
  val serializer = JSONSerializer
  lazy val scienceParse = new ScienceParseClient(domain = "localhost", port = "8080")
  lazy val commentReader = OdinEngine.fromConfigSection("CommentEngine")
  lazy val alignmentHandler = new AlignmentHandler(ConfigFactory.load()[Config]("alignment"))
  protected lazy val logger: Logger = LoggerFactory.getLogger(this.getClass)
  // fixme: these should come from config if possible
  private val numAlignments: Int = 5
  private val numAlignmentsSrcToComment: Int = 3
  private val scoreThreshold: Double = 0.0
  private val maxSVOgroundingsPerVarDefault: Int = 5
  private val groundToSVODefault = true
  private val appendToGrFNDefault = true
  private val defaultSerializerName = "AutomatesJSONSerializer" // other - "JSONSerializer"
  private val debugDefault = true
  private val groundToWikiDefault: Boolean = generalConfig[Boolean]("apps.groundToWiki")
  private val saveWikiGroundingsDefault: Boolean = generalConfig[Boolean]("apps.saveWikiGroundingsDefault")

  logger.info("Completed Initialization ...")
  // -------------------------------------------------

  type Trigger = String

  /**
    * Create an Action to render an HTML page.
    *
    * The configuration in the `routes` file means that this method
    * will be called when the application receives a `GET` request with
    * a path of `/`.
    */
  def index() = Action { implicit request: Request[AnyContent] =>
    Ok(views.html.index())
  }

  // -------------------------------------------
  //      API entry points for SVOGrounder
  // -------------------------------------------

  // the API has been disabled by the hosting organization
  def groundMentionsToSVO: Action[AnyContent] = Action { request =>
    val k = 10 //todo: set as param in curl

    // Using Becky's method to load mentions
    val data = request.body.asJson.get.toString()
    val json = ujson.read(data)
    val source = scala.io.Source.fromFile(json("mentions").str)
    val mentionsJson4s = json4s.jackson.parseJson(source.getLines().toArray.mkString(" "))
    source.close()


    val defMentions = JSONSerializer.toMentions(mentionsJson4s).filter(m => m.label matches "Description")
    //    val grfnPath = json("grfn").str
    //    val grfnFile = new File(grfnPath)
    //    val grfn = ujson.read(grfnFile.readString())
    //    val localCommentReader = OdinEngine.fromConfigSectionAndGrFN("CommentEngine", grfnPath)
    val result = SVOGrounder.mentionsToGroundingsJson(defMentions,k)
    Ok(result).as(JSON)
  }

  // -------------------------------------------
  //      API entry points for WikidataGrounder
  // -------------------------------------------

  def groundMentionsToWikidata: Action[AnyContent] = Action { request =>
    // writes a json file with groundings associated with identifier strings
    println("Started grounding")
    val data = request.body.asJson.get.toString()
    val json = ujson.read(data)

    val mentionsPath = json("mentions").str
    val mentionsFile = new File(mentionsPath)

    val ujsonOfMenFile = ujson.read(mentionsFile)
    val defMentions = AutomatesJSONSerializer.toMentions(ujsonOfMenFile).filter(m => m.label contains "Description")
    val glVars = WikidataGrounder.mentionsToGlobalVarsWithWikidataGroundings(defMentions)

    Ok(glVars).as(JSON)

  }


  def groundStringToSVO: Action[AnyContent] = Action { request =>
    val string = request.body.asText.get
    // Note -- topN can be exposed to the API if needed
    Ok(SVOGrounder.groundString(string)).as(JSON)
  }


  // we need documentation on how to use this, or we can remove it

  // currently I think it's only used in odin_interface.py
  // Deprecate


  def getMentions(text: String) = Action {
    val (doc, mentions) = processPlayText(ieSystem, text)
    println(s"Sentence returned from processPlaySentence : ${doc.sentences.head.getSentenceText}")
    for (em <- mentions) {
      if (em.label matches "Description") {
        println("Mention: " + em.text)
        println("att: " + em.attachments.mkString(" "))
      }
    }
    //    val mjson = Json.obj("x" -> mentions.jsonAST.toString)
    val json = JsonUtils.mkJsonFromMentions(mentions)
    Ok(json)
  }

  // -----------------------------------------------------------------
  //                        Webservice Methods
  // -----------------------------------------------------------------
  /**
    * Extract mentions from a text, optionally given a set of already known entities.
    * Expected fields in the json obj passed in:
    *  'text' : String of the paper
    *  'entities' : (optional) List of String entities of interest (e.g., variables)
    * @return Seq[Mention] (json serialized)
    */
  def process_text: Action[JsValue] = Action(parse.json) { request =>
    val data = request.body.toString()
    val json = ujson.read(data)
    val text = json("text").str
    val gazetteer = json.obj.get("entities").map(_.arr.map(_.str))

    val mentionsJson = getOdinJsonMentions(ieSystem, text, gazetteer)
    val compact = json4s.jackson.compactJson(mentionsJson)
    Ok(compact)

  }

  /**
    * Extract mentions from a pdf. Requires Science-Parse running. Expected fields in the json obj passed in:
    *  'pdf' : path to the pdf file
    * @return Seq[Mention] (json serialized)
    */
  def pdf_to_mentions: Action[AnyContent] = Action { request =>
    val data = request.body.asJson.get.toString()
    val json = ujson.read(data)
    val pdfFile = json("pdf").str
    logger.info(s"Extracting mentions from $pdfFile")
    val scienceParseDoc = scienceParse.parsePdf(pdfFile)
    val texts = if (scienceParseDoc.sections.isDefined)  {
      scienceParseDoc.sections.get.map(_.headingAndText) ++ scienceParseDoc.abstractText
    } else scienceParseDoc.abstractText.toSeq
    logger.info("Finished converting to text")
    val mentions = texts.flatMap(t => ieSystem.extractFromText(t, keepText = true, filename = Some(pdfFile)))
    val outFile = json("outfile").str
    AutomatesExporter(outFile).export(mentions)
    //    mentions.saveJSON(outFile, pretty=true)
    Ok("")
  }

  /**
    * Extract mentions from a json produced by running Science Parse on a pdf file. Expected fields in the json obj passed in:
    *  'json' : path to the Science Parse json file, 'outfile' : path to the json file to store extracted mentions. In the curl post request, the data argument will look like this: "--data '{"json": "someDirectory/petpno_Penman.json", "outfile": path/to/output..json}'"
    * @return Seq[Mention] (json serialized)
    */

  def json_doc_to_mentions: Action[AnyContent] = Action { request =>
    val data = request.body.asJson.get.toString()
    val json = ujson.read(data)
    val jsonFile = json("json").str
    logger.info(s"Extracting mentions from $jsonFile")
    val loader = new ScienceParsedDataLoader
    val texts = loader.loadFile(jsonFile)
    val mentions = texts.flatMap(t => ieSystem.extractFromText(t, keepText = true, filename = Some(jsonFile)))
    val outFile = json("outfile").str
    AutomatesExporter(outFile).export(mentions)
    Ok("")
  }


  def cosmos_json_to_mentions: Action[AnyContent] = Action { request =>
    val data = request.body.asJson.get.toString()
    val pathJson = ujson.read(data)
    val jsonPath = pathJson("pathToCosmosJson").str
    logger.info(s"Extracting mentions from $jsonPath")

    // cosmos stores information about each block on each pdf page
    // for each block, we load the text (content) and the location of the text (page_num and block order/index on the page)
    val loader = new CosmosJsonDataLoader
    val textsAndLocations = loader.loadFile(jsonPath)
    val textsAndFilenames = textsAndLocations.map(_.split("<::>").slice(0,2).mkString("<::>"))
    val locations = textsAndLocations.map(_.split("<::>").takeRight(2).mkString("<::>")) //location = pageNum::blockIdx

    println("started extracting")
    // extract mentions form each text block
    val mentions = for (tf <- textsAndFilenames) yield {
      val Array(text, filename) = tf.split("<::>")
      ieSystem.extractFromText(text, keepText = true, Some(filename))
    }

    // store location information from cosmos as an attachment for each mention
    val menWInd = mentions.zipWithIndex
    val mentionsWithLocations = new ArrayBuffer[Mention]()
    for (tuple <- menWInd) {
      // get page and block index for each block; cosmos location information will be the same for all the mentions within one block
      val menInTextBlocks = tuple._1
      val id = tuple._2
      val location = locations(id).split("<::>").map(loc => loc.split(",").map(_.toInt)) //(_.toDouble.toInt)
      val pageNum = location.head
      val blockIdx = location.last

      for (m <- menInTextBlocks) {
        val filename = m.document.id.getOrElse("unknown_file")
        val newMen = m.withAttachment(new MentionLocationAttachment(filename, pageNum, blockIdx, "MentionLocation"))
        mentionsWithLocations.append(newMen)
      }
    }


    val outFile = pathJson("outfile").str
    AutomatesExporter(outFile).export(mentionsWithLocations)

    Ok("")

  }
  /**
    * Align mentions from text, code, comment. Expected fields in the json obj passed in:
    *  'mentions' : file path to Odin serialized mentions
    *  'equations': path to the decoded equations
    *  'grfn'     : path to the grfn file, already expected to have comments and vars/identifiers
    * @return decorated grfn with link elems and link hypotheses
    */
  def align: Action[AnyContent] = Action { request =>

    val data = request.body.asJson.get.toString()
    val pathJson = ujson.read(data) //the json that contains the path to another json---the json that contains all the relevant components, e.g., mentions and equations
    val jsonPath = pathJson("pathToJson").str
    val jsonFile = new File(jsonPath)
    val json = ujson.read(jsonFile.readString())

    val jsonObj = json.obj
    val debug = if (jsonObj.contains("debug")) json("debug").bool else debugDefault


    //if toggles and arguments are not provided in the input, use class defaults (this is to be able to process the previously used GrFN format input)
    val groundToSVO = if (jsonObj.contains("toggles")) {
      json("toggles").obj("groundToSVO").bool
    } else groundToSVODefault

    val groundToWiki = if (jsonObj.contains("toggles")) {
      json("toggles").obj("groundToWiki").bool
    } else groundToWikiDefault

    val saveWikiGroundings = if (jsonObj.contains("toggles")) {
      json("toggles").obj("saveWikiGroundings").bool
    } else saveWikiGroundingsDefault

    val appendToGrFN = if (jsonObj.contains("toggles")) {
      json("toggles").obj("appendToGrFN").bool
    } else appendToGrFNDefault

    val maxSVOgroundingsPerVar = if (jsonObj.contains("arguments")) {
      json("arguments").obj("maxSVOgroundingsPerVar").num.toInt
    } else maxSVOgroundingsPerVarDefault


    val serializerName = if (jsonObj.contains("arguments")) {
      val args = json("arguments")
      if (args.obj.contains("serializer_name")) {
        args.obj("serializer_name").str
      } else defaultSerializerName
    } else defaultSerializerName

    //align components if the right information is provided in the json---we have to have at least Mentions extracted from a paper and either the equations or the source code info (incl. source code variables/identifiers and comments). The json can also contain svo groundings with the key "SVOgroundings".
    if (jsonObj.contains("mentions") || (jsonObj.contains("equations") || jsonObj.contains("source_code"))) {
      val argsForGrounding = AlignmentJsonUtils.getArgsForAlignment(jsonPath, json, groundToSVO, groundToWiki, serializerName)

      // ground!
      val groundings = ExtractAndAlign.groundMentions(
        json,
        argsForGrounding.identifierNames,
        argsForGrounding.identifierShortNames,
        argsForGrounding.descriptionMentions,
        argsForGrounding.parameterSettingMentions,
        argsForGrounding.intervalParameterSettingMentions,
        argsForGrounding.unitMentions,
        argsForGrounding.commentDescriptionMentions,
        argsForGrounding.equationChunksAndSource,
        argsForGrounding.svoGroundings, //Some(Seq.empty)
        argsForGrounding.wikigroundings,
        groundToSVO,
        groundToWiki,
        saveWikiGroundings,
        maxSVOgroundingsPerVar,
        alignmentHandler,
        Some(numAlignments),
        Some(numAlignmentsSrcToComment),
        scoreThreshold,
        appendToGrFN,
        debug
      )

      val groundingsAsString = ujson.write(groundings, indent = 4)

      val groundingsJson4s = json4s.jackson.prettyJson(json4s.jackson.parseJson(groundingsAsString))
      Ok(groundingsJson4s)
    } else {
      logger.warn(s"Nothing to do for keys: $jsonObj")
      Ok("")
    }

  }

  def readMentionsFromJson(pathToMentionsFile: String, mentionType: String): Seq[Mention] = {
    val mentionsFile = new File(pathToMentionsFile)
    val ujsonMentions = ujson.read(mentionsFile.readString())
    // val ujsonMentions = json("mentions") //the mentions loaded from json in the ujson format
    //transform the mentions into json4s format, used by mention serializer
    val jvalueMentions = upickle.default.transform(
      ujsonMentions
    ).to(Json4sJson)
    val textMentions = JSONSerializer.toMentions(jvalueMentions)

    val mentions = textMentions
      .filter(m => m.label matches mentionType)
    mentions
  }

  def readDescrTextsFromJsonForModelComparison(pathToModelComparisonInput: String): (ujson.Obj, ujson.Obj) = {

    val modelComparisonInputFile = new File(pathToModelComparisonInput)
    val ujsonObj = ujson.read(modelComparisonInputFile.readString()).arr
    val paper1obj = ujsonObj.head// keys: grfn_uid, "variable_descrs"
    val paper2obj = ujsonObj.last.obj // keys: grfn_uid, "variable_descrs"
    (ujson.Obj(paper1obj("grfn_uid").str -> paper1obj("variable_descrs")), ujson.Obj(paper2obj("grfn_uid").str -> paper2obj("variable_descrs")))
  }


  def alignMentionsFromTwoModels: Action[AnyContent] = Action { request =>

    val data = request.body.asJson.get.toString()
    val pathJson = ujson.read(data) //the json that contains the path to another json---the json that contains all the relevant components, e.g., mentions and equations
    val jsonPath = pathJson("pathToJson").str
    val jsonFile = new File(jsonPath)
    val json = ujson.read(jsonFile.readString())
    val jsonObj = json.obj

    val debug = if (jsonObj.contains("debug")) json("debug").bool else debugDefault
    val modelCompAlignmentHandler = new AlignmentHandler(ConfigFactory.load()[Config]("modelComparisonAlignment"))

    val inputFilePath = json("input_file").str
    val modelComparisonInputFile = new File(inputFilePath)
    val ujsonObj = ujson.read(modelComparisonInputFile.readString()).arr
    val paper1obj = ujsonObj.head.obj// keys: grfn_uid, "variable_descrs"
  val paper2obj = ujsonObj.last.obj // keys: grfn_uid, "variable_descrs"

    val paper1id = paper1obj("grfn_uid").str
    val paper2id = paper2obj("grfn_uid").str

    val paper1values = paper1obj("variable_descrs").arr
    val paper2values = paper2obj("variable_descrs").arr

    val paper1texts = paper1values.map(v => v.obj("code_identifier") + " " + v.obj("text_identifier") + " " + v.obj("text_description"))
    val paper2texts = paper2values.map(v => v.obj("code_identifier") + " " + v.obj("text_identifier") + " " + v.obj("text_description"))


    // get alignments
    val alignments = modelCompAlignmentHandler.w2v.alignTexts(paper1texts, paper2texts, useBigrams = true)

    // group by src idx, and keep only top k (src, dst, score) for each src idx
    val topKAlignments = Aligner.topKBySrc(alignments, 3, scoreThreshold, debug)

    // id link elements
    val linkElements = ExtractAndAlign.getInterModelComparisonLinkElements(paper1values, paper1id, paper2values, paper2id)

    val hypotheses = ExtractAndAlign.getInterPaperLinkHypothesesWithValues(linkElements, topKAlignments, debug)
    var outputJson = ujson.Obj()

    if (debug) {
      for (le <- linkElements.keys) {
        outputJson(le) = linkElements(le)
      }
    }

    outputJson("grfn1") = paper1id
    outputJson("grfn2") = paper2id

    outputJson("variable_alignment") = hypotheses
    val groundingsAsString = ujson.write(outputJson, indent = 4)

    val groundingsJson4s = json4s.jackson.prettyJson(json4s.jackson.parseJson(groundingsAsString))
    Ok(groundingsJson4s)

  }

  // -----------------------------------------------------------------
  //               Backend methods that do stuff :)
  // -----------------------------------------------------------------

  def processPlayText(ieSystem: OdinEngine, text: String, gazetteer: Option[Seq[String]] = None): (Document, Vector[Mention]) = {
    // preprocessing
    logger.info(s"Processing sentence : ${text}")
    val doc = ieSystem.cleanAndAnnotate(text, keepText = true, filename = None)

    logger.info(s"DOC : ${doc}")
    // extract mentions from annotated document
    val mentions = if (gazetteer.isDefined) {
      ieSystem.extractFromDocWithGazetteer(doc, gazetteer = gazetteer.get)
    } else {
      ieSystem.extractFrom(doc)
    }
    val sorted = mentions.sortBy(m => (m.sentence, m.getClass.getSimpleName)).toVector

    logger.info(s"Done extracting the mentions ... ")
    logger.info(s"They are : ${mentions.map(m => m.text).mkString(",\t")}")

    // return the sentence and all the mentions extracted ... TODO: fix it to process all the sentences in the doc
    (doc, sorted)
  }

  // Method where aske reader processing for webservice happens
  def getOdinJsonMentions(ieSystem: OdinEngine, text: String, gazetteer: Option[Seq[String]] = None): org.json4s.JsonAST.JValue = {

    // preprocessing
    logger.info(s"Processing sentence : $text" )
    val (_, mentions) = processPlayText(ieSystem, text, gazetteer)

    // Export to JSON
    val json = serializer.jsonAST(mentions)
    json
  }


  def parseSentence(text: String, showEverything: Boolean) = Action {
    val (doc, eidosMentions) = processPlayText(ieSystem, text)
    logger.info(s"Sentence returned from processPlayText : ${doc.sentences.head.getSentenceText}")
    val json = mkJson(text, doc, eidosMentions, showEverything) // we only handle a single sentence
    Ok(json)
  }

  protected def mkParseObj(sentence: Sentence, sb: StringBuilder): Unit = {
    def getTdAt(option: Option[Array[String]], n: Int): String = {
      val text = if (option.isEmpty) ""
      else option.get(n)

      "<td>" + xml.Utility.escape(text) + "</td>"
    }

    sentence.words.indices.foreach { i =>
      sb
        .append("<tr>")
        .append("<td>" + xml.Utility.escape(sentence.words(i)) + "</td>")
        .append(getTdAt(sentence.tags, i))
        .append(getTdAt(sentence.lemmas, i))
        .append(getTdAt(sentence.entities, i))
        .append(getTdAt(sentence.norms, i))
        .append(getTdAt(sentence.chunks, i))
        .append("</tr>")
    }
  }

  protected def mkParseObj(doc: Document): String = {
    val header =
      """
        |  <tr>
        |    <th>Word</th>
        |    <th>Tag</th>
        |    <th>Lemma</th>
        |    <th>Entity</th>
        |    <th>Norm</th>
        |    <th>Chunk</th>
        |  </tr>
      """.stripMargin
    val sb = new StringBuilder(header)

    doc.sentences.foreach(mkParseObj(_, sb))
    sb.toString
  }

  def mkJson(text: String, doc: Document, mentions: Vector[Mention], showEverything: Boolean): JsValue = {
    logger.info("Found mentions (in mkJson):")
    mentions.foreach(DisplayUtils.displayMention)

    val sent = doc.sentences.head
    val syntaxJsonObj = Json.obj(
      "text" -> text,
      "entities" -> mkJsonFromTokens(doc),
      "relations" -> mkJsonFromDependencies(doc)
    )
    val eidosJsonObj = mkJsonForEidos(text, sent, mentions, showEverything)
    val groundedAdjObj = mkGroundedObj(mentions)
    val parseObj = mkParseObj(doc)

    // These print the html and it's a mess to look at...
    // println(s"Grounded Gradable Adj: ")
    // println(s"$groundedAdjObj")

    Json.obj(
      "syntax" -> syntaxJsonObj,
      "eidosMentions" -> eidosJsonObj,
      "groundedAdj" -> groundedAdjObj,
      "parse" -> parseObj
    )
  }

  def mkGroundedObj(mentions: Vector[Mention]): String = {
    var objectToReturn = ""

    //return events and relations first---those tend to be the ones we are most interested in and having them come first will help avoid scrolling through the entities first
    // collect relation mentions for display
    val relations = mentions.flatMap {
      case m: RelationMention => Some(m)
      case _ => None
    }

    val events = mentions.filter(_ matches "Event")
    if (events.nonEmpty) {
      objectToReturn += s"<h2>Found Events:</h2>"
      for (event <- events) {
        objectToReturn += s"${DisplayUtils.webAppMention(event)}"
      }
    }

    // Entities
    val entities = mentions.filter(_ matches "Entity")
    if (entities.nonEmpty){
      objectToReturn += "<h2>Found Entities:</h2>"
      for (entity <- entities) {
        objectToReturn += s"${DisplayUtils.webAppMention(entity)}"
      }
    }

    objectToReturn += "<br>"
    objectToReturn
  }

  def mkJsonForEidos(sentenceText: String, sent: Sentence, mentions: Vector[Mention], showEverything: Boolean): Json.JsValueWrapper = {
    val topLevelTBM = mentions.flatMap {
      case m: TextBoundMention => Some(m)
      case _ => None
    }
    // collect event mentions for display
    val events = mentions.flatMap {
      case m: EventMention => Some(m)
      case _ => None
    }
    // collect relation mentions for display
    val relations = mentions.flatMap {
      case m: RelationMention => Some(m)
      case _ => None
    }
    // collect triggers for event mentions
    val triggers = events.flatMap { e =>
      val argTriggers = for {
        a <- e.arguments.values
        if a.isInstanceOf[EventMention]
      } yield a.asInstanceOf[EventMention].trigger
      e.trigger +: argTriggers.toSeq
    }
    // collect event arguments as text bound mentions
    val entities = for {
      e <- events ++ relations
      a <- e.arguments.values.flatten
    } yield a match {
      case m: TextBoundMention => m
      case m: RelationMention => new TextBoundMention(m.labels, m.tokenInterval, m.sentence, m.document, m.keep, m.foundBy)
      case m: EventMention => m.trigger
    }
    // generate id for each textbound mention
    val tbMentionToId = (entities ++ triggers ++ topLevelTBM)
      .distinct
      .zipWithIndex
      .map { case (m, i) => (m, i + 1) }
      .toMap
    // return brat output
    Json.obj(
      "text" -> sentenceText,
      "entities" -> mkJsonFromEntities(entities ++ topLevelTBM, tbMentionToId),
      "triggers" -> mkJsonFromEntities(triggers, tbMentionToId),
      "events" -> mkJsonFromEventMentions(events, tbMentionToId),
      "relations" -> (if (showEverything) mkJsonFromRelationMentions(relations, tbMentionToId) else Array[String]())
    )
  }

  def mkJsonFromEntities(mentions: Vector[TextBoundMention], tbmToId: Map[TextBoundMention, Int]): Json.JsValueWrapper = {
    val entities = mentions.map(m => mkJsonFromTextBoundMention(m, tbmToId(m)))
    Json.arr(entities: _*)
  }

  def mkJsonFromTextBoundMention(m: TextBoundMention, i: Int): Json.JsValueWrapper = {
    Json.arr(
      s"T$i",
      HomeController.statefulRepresentation(m).label,
      Json.arr(Json.arr(m.startOffset, m.endOffset))
    )
  }

  def mkJsonFromEventMentions(ee: Seq[EventMention], tbmToId: Map[TextBoundMention, Int]): Json.JsValueWrapper = {
    var i = 0
    val jsonEvents = for (e <- ee) yield {
      i += 1
      mkJsonFromEventMention(e, i, tbmToId)
    }
    Json.arr(jsonEvents: _*)
  }

  def mkJsonFromEventMention(ev: EventMention, i: Int, tbmToId: Map[TextBoundMention, Int]): Json.JsValueWrapper = {
    Json.arr(
      s"E$i",
      s"T${tbmToId(ev.trigger)}",
      Json.arr(mkArgMentions(ev, tbmToId): _*)
    )
  }

  def mkJsonFromRelationMentions(rr: Seq[RelationMention], tbmToId: Map[TextBoundMention, Int]): Json.JsValueWrapper = {
    var i = 0
    val jsonRelations = for (r <- rr) yield {
      i += 1
      mkJsonFromRelationMention(r, i, tbmToId)
    }
    Json.arr(jsonRelations: _*)
  }

  def getArg(r: RelationMention, name: String): TextBoundMention = r.arguments(name).head match {
    case m: TextBoundMention => m
    case m: EventMention => m.trigger
    case r: RelationMention => prioritizedArg(r)//smushIntoTextBound(r) //fixme - this is likely not the right solution...!
  }

  def smushIntoTextBound(r: RelationMention): TextBoundMention = new TextBoundMention(r.labels, r.tokenInterval, r.sentence, r.document, r.keep, r.foundBy + "-smushed", r.attachments)

  def prioritizedArg(r: RelationMention): TextBoundMention = {
    val priorityArgs = Seq("pitch", "beat", "value")
    val prioritized = r.arguments.filter(a => priorityArgs.contains(a._1)).values.flatten.headOption
    prioritized.getOrElse(r.arguments.values.flatten.head).asInstanceOf[TextBoundMention] //fixme
  }

  def mkJsonFromRelationMention(r: RelationMention, i: Int, tbmToId: Map[TextBoundMention, Int]): Json.JsValueWrapper = {
    val relationArgNames = r.arguments.keys.toSeq
    val head = relationArgNames.head
    val last = relationArgNames.last

    // fixme: this is a temp solution to avoid error caused by the assertion below, but the visualization does not look right
    if (relationArgNames.length > 2) {
      logger.warn("More than three args, webapp will need to be updated to handle!")
    }
//    assert(relationArgNames.length < 3, "More than three args, webapp will need to be updated to handle!")
    Json.arr(
      s"R$i",
      r.label,
      // arguments are hardcoded to ensure the direction (controller -> controlled)
      Json.arr(
        Json.arr(head, "T" + tbmToId(getArg(r, head))),
        Json.arr(last, "T" + tbmToId(getArg(r, last)))
      )
    )
  }



  def mkArgMentions(ev: EventMention, tbmToId: Map[TextBoundMention, Int]): Seq[Json.JsValueWrapper] = {
    val args = for {
      argRole <- ev.arguments.keys
      m <- ev.arguments(argRole)
    } yield {
      val arg = m match {
        case m: TextBoundMention => m
        case m: RelationMention => new TextBoundMention(m.labels, m.tokenInterval, m.sentence, m.document, m.keep, m.foundBy)
        case m: EventMention => m.trigger
      }
      mkArgMention(argRole, s"T${tbmToId(arg)}")
    }
    args.toSeq
  }

  def mkArgMention(argRole: String, id: String): Json.JsValueWrapper = {
    Json.arr(argRole, id)
  }

  def mkJsonFromTokens(doc: Document): Json.JsValueWrapper = {
    var offset = 0

    val tokens = doc.sentences.flatMap { sent =>
      val tokens = sent.words.indices.map(i => mkJsonFromToken(sent, offset, i))
      offset += sent.words.size
      tokens
    }
    Json.arr(tokens: _*)
  }

  def mkJsonFromToken(sent: Sentence, offset: Int, i: Int): Json.JsValueWrapper = {
    Json.arr(
      s"T${offset + i + 1}", // token id (starts at one, not zero)
      sent.tags.get(i), // lets assume that tags are always available
      Json.arr(Json.arr(sent.startOffsets(i), sent.endOffsets(i)))
    )
  }

  def mkJsonFromDependencies(doc: Document): Json.JsValueWrapper = {
    var offset = 1

    val rels = doc.sentences.flatMap { sent =>
      var relId = 0
      val deps = sent.universalEnhancedDependencies.get // lets assume that dependencies are always available
      val rels = for {
        governor <- deps.outgoingEdges.indices
        (dependent, label) <- deps.outgoingEdges(governor)
      } yield {
        val json = mkJsonFromDependency(offset + relId, offset + governor, offset + dependent, label)
        relId += 1
        json
      }
      offset += sent.words.size
      rels
    }
    Json.arr(rels: _*)
  }

  def mkJsonFromDependency(relId: Int, governor: Int, dependent: Int, label: String): Json.JsValueWrapper = {
    Json.arr(
      s"R$relId",
      label,
      Json.arr(
        Json.arr("governor", s"T$governor"),
        Json.arr("dependent", s"T$dependent")
      )
    )
  }

  def tab():String = "&nbsp;&nbsp;&nbsp;&nbsp;"
}

object HomeController {

  // fixme: ordering/precedence...
  def statefulRepresentation(m: Mention): Mention = {
    val stateAffix = ""


    // If you found something, append the affix to top label and add to the Seq of labels
    if (stateAffix.nonEmpty) {
      val modifiedLabels = Seq(m.label ++ stateAffix) ++ m.labels
      val out = m match {
        case tb: TextBoundMention => m.asInstanceOf[TextBoundMention].copy(labels = modifiedLabels)
        case rm: RelationMention => m.asInstanceOf[RelationMention].copy(labels = modifiedLabels)
        case em: EventMention => em.copy(labels = modifiedLabels)
      }

      return out
    }

    // otherwise, return original
    m
  }

}