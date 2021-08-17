package org.clulab.aske.automates.text

import org.clulab.aske.automates.TestUtils._

class TestParameterSettingEventInterval  extends ExtractionTest {

  // Tests from paper: 2017-IMPLEMENTING STANDARDIZED REFERENCE EVAPOTRANSPIRATION AND DUAL CROP COEFFICIENT APPROACH IN THE DSSAT CROPPING SYSTEM MODEL

  val t1a = "If E and T data are unavailable, values of SKc from 0.5 to 0.7 are recommended and values of Kc from 0.3 to 0.9."
  passingTest should s"extract the parameter setting(s) from t13a: ${t1a}" taggedAs(Somebody, Interval) in {

    val desired = Seq(
      "SKc" -> Seq("0.5", "0.7"),
      "Kc" -> Seq("0.3", "0.9") //this second arg is a toy example
    )

    val mentions = extractMentions(t1a)
    testParameterSettingEventInterval(mentions, desired)
  }

  val t2a = "The value of SKc was varied between 0.4 and 0.9 with a base level of 0.5 for maize and 0.6 for cotton from prior calibration efforts."
  passingTest should s"extract the parameter setting(s) from t2a: ${t2a}" taggedAs(Somebody, Interval) in {

    val desired = Seq(
      "SKc" -> Seq("0.4", "0.9")
    )

    val mentions = extractMentions(t2a)
    testParameterSettingEventInterval(mentions, desired)
  }

  val t3a = "where KEP (typically ranging from 0.5 to 0.8) is defined as an energy extinction coefficient of the canopy for total solar irradiance"
  passingTest should s"extract the parameter setting(s) from t3a: ${t3a}" taggedAs(Somebody, Interval) in {

    val desired = Seq(
      "KEP" -> Seq("0.5", "0.8")
    )

    val mentions = extractMentions(t3a)
    testParameterSettingEventInterval(mentions, desired)
  }

  val t4a = "Under full irrigation, Kcbmax with the ETo-Kcb method had little influence on maize and cotton yield " +
    "for 0.9 < Kcbmax < 1.15, but simulated yield decreased rapidly for Kcbmin > 1.15 (fig. 6a)."
  passingTest should s"extract the parameter setting(s) from t4a and NOT extract the figure number: ${t4a}" taggedAs(Somebody, Interval) in {
    val desired = Seq(
            "Kcbmax" -> Seq("0.9", "1.15"),
            "Kcbmin" -> Seq("1.15", "") //todo: need to have some mechanism to preserve ><=. some sort of attachment? similar to count in wm or use 'valueMin'/'valueMax' for the var
    )
    val mentions = extractMentions(t4a)

    testParameterSettingEventInterval(mentions, desired)
  }

  // SuperMaaS papers tests
  val t1b = "Vernalisation is simulated from daily average crown temperature and daily maximum and minimum temperatures using the original CERES can occur if daily maximum temperature is above 30 o C."
  passingTest should s"extract the parameter setting(s) from t1b: ${t1b}" taggedAs(Somebody, Interval) in {
    val desired = Seq(
      "daily maximum temperature" -> Seq("30", "")
    )
    val mentions = extractMentions(t1b)
    testParameterSettingEventInterval(mentions, desired)
  }

  val t2b = "The duration of grain filling ( tt_startgf_to_mat ) is cultivar specific and usually lies between 500 and 800 o C days ."
  passingTest should s"extract the parameter setting(s) from t2b: ${t2b}" taggedAs(Somebody, Interval) in {
    val desired = Seq(
      "duration of grain filling" -> Seq("500", "800")
    )
    val mentions = extractMentions(t2b)
    testParameterSettingEventInterval(mentions, desired)
  }

  val t3b = "It is assumed that leaf expansion growth is reduced when the supply / demand ratio for water is below 1.1 and stops when supply / demand ratio reaches 0.1 ."
  passingTest should s"extract the parameter setting(s) from t3b: ${t3b}" taggedAs(Somebody, Interval) in {
    val desired = Seq(
      "supply / demand ratio for water" -> Seq("", "1.1")
    )
    val mentions = extractMentions(t3b)
    testParameterSettingEventInterval(mentions, desired)
  }

  val t4b = "The current model specifies sla_max as varying from 27 000 to 22000 mm 2 g -1 t o constrain daily leaf area increase where carbon is limiting ."
  passingTest should s"extract the parameter setting(s) from t4b: ${t4b}" taggedAs(Somebody, Interval) in {
    val desired = Seq(
      "sla_max" -> Seq("22000", "27 000")
    )
    val mentions = extractMentions(t4b)
    testParameterSettingEventInterval(mentions, desired)
  }

  val t5b = "ratio_root_shoot is specified for each growth stage , and varies from 1.0 at emergence , to 0.09 at flowering ."
  passingTest should s"extract the parameter setting(s) from t5b: ${t5b}" taggedAs(Somebody, Interval) in {
    val desired = Seq(
      "ratio_root_shoot" -> Seq("0.09", "1.0")
    )
    val mentions = extractMentions(t5b)
    testParameterSettingEventInterval(mentions, desired)
  }

  val t6b = "Senescence due to frost commences when temperatures decrease below -5 o C."
  passingTest should s"extract the parameter setting(s) from t6b: ${t6b}" taggedAs(Somebody, Interval) in {
    val desired = Seq(
      "temperatures" -> Seq("", "-5")
    )
    val mentions = extractMentions(t6b)
    testParameterSettingEventInterval(mentions, desired)
  }

  val t7b = "Above an LAI of 4.0 light competition causes leaf area to be lost ."
  failingTest should s"extract the parameter setting(s) from t7b: ${t7b}" taggedAs(Somebody, Interval) in {
    val desired = Seq(
      "LAI" -> Seq("4.0", "")
    )
    val mentions = extractMentions(t7b)
    testParameterSettingEventInterval(mentions, desired)
  }

  val t8b = "Regrowth is ensured if the parameter min_tpla is set to a value greater than zero ."
  failingTest should s"extract the parameter setting(s) from t8b: ${t8b}" taggedAs(Somebody, Interval) in {
    val desired = Seq(
      "min_tpla" -> Seq("0", "")
    )
    val mentions = extractMentions(t8b)
    testParameterSettingEventInterval(mentions, desired)
  }

  //
//  // Tests from paper: 2005-THE ASCE STANDARDIZED REFERENCE EVAPOTRANSPIRATION EQUATION
//  val t1b = "Rns and Rnl are generally positive or zero in value."
//  failingTest should s"extract the parameter setting(s) from t3a: ${t3a}" taggedAs(Somebody, Interval) in {
//
//    val desired = Seq(
//      "KEP" -> Seq("0", "0.8") //todo: need a rule for "range from"
//    )
//
//    val mentions = extractMentions(t3a)
//    testParameterSettingEventInterval(mentions, desired)
//  }


  // supermaas test todo:
//  The kl factor is empirically derived , incorporating both plant and soil factors which limit rate of water uptake - it represents the fraction of available soil water that can potentially be taken up on that day from that layer , and values typically vary between 0.01 for deep layers with low root length densities to 0.10 for surface layers with high root length densities do layer = 1 , deepest_layer ( do loop to calculate available water for all layers ) sw_avail = sw ( layer ) - ll = sw_avail * kl ( layer ) Soil water demand is calculated as in the ' biomass accumulation ' section above where potential biomass production is a function of radiation interception and rue .
}
