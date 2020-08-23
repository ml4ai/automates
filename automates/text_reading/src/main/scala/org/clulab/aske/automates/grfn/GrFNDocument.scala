package org.clulab.aske.automates.grfn

import upickle.default._
import upickle.default.{ReadWriter => RW, macroRW}

case class GrFNDocument (
  functions: Vector[GrFNFunction],
  start: String,
  name: Option[String],
  dateCreated: String,
  variables: Option[Seq[GrFNVariable]],
  alignments: Option[Seq[GrFNAlignment]]
)
object GrFNDocument {
  implicit val rw: RW[GrFNDocument] = macroRW

  def getVariables(grfnDocument: GrFNDocument): Seq[GrFNVariable] = {
    val variables = for {
      f <- grfnDocument.functions
      vs <- f.variables
    } yield vs
    variables.flatten
  }
}

case class GrFNFunction(
  name: String,
  functionType: Option[String],
  sources: Option[Vector[GrFNSource]],
  body: Option[Vector[GrFNBody]],
  target: Option[String],
  input: Option[Vector[GrFNVariable]],
  variables: Option[Vector[GrFNVariable]]
)
object GrFNFunction {implicit val rw: RW[GrFNFunction] = macroRW}

case class GrFNSource(
  name: String,
  sourceType: String
)
object GrFNSource {implicit val rw: RW[GrFNSource] = macroRW}

// fixme
case class GrFNBody(
  bodyType: Option[String],
  name: String,
  reference: Option[Int],
  //input: Option[], // fixme
  //output: Option[]
)
object GrFNBody {implicit val rw: RW[GrFNBody] = macroRW}

case class GrFNVariable(
  name: String,
  domain: String,
  description: Option[GrFNProvenance]
)
object GrFNVariable {implicit val rw: RW[GrFNVariable] = macroRW}

case class GrFNIO(
  name: String,
  index: Int
)
object GrFNIO {implicit val rw: RW[GrFNIO] = macroRW}

case class GrFNProvenance(
  text: String,
  source: String,
  sentIdx: Int
)
object GrFNProvenance {implicit val rw: RW[GrFNProvenance] = macroRW}

case class GrFNAlignment(
  src: String,
  dst: String,
  score: Double
)
object GrFNAlignment {implicit val rw: RW[GrFNAlignment] = macroRW}
