package org.clulab.aske.automates.text

import org.clulab.aske.automates.TestUtils._

class TestUnits extends ExtractionTest {

  val t1a = "The (average) daily net radiation expressed in megajoules per square metre per day (MJ m-2 day-1) is required."
  passingTest should s"extract variables and units from t1a: ${t1a}" taggedAs(Somebody) in {
    val desired = Seq(
      "(average) daily net radiation" -> Seq("MJ m-2 day-1")
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
      "density of water" -> Seq("Mg m-3") // `density of water` is likely preferred over pw because of the keep longest action; this is an acceptable result

    )
    val mentions = extractMentions(t8a)
    testUnitEvent(mentions, desired)
  }

  // supermaas papers
  val t9a = "Figure 2 : Performance of the fababean module ( observed versus simulated grain yield in g / m2 ) against test datasets reported by Turpin et al. ( 2003 ) ."
  failingTest should s"extract variables and units from t9a: ${t9a}" taggedAs(Somebody) in {
    val desired = Seq(
      "grain yield" -> Seq("g / m2")
    )
    val mentions = extractMentions(t9a)
    testUnitEvent(mentions, desired)
  }

  val t10a = "Maximum specific leaf area ( sla_max ) defines the maximum leaf area ( m 2 ) that can be expanded per gram of biomass ."
  passingTest should s"extract variables and units from t10a: ${t10a}" taggedAs(Somebody) in {
    val desired = Seq(
      "Maximum specific leaf area" -> Seq("m 2") // ideally `sla_max` but works for our purposes since we can align to identifier through concept
    )
    val mentions = extractMentions(t10a)
    testUnitEvent(mentions, desired)
  }

  val t11a = "The phase is comprised of an initial period of fixed thermal time during which shoot elongation is slow ( the \"lag\" phase) and a linear period , where the rate of shoot elongation towards the soil surface is linearly related to air temperature ( measured in o Cd mm -1 ) ."
  failingTest should s"extract variables and units from t11a: ${t11a}" taggedAs(Somebody) in {
    val desired = Seq(
      "rate of shoot elongation towards the soil surface" -> Seq("o Cd mm -1")
    )
    val mentions = extractMentions(t11a)
    testUnitEvent(mentions, desired)
  }

  val t12a = "It shows that the pasture is not harvested before 1/07/1995 , the harvest frequency is once every 21 days and the harvest residual is 1250 kg / ha ."
  failingTest should s"extract variables and units from t12a: ${t12a}" taggedAs(Somebody) in {
    val desired = Seq(
      "harvest residual" -> Seq("kg / ha")
    )
    val mentions = extractMentions(t12a)
    testUnitEvent(mentions, desired)
  }

  val t13a = "For the purposes of model parameterisation the value of shoot_lag has been assumed to be around 40 o Cd."
  failingTest should s"extract variables and units from t13a: ${t13a}" taggedAs(Somebody) in {
    val desired = Seq(
      "shoot_lag" -> Seq("o Cd")
    )
    val mentions = extractMentions(t13a)
    testUnitEvent(mentions, desired)
  }

  val t14a = "This means that at a sowing depth of 4 cm emergence occurs..."
  failingTest should s"extract variables and units from t14a: ${t14a}" taggedAs(Somebody) in {
    val desired = Seq(
      "sowing depth" -> Seq("cm")
    )
    val mentions = extractMentions(t14a)
    testUnitEvent(mentions, desired)
  }

  val t15a = "Root biomass is converted to root length using the parameter specific_root_length ( currently assumed as 60000 mm / g for all species ) ."
  failingTest should s"extract variables and units from t15a: ${t15a}" taggedAs(Somebody) in {
    val desired = Seq(
      "specific_root_length" -> Seq("mm / g")
    )
    val mentions = extractMentions(t15a)
    testUnitEvent(mentions, desired)
  }

}


