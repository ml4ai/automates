package org.clulab.aske.automates.text

import org.clulab.aske.automates.TestUtils.ExtractionTest

class TestDefinitions extends ExtractionTest {

  passingTest should "find definitions 1" in {

    val text = "where Kcdmin is the minimum crop coefficient or Kcd at LAI = 0, Kcdmax is the maximum crop " +
      "coefficient at high LAI, and SKc is a shaping parameter that determines the shape of the Kcd versus LAI curve."

    val desired = Map(
      "Kcdmin" -> Seq("minimum crop coefficient"),
      "Kcdmax" -> Seq("maximum crop coefficient"), // Seq("maximum crop coefficient at high LAI"), fixme?
      "SKc" -> Seq("shaping parameter")
    )
    val mentions = extractMentions(text)
    testDefinitionEvent(mentions, desired)

  }

  // Tests from paper: 2017-IMPLEMENTING STANDARDIZED REFERENCE EVAPOTRANSPIRATION AND DUAL CROP COEFFICIENT APPROACH IN THE DSSAT CROPPING SYSTEM MODEL

  val t1 = "Crop coefficients (Kcs) are calculated for the current Penman-Monteith ET approach in DSSAT-CSM as:"

  val t2 = "where LAI is the simulated leaf area index, EORATIO is defined as the maximum Kcs at LAI = 6.0 " +
    "(Sau et al., 2004; Thorp et al., 2010), and Kcs is the DSSAT-CSM crop coefficient."

  val t3 = "where Kcdmin is the minimum crop coefficient or Kcd at LAI = 0, Kcdmax is the maximum crop coefficient " +
    "at high LAI, and SKc is a shaping parameter that determines the shape of the Kcd versus LAI curve."

  val t4 = "DSSAT-CSM employs the following formula for calculation of E0 (potential crop ET):"

  val t5 = "The ESo calculation in equation 4 is implemented for the CSM-CERESMaize model and several other crop models."

  val t6 = "Similar to equation 2, E0 is calculated as the product of Kcd and ETpm."

  // Tests from paper: 2016-Camargo-and Kemanian-Six-crop-models differ-in-their-simulation-of water-uptake

  val t7 = "In APSIM, water uptake (Ta, mm d−1) is determined from potential transpiration demand (Tp, mm d−1), soil " +
    "water available (WA, mm d−1), and water supply (WS, mm d−1) for each ith day and soil layer as:"

  val t8 = "where fi is the daily fractional light interception, ETo is the daily reference evapotranspiration (mm d−1)," +
    " \\\"pwp is the water content at permanent wilting point (m3 m−3), $z is the soil layer thickness (m), and kl " +
    "is the water extraction rate, an empiric soil–root factor for the fraction of available water that can be " +
    "supplied to the plant from each rooted soil layer."

  val t9 = "This means that kl represents a maximum supply determined by !r and the resistance to water flow " +
    "(Passioura, 1983; Monteith, 1986)"

  val t10 = "The plant conductance is calculated by inverting the transpiration equation using a maximum expected " +
    "transpiration (Tx, mm d−1), the soil water potential at field capacity ( Sfc, J kg−1) and the leaf water " +
    "potential at the onset of stomatal closure ( Lsc, J kg−1):"

  val t11 = "The average soil water potential ( ̄S , J kg−1) is calculated based on a representative root length " +
    "fraction for each soil layer (fr,j):"

  val t12 = "The L is calculated using T, Cp and  ̄S ."

  val t13 = "If L falls below that of permanent wilting point ( Lpwp), then Ta = 0"

  val t14 = "Finally, Ta is calculated using s and L, Cp and Tp:"

  val t15 = "For this research Tx = 10 mm d−1, Lsc = −1100 J kg−1 and Lpwp = −2000 J kg−1."

  val t16 = "In DSSAT, root water uptake is calculated in two steps."

  val t17 = "First, water uptake per unit of root length is computed in each soil layer (Url, m3 m−1 d−1) as an " +
    "exponential function that depends on:"

}
