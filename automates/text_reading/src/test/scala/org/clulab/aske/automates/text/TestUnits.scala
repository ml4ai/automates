package org.clulab.aske.automates.text

import org.clulab.aske.automates.TestUtils._

class TestUnits extends ExtractionTest {

//todo: these tests are only here for the purpose of testing if the rules are extracting what they should; ultimately, they should be checking if the units are attached to variables themselves and not to the concepts/descriptions of variables

  val t1a = "The (average) daily net radiation expressed in megajoules per square metre per day (MJ m-2 day-1) is required."
  passingTest should s"extract variables and units from t1a: ${t1a}" taggedAs(Somebody) in {
    val desired = Seq(
      "daily net radiation" -> Seq("MJ m-2 day-1")
    )
    val mentions = extractMentions(t1a)
    testUnitEvent(mentions, desired)
  }

  val t2a = "Wind speed is given in metres per second (m s-1) or kilometres per day (km day-1)."
  passingTest should s"extract variables and units from t2a: ${t2a}" taggedAs(Somebody) in {
    val desired = Seq(
      "Wind speed" -> Seq("m s-1", "km day-1")
    )
    val mentions = extractMentions(t2a)
    testUnitEvent(mentions, desired)
  }

  val t3a = "a hypothetical crop with an assumed height of 0.12 m, with a surface resistance of 70 s m-1 and an albedo of 0.23"
  passingTest should s"extract variables and units from t3a: ${t3a}" taggedAs(Somebody) in {
    val desired = Seq(
      "assumed height" -> Seq("m"), //todo: `exclude assumed'?
      "surface resistance" -> Seq("s m-1")
    )
    val mentions = extractMentions(t3a)
    testUnitEvent(mentions, desired)
  }

  val t4a = "In one type, water uptake is a function of the difference in water potentials ( , J kg−1) and the conductances (C, kg s m−4) between adjacent components in the soil–plant system."
  passingTest should s"extract variables and units from t4a: ${t4a}" taggedAs(Somebody) in {
    val desired = Seq(
      "water potentials" -> Seq("J kg−1"),
      "conductances" -> Seq("kg s m−4")
    )
    val mentions = extractMentions(t4a)
    testUnitEvent(mentions, desired)
  }

  val t5a = "T = daily mean air temperature [°C]"
  passingTest should s"extract variables and units from t5a: ${t5a}" taggedAs(Somebody) in {
    val desired = Seq(
      "T" -> Seq("°C")
    )
    val mentions = extractMentions(t5a)
    testUnitEvent(mentions, desired)
  }

  val t6a = "The following values are often used: apsy = 0.000662 for ventilated (Asmann type) psychrometers having air movement between 2 and 10 m s-1 for Twet ≥ 0 and 0.000594 for Twet < 0, = 0.000800 for naturally ventilated psychrometers having air movement of about 1 m s-1, and = 0.001200 for non-ventilated psychrometers installed in glass or plastic greenhouses."
  passingTest should s"extract variables and units from t6a: ${t6a}" taggedAs(Somebody) in {
    val desired = Seq(
      "air movement" -> Seq("m s-1"),
      "air movement" -> Seq("m s-1")
    )
    val mentions = extractMentions(t6a)
    testUnitEvent(mentions, desired)
  }

  val t7a = "soil layer thickness ($z, m), the water uptake from previous soil layers (uk, mm d−1)"
  passingTest should s"extract variables and units from t7a: ${t7a}" taggedAs(Somebody) in {
    val desired = Seq(
      "soil layer thickness" -> Seq("m"),
      "previous soil layers" -> Seq("mm d−1") //todo: lose `previous'?

    )
    val mentions = extractMentions(t7a)
    testUnitEvent(mentions, desired)
  }

  //todo: check source of this example
  val t8a = "The density of water (ρw) is taken as 1.0 Mg m-3."
  passingTest should s"extract variables and units from t8a: ${t8a}" taggedAs(Somebody) in {
    val desired = Seq(
      "ρw" -> Seq("Mg m-3")

    )
    val mentions = extractMentions(t8a)
    testUnitEvent(mentions, desired)
  }


}
