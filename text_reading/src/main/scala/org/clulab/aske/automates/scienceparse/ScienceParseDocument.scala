package org.clulab.aske.automates.scienceparse

import ujson.Value

case class ScienceParseDocument(
  id: String,
  title: Option[String],
  year: Option[Value],
  authors: Vector[Author],
  abstractText: Option[String],
  sections: Option[Vector[Section]],
  references: Vector[Reference]
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
