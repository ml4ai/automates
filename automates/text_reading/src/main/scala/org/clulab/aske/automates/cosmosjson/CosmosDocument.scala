package org.clulab.aske.automates.cosmosjson
import ujson.Value

case class CosmosDocument(
                                 cosmosOjects: Seq[CosmosObject]
                               )


case class CosmosObject(
                       pdfName: Option[String],
                       pageNum: Option[Int],
                       blockIdx: Option[Int],
                       content: Option[String],
                       cls: Option[String], //postprocess_cls (class)
                       postprocessScore: Option[Double],
                       detect_cls: Option[String]
                       )
case class Author(
                   name: String,
                   affiliations: Vector[String]
                 )

case class Section(
                    headingAndText: String
                  )

case class Reference(
                      title: String,
                      authors: Vector[String],
                      venue: Option[String],
                      year: Option[Int]
                    )
