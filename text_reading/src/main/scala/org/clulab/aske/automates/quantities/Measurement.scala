package org.clulab.aske.automates.quantities

sealed trait Measurement

case class Value(
  quantity: Quantity,
  quantified: Option[Quantified]
) extends Measurement

case class Interval(
  quantityLeast: Option[Quantity],
  quantityMost: Option[Quantity]
) extends Measurement

case class Quantity(
  rawValue: String,
  parsedValue: Double,
  normalizedValue: Option[Double],
  rawUnit: Option[Unit],
  normalizedUnit: Option[Unit],
  offset: Offset
)

case class Offset(
  start: Int,
  end: Int
)

case class Unit(
  name: String,
  unitType: String,
  system: String,
  offset: Option[Offset]
)

case class Quantified(
  rawName: String,
  normalizedName: String,
  offset: Offset
)
