package org.clulab.aske.automates.grfn

case class GrFNDocument (
  functions: Vector[GrFNFunction],
  start: String,
  name: String,
  dateCreated: String)

case class GrFNFunction(
  name: String,
  functionType: String,
  sources: Option[Vector[GrFNSource]],
  body: Option[Vector[GrFNBody]],
  target: String,
  input: Option[Vector[GrFNVariable]],
  variables: Option[Vector[GrFNVariable]]
)

case class GrFNSource(
  name: String,
  sourceType: String
)

case class GrFNBody(
  bodyType: Option[String],
  name: String,
  reference: Option[Int],
  input: Option[],
  output: Option[]
)

case class GrFNVariable(
  name: String,
  domain: String
)

case class GrFNIO(
  name: String,
  index: Int
)