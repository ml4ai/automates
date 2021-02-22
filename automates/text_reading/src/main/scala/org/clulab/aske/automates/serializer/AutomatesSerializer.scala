package org.clulab.aske.automates.serializer

import org.clulab.aske.automates.attachments.MentionLocationAttachment
import org.clulab.odin
import org.clulab.odin.{Attachment, EventMention, Mention, RelationMention, TextBoundMention}
import org.clulab.processors.{Document, Sentence}
import org.clulab.struct.{DirectedGraph, Edge, GraphMap, Interval}
import org.clulab.odin.serialization.json._
import org.clulab.serialization.json.{DirectedGraphOps, EdgeOps, GraphMapOps}

import scala.collection.mutable.ArrayBuffer

object AutomatesJSONSerializer {

  // This is a ujson adaptation of org.clulab.odin.serialization.json.JSONSerializer

  // Deserializing mentions
  def toMentions(menUJson: ujson.Value): Seq[Mention] = {

    require(!menUJson("mentions").isNull, "\"mentions\" key missing from json")
    require(!menUJson("documents").isNull, "\"documents\" key missing from json")

    val docMap = mkDocumentMap(menUJson("documents"))
    val mentionsUJson = menUJson("mentions")
    val toReturn = mentionsUJson.arr.map(item => toMention(item, docMap)).toSeq
    toReturn

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
    val attachments = new ArrayBuffer[Attachment]

    if (mentionComponents.obj.keys.toList.contains("attachments")) {
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



  def toAttachment(json: ujson.Value): Attachment = {
    val attType = json("attType").str
    val toReturn = attType match {
      case "mentionLocation" => new MentionLocationAttachment(json("pageNum").num.toInt, json("blockIdx").num.toInt, attType)
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
      "id" -> document.id.get,
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
        "foundBy" -> tb.foundBy
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


}