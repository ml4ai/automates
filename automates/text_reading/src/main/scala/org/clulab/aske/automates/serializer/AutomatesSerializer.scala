package org.clulab.aske.automates.serializer


import org.clulab.aske.automates.attachments.{ContextAttachment, DiscontinuousCharOffsetAttachment, FunctionAttachment, MentionLocationAttachment, ParamSetAttachment, ParamSettingIntAttachment, UnitAttachment}
import org.clulab.odin
import org.clulab.odin.{Attachment, EventMention, Mention, RelationMention, TextBoundMention}
import org.clulab.processors.{Document, Sentence}
import org.clulab.struct.{DirectedGraph, Edge, GraphMap, Interval}
import org.clulab.odin.serialization.json._
import org.clulab.serialization.json.{DirectedGraphOps, EdgeOps, Equivalency, GraphMapOps, JSONSerialization}
import org.clulab.aske.automates.mentions.CrossSentenceEventMention
import org.json4s.{JArray, JNothing, JNull, JObject, JValue}

import scala.collection.mutable.ArrayBuffer
import scala.util.hashing.MurmurHash3.{finalizeHash, mix, stringHash, unorderedHash}

object AutomatesJSONSerializer {

  // This is a ujson adaptation of org.clulab.odin.serialization.json.JSONSerializer

  // Deserializing mentions
  def toMentions(menUJson: ujson.Value): Seq[Mention] = {

    require(!menUJson("mentions").isNull, "\"mentions\" key missing from json")
    require(!menUJson("documents").isNull, "\"documents\" key missing from json")

    val docMap = mkDocumentMap(menUJson("documents"))
    val mentionsUJson = menUJson("mentions")

    mentionsUJson.arr.map(item => toMention(item, docMap)).toSeq
  }


  def toMention(mentionComponents: ujson.Value, docMap: Map[String, Document]): Mention = {
    val tokIntObj = mentionComponents("tokenInterval").obj
    val tokenInterval = Interval(tokIntObj("start").num.toInt, tokIntObj("end").num.toInt)
    val labels = mentionComponents("labels").arr.map(_.str).toArray
    val sentence = mentionComponents("sentence").num.toInt
    val docHash = mentionComponents("document").str.toInt
    val document = docMap(docHash.toString)
    val keep = mentionComponents("keep").bool
    val foundBy = mentionComponents("foundBy").str
    val menType = mentionComponents("type").str
    val sentences = if (menType == "CrossSentenceEventMention") {
      mentionComponents("sentences").arr.map(_.num.toInt)
    } else Seq.empty
    val attachments = new ArrayBuffer[Attachment]

    if (mentionComponents.obj.contains("attachments")) {
      val attObjArray = mentionComponents("attachments").arr
      for (ao <- attObjArray) {
        val att = toAttachment(ao)
        attachments.append(att)
      }
    }


    val attAsSet = attachments.toSet

    def getArgs(argObj: ujson.Value): Map[String, Seq[Mention]] = {
      val args = for  {
        (k,v) <- argObj.obj
        seqOfArgMentions = v.arr.map(toMention(_, docMap))

      } yield k -> seqOfArgMentions
      args.toMap
    }

    menType match {
      case "TextBoundMention" =>
        new TextBoundMention(
          labels,
          tokenInterval,
          sentence,
          document,
          keep,
          foundBy,
          attachments = attAsSet
        )
      case "RelationMention" => {
        new RelationMention(
          labels,
          tokenInterval,
          getArgs(mentionComponents("arguments")),
          toPaths(mentionComponents, docMap),
          sentence,
          document,
          keep,
          foundBy,
          attachments = attAsSet
        )

      }
      case "EventMention" => {
        new EventMention(
          labels,
          tokenInterval,
          toMention(mentionComponents("trigger"), docMap).asInstanceOf[TextBoundMention],
          getArgs(mentionComponents("arguments")),
          toPaths(mentionComponents, docMap),
          sentence,
          document,
          keep,
          foundBy,
          attachments = attAsSet
        )
      }
      case "CrossSentenceEventMention" => {
        new CrossSentenceEventMention(
          labels,
          tokenInterval,
          toMention(mentionComponents("trigger"), docMap).asInstanceOf[TextBoundMention],
          getArgs(mentionComponents("arguments")),
          Map.empty[String, Map[Mention, odin.SynPath]],
          sentence,
          sentences,
          document,
          keep,
          foundBy,
          attachments = attAsSet
        )
      }
    }
  }

  def toPaths(mentionJson: ujson.Value, docMap: Map[String, Document]): Map[String, Map[Mention, odin.SynPath]] = {

    /** Create mention from args json for given id */
    def findMention(mentionID: String, json: ujson.Value, docMap: Map[String, Document]): Option[Mention] = {
      mentionJson("arguments") match {
        case ujson.Null => None
        case something =>
          val argsjson = for {
            mnsjson <- something.obj.values
            mjson <- mnsjson.arr
            if mjson("id").str == mentionID
          } yield mjson

          argsjson.toList match {
            case Nil => None
            case j :: _ => Some(toMention(j, docMap))
          }
      }
    }

    // build paths
    if (mentionJson("paths").isNull) {
      Map.empty[String, Map[Mention, odin.SynPath]]
    } else {
      mentionJson("paths") match {
        case ujson.Null => Map.empty[String, Map[Mention, odin.SynPath]]
        case contents => for {
          (argName, innermap) <- contents.obj.toMap
        } yield {
          val pathMap = for {
            (mentionID, pathJSON) <- innermap.obj.toList
            mOp = findMention(mentionID, mentionJson, docMap)
            if mOp.nonEmpty
            m = mOp.get
            edges = pathJSON.arr.map(hop => Edge(hop.obj("source").num.toInt, hop.obj("destination").num.toInt, hop.obj("relation").str))
            synPath: odin.SynPath = DirectedGraph.edgesToTriples(edges)
          } yield m -> synPath
          argName -> pathMap.toMap
        }
      }
    }
  }



  def toAttachment(json: ujson.Value): Attachment = {
    val attType = json("attType").str
    val toReturn = attType match {
      case "MentionLocation" => new MentionLocationAttachment(json("filename").str, json("pageNum").arr.map(_.num.toInt), json("blockIdx").arr.map(_.num.toInt), attType)
      case "DiscontinuousCharOffset" => new DiscontinuousCharOffsetAttachment(json("charOffsets").arr.map(v => (v.arr.head.num.toInt, v.arr.last.num.toInt)), attType)
      case "ParamSetAtt" => new ParamSetAttachment(json("attachedTo").str, attType)
      case "ParamSettingIntervalAtt" => {
        var inclLower: Option[Boolean] = None
        var inclUpper: Option[Boolean] = None
        if (!json("inclusiveLower").isNull) inclLower = Some(json("inclusiveLower").bool)
        if (!json("inclusiveUpper").isNull) inclUpper = Some(json("inclusiveUpper").bool)

        new ParamSettingIntAttachment(inclLower, inclUpper, json("attachedTo").str, attType)
      }

      case "UnitAtt" => new UnitAttachment(json("attachedTo").str, attType)
      case "ContextAtt" => {
        val foundBy = json("foundBy").str
        new ContextAttachment(attType, json("contexts").arr, foundBy)
      }
      case "FunctionAtt" => {
        val foundBy = json("foundBy").str
        val trigger = json("trigger").str
        new FunctionAttachment(attType, trigger, foundBy)
      }
      case _ => ???
    }
    toReturn
  }

  def mkDocumentMap(documentsUJson: ujson.Value): Map[String, Document] = {
    val docHashToDocument = for {
      (k,v) <- documentsUJson.obj
      if !v("sentences").isNull

    } yield k -> toDocument(v)
    docHashToDocument.toMap
  }

  def toDocument(docComponents: ujson.Value): Document = {
    val sentences = docComponents("sentences").arr.map(toSentence(_)).toArray
    val doc = Document(sentences)
    doc.text = Some(docComponents("text").str)
    doc.id = Some(docComponents("id").str)
    doc
  }

  def toSentence(sentComponents: ujson.Value): Sentence = {
    val s = new Sentence(
      sentComponents("raw").arr.map(_.str).toArray,
      sentComponents("startOffsets").arr.map(_.num).map(_.toInt).toArray,
      sentComponents("endOffsets").arr.map(_.num).map(_.toInt).toArray,
      sentComponents("words").arr.map(_.str).toArray,

    )
    s.tags = Some(sentComponents("tags").arr.map(_.str).toArray)
    s.lemmas = Some(sentComponents("lemmas").arr.map(_.str).toArray)
    s.entities = Some(sentComponents("entities").arr.map(_.str).toArray)
    s.norms = Some(sentComponents("norms").arr.map(_.str).toArray)
    s.chunks = Some(sentComponents("chunks").arr.map(_.str).toArray)
    val graphs = sentComponents("graphs").obj.map(item => item._1 -> toDirectedGraph(item._2)).toMap
    s.graphs = GraphMap(graphs)
    s
  }

  def toDirectedGraph(edgesAndRoots: ujson.Value): DirectedGraph[String] = {
    val edges = edgesAndRoots.obj("edges").arr.map(item => new Edge(item.obj("source").num.toInt, item.obj("destination").num.toInt, item.obj("relation").str))
    val roots = edgesAndRoots.obj("roots").arr.map(_.num.toInt).toSet
    new DirectedGraph[String](edges.toList, roots)
  }

  // Serialization
  def serializeMentions(mentions: Seq[Mention]): ujson.Value = {
    val json = ujson.Obj()
    json("mentions") = mentions.map(m => toUJson(m))
    val distinctDocs = mentions.map(_.document).distinct

    val docsAsUjsonObj = ujson.Obj()
    for (doc <- distinctDocs) {
      docsAsUjsonObj(doc.equivalenceHash.toString) = toUJson(doc)
    }
    json("documents") = docsAsUjsonObj
    json
  }

  def toUJson(mention: Mention): ujson.Value = {
    mention match {
      case tb: TextBoundMention => AutomatesTextBoundMentionOps(tb).toUJson//toUJson(tb)
      case rm: RelationMention => AutomatesRelationMentionOps(rm).toUJson
      case em: EventMention => AutomatesEventMentionOps(em).toUJson
      case cm: CrossSentenceEventMention => AutomatesCrossSentenceEventMentionOps(cm).toUJson
      case _ => ???
    }
  }


  def pathsAsUJson(paths: Map[String, Map[Mention, odin.SynPath]]): ujson.Value = paths match {
    case gps if gps.nonEmpty => pathsToUJson(gps)
    case _ => ujson.Null
  }

  def pathsToUJson(paths: Map[String, Map[Mention, odin.SynPath]]): ujson.Value = {
    val simplePathMap: Map[String, Map[String, List[ujson.Value]]] = paths.mapValues{ innermap =>
      val pairs = for {
        (m: Mention, path: odin.SynPath) <- innermap.toList
        edgeUJson = DirectedGraph.triplesToEdges[String](path.toList).map(_.toUJson)
      } yield (m.id, edgeUJson)
      pairs.toMap
    }
    simplePathMap
  }

  implicit class AutomatesEdgeOps(edge: Edge[String]) extends EdgeOps(edge: Edge[String]) {
    def toUJson: ujson.Value = {
      ujson.Obj(
      "source" -> edge.source,
      "destination" -> edge.destination,
      "relation" -> edge.relation.toString
      )
    }
  }


  def toUJson(attachments: Set[Attachment]): ujson.Value = {
    val attsAsUJson = attachments.map(toUJson(_)).toList
    attsAsUJson
  }

  def toUJson(attachment: Attachment): ujson.Value = {
    attachment match {
      case a: MentionLocationAttachment => a.toUJson
      case a: DiscontinuousCharOffsetAttachment => a.toUJson
      case a: ParamSetAttachment => a.toUJson
      case a: ParamSettingIntAttachment => a.toUJson
      case a: UnitAttachment => a.toUJson
      case a: ContextAttachment => a.toUJson
      case a: FunctionAttachment => a.toUJson
      case _ => ???
    }
  }


  def argsToUJson(arguments: Map[String, Seq[Mention]]): ujson.Value = {
    val argsAsUJson = ujson.Obj()
    for (arg <- arguments) {
      argsAsUJson(arg._1) = arg._2.map(toUJson(_)).toList
    }
    argsAsUJson
  }

  def toUJson(document: Document): ujson.Value = {

    val sentencesAsUJson = document.sentences.map(s => toUJson(s)).toList
    ujson.Obj(
      "id" -> document.id.getOrElse("unknownDocument"),
      "text" -> document.text.get,
      "sentences" -> sentencesAsUJson
    )
  }

  def toUJson(s: Sentence): ujson.Value = {
    ujson.Obj(
      "words" -> s.words.toList,
      "startOffsets" -> s.startOffsets.toList,
      "endOffsets" -> s.endOffsets.toList,
      "raw" -> s.raw.toList,
      "tags" -> s.tags.get.toList,
      "lemmas" -> s.lemmas.get.toList,
      "entities" -> s.entities.get.toList,
      "norms" -> s.norms.get.toList,
      "chunks" -> s.chunks.get.toList,
      "graphs" -> s.graphs.toUJson

    )
  }

  implicit class AutomatesGraphMapOps(gm: GraphMap) extends GraphMapOps(gm: GraphMap) {

    def toUJson: ujson.Value = gm.toMap.mapValues(_.toUJson)

  }

  implicit class AutomatesDirectedGraphOps(dg: DirectedGraph[String]) extends DirectedGraphOps(dg: DirectedGraph[String]) {
    def toUJson: ujson.Value = ujson.Obj(
      "edges" -> dg.edges.map(_.toUJson),
      "roots" -> dg.roots
    )
  }

  implicit class AutomatesTextBoundMentionOps(tb: TextBoundMention) extends TextBoundMentionOps(tb: TextBoundMention) {

    def toUJson: ujson.Value = {
      ujson.Obj(
        "id" -> TextBoundMentionOps(tb).id,
        "type" -> "TextBoundMention",
        "text" -> tb.text,
        "labels" -> tb.labels,
        "tokenInterval" -> Map("start" -> tb.tokenInterval.start, "end" -> tb.tokenInterval.end),
        "characterStartOffset" -> tb.startOffset,
        "characterEndOffset" -> tb.endOffset,
        "sentence" -> tb.sentence,
        "document" -> tb.document.equivalenceHash.toString,
        "keep" -> tb.keep,
        "foundBy" -> tb.foundBy,
        "attachments" -> AutomatesJSONSerializer.toUJson(tb.attachments)
      )
    }
  }



  implicit class AutomatesRelationMentionOps(rm: RelationMention) extends RelationMentionOps(rm: RelationMention) {

    def toUJson: ujson.Value = {
      ujson.Obj(
        "type" -> "RelationMention",
        "id" -> RelationMentionOps(rm).id,
        "text" -> rm.text,
        "labels" -> rm.labels,
        "arguments" -> argsToUJson(rm.arguments),
        "paths" -> AutomatesJSONSerializer.pathsAsUJson(rm.paths),
        "tokenInterval" -> Map("start" -> rm.tokenInterval.start, "end" -> rm.tokenInterval.end),
        "characterStartOffset" -> rm.startOffset,
        "characterEndOffset" -> rm.endOffset,
        "sentence" -> rm.sentence,
        "document" -> rm.document.equivalenceHash.toString,
        "keep" -> rm.keep,
        "foundBy" -> rm.foundBy,
        "attachments" -> AutomatesJSONSerializer.toUJson(rm.attachments)
      )
    }
  }

  implicit class AutomatesEventMentionOps(em: EventMention) extends EventMentionOps(em: EventMention) {

    def toUJson: ujson.Value = {
      ujson.Obj(
        "type" -> "EventMention",
        "id" -> EventMentionOps(em).id,
        "text" -> em.text,
        "labels" -> em.labels,
        "trigger" -> AutomatesTextBoundMentionOps(em.trigger).toUJson,
        "arguments" -> argsToUJson(em.arguments),
        "paths" -> AutomatesJSONSerializer.pathsAsUJson(em.paths),
        "tokenInterval" -> Map("start" -> em.tokenInterval.start, "end" -> em.tokenInterval.end),
        "characterStartOffset" -> em.startOffset,
        "characterEndOffset" -> em.endOffset,
        "sentence" -> em.sentence,
        "document" -> em.document.equivalenceHash.toString,
        "keep" -> em.keep,
        "foundBy" -> em.foundBy,
        "attachments" -> AutomatesJSONSerializer.toUJson(em.attachments)
      )
    }
  }

    /** Hash representing the [[Mention.arguments]] */
    private def argsHash(args: Map[String, Seq[Mention]]): Int = {
      val argHashes = for {
        (role, mns) <- args
        bh = stringHash(s"role:$role")
        hs = mns.map(_.equivalenceHash)
      } yield mix(bh, unorderedHash(hs))
      val h0 = stringHash("org.clulab.odin.Mention.arguments")
      finalizeHash(h0, unorderedHash(argHashes))
    }

  implicit class CrossSentenceEventMentionOps(cm: CrossSentenceEventMention) extends JSONSerialization with Equivalency {

    val stringCode = s"org.clulab.aske.automates.mentions.${CrossSentenceEventMention.toString}"

    def equivalenceHash: Int = {
      // the seed (not counted in the length of finalizeHash)
      val h0 = stringHash(stringCode)
      // labels
      val h1 = mix(h0, cm.labels.hashCode)
      // interval.start
      val h2 = mix(h1, cm.tokenInterval.start)
      // interval.end
      val h3 = mix(h2, cm.tokenInterval.end)
      // sentence index
      val h4 = mix(h3, cm.sentence)
      // 2nd sentence index
      val h5 = mix(h4, cm.sentences.hashCode)
      // document.equivalenceHash
      val h6 = mix(h5, cm.document.equivalenceHash)
      // args
      val h7 = mix(h6, argsHash(cm.arguments))
      // trigger
      val h8 = mix(h7, TextBoundMentionOps(cm.trigger).equivalenceHash)
      finalizeHash(h8, 8)
    }

    def jsonAST: JValue = JNull
  }

  implicit class AutomatesCrossSentenceEventMentionOps(cm: CrossSentenceEventMention) extends CrossSentenceEventMentionOps(cm: CrossSentenceEventMention) {

    def toUJson: ujson.Value = {
      ujson.Obj(
        "type" -> "CrossSentenceEventMention",
        "id" -> CrossSentenceEventMentionOps(cm).id,
        "text" -> cm.text,
        "labels" -> cm.labels,
        "trigger" -> AutomatesTextBoundMentionOps(cm.trigger).toUJson,
        "arguments" -> argsToUJson(cm.arguments),
        "paths" -> AutomatesJSONSerializer.pathsAsUJson(cm.paths),
        "tokenInterval" -> Map("start" -> cm.tokenInterval.start, "end" -> cm.tokenInterval.end),
        "characterStartOffset" -> cm.startOffset,
        "characterEndOffset" -> cm.endOffset,
        "sentence" -> cm.sentence,
        "sentences" -> cm.sentences,
        "document" -> cm.document.equivalenceHash.toString,
        "keep" -> cm.keep,
        "foundBy" -> cm.foundBy,
        "attachments" -> AutomatesJSONSerializer.toUJson(cm.attachments)
      )
    }
  }
}