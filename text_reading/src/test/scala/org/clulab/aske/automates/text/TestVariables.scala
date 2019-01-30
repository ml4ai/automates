package org.clulab.aske.automates.text

import org.clulab.aske.automates.TestUtils.{ExtractionTest, Somebody}
import org.clulab.aske.automates.OdinEngine.VARIABLE_LABEL

class TestVariables extends ExtractionTest {

  passingTest should "find variables SIMPLE" in {
    val text = "where Kcdmin is the minimum crop coefficient"

    val desired = Seq("Kcdmin")
    val mentions = extractMentions(text)
    testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }

  passingTest should "find variables 1" in {
    val text = "where Kcdmin is the minimum crop coefficient or Kcd at LAI = 0, Kcdmax is the maximum crop " +
      "coefficient at high LAI, and SKc is a shaping parameter that determines the shape of the Kcd versus LAI curve."

    val desired = Seq("Kcdmin", "Kcd", "LAI", "Kcdmax", "LAI", "SKc", "Kcd", "LAI")
    val mentions = extractMentions(text)
    testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }

  //
  // sentences from 2017-IMPLEMENTING STANDARDIZED REFERENCE EVAPOTRANSPIRATION AND DUAL CROP COEFFICIENT APPROACH IN THE DSSAT CROPPING SYSTEM MODEL
  //

  passingTest should "find variables 2" in {
    val text = "Crop coefficients (Kcs) are calculated for the current Penman-Monteith ET approach in DSSAT-CSM as:"
    // TODO:  Is Penman-Monteith part of the variable? Is DSSAT-CSM a variable?
    val desired = Seq("Kcs", "ET", "DSSAT-CSM")
    val mentions = extractMentions(text)
    testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }

  passingTest should "find variables 3" in {
    val text = "where LAI is the simulated leaf area index, EORATIO is defined as the maximum Kcs at LAI = 6.0 (Sau et al., 2004; Thorp et al., 2010), and Kcs is the DSSAT-CSM crop coefficient. "
    // TODO:  Is DSSAT-CSM a variable?
    val desired = Seq("LAI", "EORATIO", "Kcs", "LAI", "Kcs", "DSSAT-CSM")
    val mentions = extractMentions(text)
    testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }

  passingTest should "find variables 4" in {
    val text = "where Kcdmin is the minimum crop coefficient or Kcd at LAI = 0, Kcdmax is the maximum crop coefficient at high LAI, and SKc is a shaping parameter that determines the shape of the Kcd versus LAI curve."

    val desired = Seq("Kcdmin", "Kcd", "LAI", "Kcdmax", "LAI", "SKc", "Kcd", "LAI")
    val mentions = extractMentions(text)
    testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }

  passingTest should "find variables 5" in {
    val text = "DSSAT-CSM employs the following formula for calculation of E0 (potential crop ET):"

    val desired = Seq("DSSAT-CSM", "E0", "ET")
    val mentions = extractMentions(text)
    testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }

  passingTest should "find variables 6" in {
    val text = "E0 is then partitioned into potential plant transpiration (EPo) and potential soil water evaporation (ESo):"

    val desired = Seq("E0", "EPo", "ESo")
    val mentions = extractMentions(text)
    testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }

  passingTest should "find variables 7" in {
    val text = "The ESo calculation in equation 4 is implemented for the CSM-CERESMaize model and several other crop models."

    val desired = Seq("ESo", "CSM_CERESMaize")
    val mentions = extractMentions(text)
    testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }

  passingTest should "find variables 8" in {
    val text = "Similar to equation 2, E0 is calculated as the product of Kcd and ETpm."

    val desired = Seq("E0", "Kcd", "ETpm")
    val mentions = extractMentions(text)
    testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }

  passingTest should "find variables 9" in {
    val text = " The primary factor causing an increase in the crop coefficient is an increase in plant cover or leaf area (Jensen and Allen, 2016); thus, Kc is correlated with LAI."

    val desired = Seq("Kc", "LAI")
    val mentions = extractMentions(text)
    testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }

  passingTest should "find variables 10" in {
    val text = "Recommended values for Kcdmin and Kcdmax can be found in FAO-56, and DeJonge et al. (2012a) recommended 0.5 < SKc < 1.0 as a typical shape to match past literature on the subject."

    val desired = Seq("Kcdmin", "Kcdmax", "FAO-56", "SKc")
    val mentions = extractMentions(text)
    testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }

  passingTest should "find variables 11" in {
    val text ="where KEP (typically ranging from 0.5 to 0.8) is defined as an energy extinction coefficient of the canopy for total solar irradiance, used for partitioning E0 to EPo and ESo (Ritchie, 1998)."

    val desired = Seq("KEP", "E0", "EPo", "ESo")
    val mentions = extractMentions(text)
    testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }

  passingTest should "find variables 12" in {
    val text = "Note that Kcdmax in equation 5 is different from Kcmax in equation A6."

    val desired = Seq("Kcdmax", "Kcmax")
    val mentions = extractMentions(text)
    testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }

  passingTest should "find variables 13" in {
    val text = "where Kcbmin is the minimum basal crop coefficient representing a dry, bare, or nearly bare soil surface."

    val desired = Seq("Kcbmin")
    val mentions = extractMentions(text)
    testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }

  passingTest should "find variables 14" in {
    val text = "The approach uses model-simulated LAI to calculate the Kcb, which means Kcb is more dynamic and responsive to cultivar, weather, and soil variability, as simulated by the model"

    val desired = Seq("LAI", "Kcb", "Kcb")
    val mentions = extractMentions(text)
    testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }

  passingTest should "find variables 15" in {
    val text = "Because the aim of equation 8 is potential soil evaporation, Ke is obtained from equation A5 with Kr = 1.0."

    val desired = Seq("Ke", "Kr")
    val mentions = extractMentions(text)
    testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }

  //
  // sentences from 2016-Camargo-and Kemanian-Six-crop-models differ-in-their-simulation-of water-uptake
  //

  passingTest should "find variables 1b" in {
    val text = "In APSIM, water uptake (Ta, mm d−1) is determined from potential transpiration demand (Tp, mm d−1), soil water available (WA, mm d−1), and water supply (WS, mm d−1) for each ith day and soil layer as:"
    // TODO:  Is APSIM a variable or the name of a model?
    val desired = Seq("APSIM", "Ta", "Tp", "WA", "WS")
    val mentions = extractMentions(text)
    testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }

  passingTest should "find variables 2b" in {
    val text = "where fi is the daily fractional light interception, ETo is the daily reference evapotranspiration (mm d−1), pwp is the water content at permanent wilting point (m3 m−3), $z is the soil layer thickness (m), and kl is the water extraction rate, an empiric soil–root factor for the fraction of available water that can be supplied to the plant from each rooted soil layer."

    val desired = Seq("fi", "ETo", "pwp", "$z", "kl")
    val mentions = extractMentions(text)
    testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }

  passingTest should "find variables 3b" in {
    val text = "This means that kl represents a maximum supply determined by !r and the resistance to water flow (Passioura, 1983; Monteith, 1986)"

    val desired = Seq("kl", "!r")
    val mentions = extractMentions(text)
    testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }

  passingTest should "find variables 4b" in {
    val text = "The plant conductance is calculated by inverting the transpiration equation using a maximum expected transpiration (Tx, mm d−1), the soil water potential at field capacity ( Sfc, J kg−1) and the leaf water potential at the onset of stomatal closure ( Lsc, J kg−1):"

    val desired = Seq("Tx", "Sfc", "Lsc")
    val mentions = extractMentions(text)
    testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }

  passingTest should "find variables 5b" in {
    val text = "The average soil water potential ( ̄S , J kg−1) is calculated based on a representative root length fraction for each soil layer (fr,j):"
    // TODO:  What is (fr,j) ?
    val desired = Seq("S", "(fr,j)")
    val mentions = extractMentions(text)
    testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }


  // NEW FORMAT

  val t6b = "The L is calculated using T, Cp and  ̄S ."
  passingTest should "extract variables from t6b" taggedAs(Somebody) in {
    val desired = Seq("L", "T", "Cp", "S")
    val mentions = extractMentions(t6b)
    testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }

  val t7b = "If L falls below that of permanent wilting point ( Lpwp), then Ta = 0"
  passingTest should "extract variables from t7b" taggedAs(Somebody) in {
    val desired = Seq("L", "Lpwp", "Ta")
    val mentions = extractMentions(t7b)
    testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }

  val t8b = "Finally, Ta is calculated using s and L, Cp and Tp:"
  passingTest should "extract variables from t8b" taggedAs(Somebody) in {
    val desired = Seq("Ta", "s", "L", "Cp", "Tp")
    val mentions = extractMentions(t8b)
    testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }

  val t9b = "For this research Tx = 10 mm d−1, Lsc = −1100 J kg−1 and Lpwp = −2000 J kg−1."
  passingTest should "extract variables from t9b" taggedAs(Somebody) in {
    val desired = Seq("Tx", "Lsc", "Lpwp")
    val mentions = extractMentions(t9b)
    testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }

  val t10b = "In DSSAT, root water uptake is calculated in two steps."
  passingTest should "extract variables from t10b" taggedAs(Somebody) in {
    // TODO: Is DSSAT a variable?
    val desired = Seq("DSSAT")
    val mentions = extractMentions(t10b)
    testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }

  val t11b = "First, water uptake per unit of root length is computed in each soil layer (Url, m3 m−1 d−1) as an exponential function that depends on:"
  passingTest should "extract variables from t11b" taggedAs(Somebody) in {
    val desired = Seq("Url")
    val mentions = extractMentions(t11b)
    testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }

  val t12b = "Second, the maximum potential water uptake for the profile (Ux, mm d−1) is obtained by multiplying Ta,rl times !r for each layer and summing over the soil profile:"
  passingTest should "extract variables from t12b" taggedAs(Somebody) in {
    // TODO:  Ta, rl, !r ??
    val desired = Seq("Ux", "Ta", "rl", "!r")
    val mentions = extractMentions(t12b)
    testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }

  val t13b = "where s1 and s2 are parameters of a logistic curve (9 and 0.005, respectively), and w represents the soil limitation to water uptake of each layer."
  passingTest should "extract variables from t13b" taggedAs(Somebody) in {
    val desired = Seq("s1", "s2", "w")
    val mentions = extractMentions(t13b)
    testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }


  // sentences from 2013-Quantifying the Influence of Climate on Human Conflict_Burke-Science

  val t1c = "where locations are indexed by i, observational periods are indexed by t, b is the parameter of interest, and ∈ is the error."
  passingTest should "extract variables from t1c" taggedAs(Somebody) in {
    // TODO:  deal with "∈" somehow ?
    val desired = Seq("i", "t", "b", "∈")
    val mentions = extractMentions(t1c)
    testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }


  // sentences from 2006-Root Water Extraction and Limiting Soil Hydraulic Conditions Estimated by Numerical Simulation

  val tX = ""
  passingTest should "extract variables from tX" taggedAs(Somebody) in {
    val desired = Seq()
    val mentions = extractMentions(tX)
    testTextBoundMention(mentions, VARIABLE_LABEL, desired)
  }

}
