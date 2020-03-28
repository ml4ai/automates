package controllers

import java.io.File

import ai.lum.common.ConfigUtils._
import ai.lum.common.FileUtils._
import com.typesafe.config.{Config, ConfigFactory}
import javax.inject._
import org.clulab.aske.automates.OdinEngine
import org.clulab.aske.automates.alignment.AlignmentHandler
import org.clulab.aske.automates.apps.ExtractAndAlign
import org.clulab.aske.automates.apps.ExtractAndExport.dataLoader
import org.clulab.aske.automates.data.ScienceParsedDataLoader
import org.clulab.aske.automates.grfn.GrFNParser
import org.clulab.aske.automates.scienceparse.ScienceParseClient
import org.clulab.grounding.SVOGrounder
import org.clulab.odin.serialization.json.JSONSerializer
import org.clulab.odin.{Attachment, EventMention, Mention, RelationMention, TextBoundMention}
import org.clulab.processors.{Document, Sentence}
import org.clulab.utils.DisplayUtils
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
  val ieSystem = OdinEngine.fromConfig()
  var proc = ieSystem.proc
  val serializer = JSONSerializer
  lazy val scienceParse = new ScienceParseClient(domain="localhost", port="8080")
  lazy val commentReader = OdinEngine.fromConfigSection("CommentEngine")
  lazy val alignmentHandler = new AlignmentHandler(ConfigFactory.load()[Config]("alignment"))
  protected lazy val logger: Logger = LoggerFactory.getLogger(this.getClass)
  private val numAlignments: Int = 5
  private val numAlignmentsSrcToComment: Int = 1
  private val scoreThreshold: Double = 0.0
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

  def groundMentionsToSVO: Action[AnyContent] = Action { request =>
    val k = 10 //todo: set as param in curl

    // Using Becky's method to load mentions
    val data = request.body.asJson.get.toString()
    val json = ujson.read(data)
    val source = scala.io.Source.fromFile(json("mentions").str)
    val mentionsJson4s = json4s.jackson.parseJson(source.getLines().toArray.mkString(" "))
    source.close()

    // NOTE: Masha's original method
    // val string = request.body.asText.get
    // val jval = json4s.jackson.parseJson(string)
    
    val mentions = JSONSerializer.toMentions(mentionsJson4s)
    val result = SVOGrounder.mentionsToGroundingsJson(mentions, k)
    Ok(result).as(JSON)
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
      if (em.label matches "Definition") {
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
    * Extract mentions from a pdf. Expected fields in the json obj passed in:
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
    val mentionsJson = serializer.jsonAST(mentions)
    val parsed_output = PlayUtils.toPlayJson(mentionsJson)
    Ok(parsed_output)
  }

  /**
    * Extract mentions from a serialized Document json. Expected fields in the json obj passed in:
    *  'json' : path to the serialized Document json file
    * @return Seq[Mention] (json serialized)
    */

  def jsonDoc_to_mentions: Action[AnyContent] = Action { request =>
    val data = request.body.asJson.get.toString()
    val json = ujson.read(data)
    val jsonFile = json("json").str
    logger.info(s"Extracting mentions from $jsonFile")
    val loader = new ScienceParsedDataLoader
    val texts = loader.loadFile(jsonFile)
    val mentions = texts.flatMap(t => ieSystem.extractFromText(t, keepText = true, filename = Some(jsonFile)))
    val mentionsJson = serializer.jsonAST(mentions)
    val parsed_output = PlayUtils.toPlayJson(mentionsJson)
    Ok(parsed_output)
  }

  /**
    * Align mentions from text, code, comment. Expected fields in the json obj passed in:
    *  'mentions' : file path to Odin serialized mentions
    *  'equations': path to the decoded equations
    *  'grfn'     : path to the grfn file, already expected to have comments and vars
    * @return decorated grfn with link elems and link hypotheses
    */
  def align: Action[AnyContent] = Action { request =>
    val data = request.body.asJson.get.toString()
    val json = ujson.read(data)
    // Load the mentions
    val source = scala.io.Source.fromFile(json("mentions").str)
    val mentionsJson4s = json4s.jackson.parseJson(source.getLines().toArray.mkString(" "))
    source.close()
    val textMentions = JSONSerializer.toMentions(mentionsJson4s)
    // get the equations
    val equationFile = json("equations").str
    val equationChunksAndSource = ExtractAndAlign.loadEquations(equationFile)
    
    // Get the GrFN
    val grfnFile = new File(json("grfn").str)
    val grfn = ujson.read(grfnFile.readString())
    // ground!
    val groundedGrfn = ExtractAndAlign.groundMentionsToGrfn(
      textMentions,
      grfn,
      commentReader,
      equationChunksAndSource,
      alignmentHandler,
      numAlignments,
      numAlignmentsSrcToComment,
      scoreThreshold
    )
    // FIXME: add a conversion method for ujson <--> play json
    val groundedGrfnJson4s = json4s.jackson.parseJson(groundedGrfn.str)
    Ok(PlayUtils.toPlayJson(groundedGrfnJson4s))
  }

  // -----------------------------------------------------------------
  //               Backend methods that do stuff :)
  // -----------------------------------------------------------------

  def processPlayText(ieSystem: OdinEngine, text: String, gazetteer: Option[Seq[String]] = None): (Document, Vector[Mention]) = {
    // preprocessing
    logger.info(s"Processing sentence : ${text}" )
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

    assert(relationArgNames.length < 3, "More than three args, webapp will need to be updated to handle!")
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
      val deps = sent.dependencies.get // lets assume that dependencies are always available
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
