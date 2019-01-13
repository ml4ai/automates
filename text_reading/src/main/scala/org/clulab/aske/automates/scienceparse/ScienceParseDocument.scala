package org.clulab.aske.automates.scienceparse

case class ScienceParseDocument(
  id: String,
  title: Option[String],
  year: Int,
  authors: Vector[Author],
  abstractText: String,
  sections: Vector[Section],
  references: Vector[Reference]
)

case class Author(
  name: String,
  affiliations: Vector[String]
)

case class Section(
  heading: Option[String],
  text: String
)

case class Reference(
  title: String,
  authors: Vector[String],
  venue: Option[String],
  year: Int
)
