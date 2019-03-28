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

case class ValueList(
  values: List[Option[Quantity]],
  quantified: Option[Quantified]
) extends Measurement

case class Quantity(
  rawValue: String,
  parsedValue: Option[Double],
  normalizedValue: Option[Double],
  rawUnit: Option[UnitOfMeasurement],
  normalizedUnit: Option[UnitOfMeasurement],
  offset: Offset
)

case class Offset(
  start: Int,
  end: Int
)

case class UnitOfMeasurement(
  name: String,
  unitType: Option[String],
  system: Option[String],
  offset: Option[Offset]
)

case class Quantified(
  rawName: String,
  normalizedName: String,
  offset: Offset
)
