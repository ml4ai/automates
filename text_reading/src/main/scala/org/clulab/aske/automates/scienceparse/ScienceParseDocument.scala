package org.clulab.aske.automates.scienceparse

case class ScienceParseDocument(
  id: String,
  title: Option[String],
  year: Int,
  authors: Vector[Author],
  abstractText: Option[String],
  sections: Vector[Section],
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
