package org.clulab.aske.automates.text

import org.clulab.aske.automates.TestUtils._
import org.clulab.aske.automates.OdinEngine.IDENTIFIER_LABEL

class TestIdentifiers extends ExtractionTest {

  val t1 = "where Kcdmin is the minimum crop coefficient"
  passingTest should s"extract identifiers from t1: ${t1}" taggedAs(Somebody) in {


    val desired = Seq("Kcdmin")
    val mentions = extractMentions(t1)
    testTextBoundMention(mentions, IDENTIFIER_LABEL, desired)
  }

  val t2 = "where Kcdmin is the minimum crop coefficient or Kcd at LAI = 0, Kcdmax is the maximum crop " +
    "coefficient at high LAI, and SKc is a shaping parameter that determines the shape of the Kcd versus LAI curve."
  passingTest should s"extract identifiers from t2: ${t2}" taggedAs(Becky) in {


    val desired = Seq("Kcdmin", "Kcd", "LAI", "Kcdmax", "LAI", "SKc", "Kcd", "LAI")
    val mentions = extractMentions(t2)
    testTextBoundMention(mentions, IDENTIFIER_LABEL, desired)
  }

  //
  // sentences from 2017-IMPLEMENTING STANDARDIZED REFERENCE EVAPOTRANSPIRATION AND DUAL CROP COEFFICIENT APPROACH IN THE DSSAT CROPPING SYSTEM MODEL
  //
  val t1a = "Crop coefficients (Kcs) are calculated for the current Penman-Monteith ET approach in DSSAT-CSM as:"
  passingTest should s"extract identifiers from t1a: ${t1a}" taggedAs(Becky) in {

    // TODO:  Is Penman-Monteith part of the identifier?
    val desired = Seq("Kcs", "ET")
    val mentions = extractMentions(t1a)
    testTextBoundMention(mentions, IDENTIFIER_LABEL, desired)
  }

  val t2a = "where LAI is the simulated leaf area index, EORATIO is descrined as the maximum Kcs at LAI = 6.0 " +
    "(Sau et al., 2004; Thorp et al., 2010), and Kcs is the DSSAT-CSM crop coefficient. "
  passingTest should s"extract identifiers from t2a: ${t2a}" taggedAs(Becky) in {

    // TODO:  Is DSSAT-CSM an identifier? - Yes
    // todo(discuss)
    val desired = Seq("LAI", "EORATIO", "Kcs", "LAI", "Kcs") //fixme: deleted DSSAT-CSM as an identifier---we find is as a model now
    val mentions = extractMentions(t2a)
    testTextBoundMention(mentions, IDENTIFIER_LABEL, desired)
  }

  val t3a = "where Kcdmin is the minimum crop coefficient or Kcd at LAI = 0, Kcdmax is the maximum crop " +
    "coefficient at high LAI, and SKc is a shaping parameter that determines the shape of the Kcd versus LAI curve."
  passingTest should s"extract identifiers from t3a: ${t3a}" taggedAs(Becky) in {

    val desired = Seq("Kcdmin", "Kcd", "LAI", "Kcdmax", "LAI", "SKc", "Kcd", "LAI")
    val mentions = extractMentions(t3a)
    testTextBoundMention(mentions, IDENTIFIER_LABEL, desired)
  }

  val t4a = "DSSAT-CSM employs the following formula for calculation of E0 (potential crop ET):"
  passingTest should s"extract identifiers from t4a: ${t4a}" taggedAs(Becky) in {


    val desired = Seq("E0", "ET")
    val mentions = extractMentions(t4a)
    testTextBoundMention(mentions, IDENTIFIER_LABEL, desired)
  }
  val t5a = "E0 is then partitioned into potential plant transpiration (EPo) and potential soil water evaporation (ESo):"
  passingTest should s"extract identifiers from t5a: ${t5a}" taggedAs(Becky) in {


    val desired = Seq("E0", "EPo", "ESo")
    val mentions = extractMentions(t5a)
    testTextBoundMention(mentions, IDENTIFIER_LABEL, desired)
  }
  val t6a = "The ESo calculation in equation 4 is implemented for the CSM-CERES-Maize model and several other crop models."
  passingTest should s"extract identifiers from t6a: ${t6a}" taggedAs(Becky) in {

    val desired = Seq("ESo")
    val mentions = extractMentions(t6a)
    testTextBoundMention(mentions, IDENTIFIER_LABEL, desired)
  }
  val t7a = "Similar to equation 2, E0 is calculated as the product of Kcd and ETpm."
  passingTest should s"extract identifiers from t7a: ${t7a}" taggedAs(Somebody) in {

    val desired = Seq("E0", "Kcd", "ETpm")
    val mentions = extractMentions(t7a)
    testTextBoundMention(mentions, IDENTIFIER_LABEL, desired)
  }

  // note: removed ref from test
  val t8a = " The primary factor causing an increase in the crop coefficient is an increase in plant cover or leaf area; thus, Kc is correlated with LAI."
  passingTest should s"find identifiers t8a: ${t8a}" taggedAs(Becky) in {
    val desired = Seq("Kc", "LAI")
    val mentions = extractMentions(t8a)
    testTextBoundMention(mentions, IDENTIFIER_LABEL, desired)
  }
  val t9a = "Recommended values for Kcdmin and Kcdmax can be found in FAO-56, and DeJonge et al. " +
    "(2012a) recommended 0.5 < SKc < 1.0 as a typical shape to match past literature on the subject."
  failingTest should s"extract identifiers from t9a: ${t9a}" taggedAs(Becky) in {

    val desired = Seq("Kcdmin", "Kcdmax", "SKc", "FAO-56") // todo: "FAO-56" - model? if yes, add to the model rule, delete from test
    //fixme: 2012a is captured as identifier (prob bc of the lookslikeaidentifier action)
    val mentions = extractMentions(t9a)
    testTextBoundMention(mentions, IDENTIFIER_LABEL, desired)
  }

  val t10a ="where KEP (typically ranging from 0.5 to 0.8) is defined as an energy extinction coefficient of the canopy for total solar irradiance, used for partitioning E0 to EPo and ESo (Ritchie, 1998)."
  passingTest should s"extract identifiers from t10a: ${t10a}" taggedAs(Becky) in {

    val desired = Seq("KEP", "E0", "EPo", "ESo")
    val mentions = extractMentions(t10a)
    testTextBoundMention(mentions, IDENTIFIER_LABEL, desired)
  }
  val t11a = "Note that Kcdmax in equation 5 is different from Kcmax in equation A6."
  passingTest should s"extract identifiers from t11a: ${t11a}" taggedAs(Becky) in {


    val desired = Seq("Kcdmax", "Kcmax")
    val mentions = extractMentions(t11a)
    testTextBoundMention(mentions, IDENTIFIER_LABEL, desired)
  }
  val t12a = "where Kcbmin is the minimum basal crop coefficient representing a dry, bare, or nearly bare soil surface."
  passingTest should s"extract identifiers from t12a: ${t12a}" taggedAs(Somebody) in {


    val desired = Seq("Kcbmin")
    val mentions = extractMentions(t12a)
    testTextBoundMention(mentions, IDENTIFIER_LABEL, desired)
  }
  val t13a = "The approach uses model-simulated LAI to calculate the Kcb, which means Kcb is more dynamic and responsive to cultivar, weather, and soil variability, as simulated by the model"
  passingTest should s"extract identifiers from t13a: ${t13a}" taggedAs(Somebody) in {

    val desired = Seq("LAI", "Kcb", "Kcb")
    val mentions = extractMentions(t13a)
    testTextBoundMention(mentions, IDENTIFIER_LABEL, desired)
  }
  val t14a = "Because the aim of equation 8 is potential soil evaporation, Ke is obtained from equation A5 with Kr = 1.0."
  passingTest should s"extract identifiers from t14a: ${t14a}" taggedAs(Somebody) in {


    val desired = Seq("Ke", "Kr")
    val mentions = extractMentions(t14a)
    testTextBoundMention(mentions, IDENTIFIER_LABEL, desired)
  }

  //
  // sentences from 2016-Camargo-and Kemanian-Six-crop-models differ-in-their-simulation-of water-uptake
  //
  val t1b = "In APSIM, water uptake (Ta, mm d−1) is determined from potential transpiration demand (Tp, mm d−1), soil water available (WA, mm d−1), and water supply (WS, mm d−1) for each ith day and soil layer as:"
  failingTest should s"extract identifiers from t1b: ${t1b}" taggedAs(Somebody) in {

    // TODO:  Is APSIM an identifier or the name of a model?
    val desired = Seq("APSIM", "Ta", "Tp", "WA", "WS") //fixme: ith is caught as identifier bc it's short, but is not on the freq word list; ideally, 'i' should be a identifier
    val mentions = extractMentions(t1b)
    testTextBoundMention(mentions, IDENTIFIER_LABEL, desired)
  }
  val t2b = "where fi is the daily fractional light interception, ETo is the daily reference evapotranspiration (mm d−1), pwp is the water content at permanent wilting point (m3 m−3), $z is the soil layer thickness (m), and kl is the water extraction rate, an empiric soil–root factor for the fraction of available water that can be supplied to the plant from each rooted soil layer."
  failingTest should s"extract identifiers from t2b: ${t2b}" taggedAs(Somebody) in {

    val desired = Seq("fi", "ETo", "pwp", "$z", "kl") //todo: missing the last three, finding 'm' as an identifier; adjust the lookLikeAnIdentifier action to allow short lower-case identifiers, probably by checking a lexicon to see if the candidate identifier is an existing word, e.g. at/or/cat...
    //todo: units are also found as identifiers
    val mentions = extractMentions(t2b)
    testTextBoundMention(mentions, IDENTIFIER_LABEL, desired)
  }
  val t3b = "This means that kl represents a maximum supply determined by r and the resistance to water flow (Passioura, 1983; Monteith, 1986)"
  passingTest should s"extract identifiers from t3b: ${t3b}" taggedAs(Somebody) in {


    val desired = Seq("kl", "r") //todo: see t2b
    val mentions = extractMentions(t3b)
    testTextBoundMention(mentions, IDENTIFIER_LABEL, desired)
  }

  val t4b = "The plant conductance is calculated by inverting the transpiration equation using a maximum expected transpiration (Tx, mm d−1), the soil water potential at field capacity ( Sfc, J kg−1) and the leaf water potential at the onset of stomatal closure ( Lsc, J kg−1):"
  passingTest should s"extract identifiers from t4b: ${t4b}" taggedAs(Somebody) in {

    val desired = Seq("Tx", "Sfc", "Lsc") //todo: finds units as identifiers; action at the end, if unit => not an identifier?
    val mentions = extractMentions(t4b)
    testTextBoundMention(mentions, IDENTIFIER_LABEL, desired)
  }
  val t5b = "The average soil water potential (S , J kg−1) is calculated based on a representative root length fraction for each soil layer (fr,j):"
  failingTest should s"extract identifiers from t5b: ${t5b}" taggedAs(Somebody) in {

    val desired = Seq("S", "fr,j") //todo: make sure there's a description test for this sent; need to do sth with the identifiers that contain commas (in the paper, 'r,j' is the subscript)
    val mentions = extractMentions(t5b)
    testTextBoundMention(mentions, IDENTIFIER_LABEL, desired)
  }


  // NEW FORMAT

  val t6b = "The L is calculated using T, Cp and S ."
  passingTest should s"extract identifiers from t6b: ${t6b}" taggedAs(Somebody) in {
    val desired = Seq("L", "T", "Cp", "S")
    val mentions = extractMentions(t6b)
    testTextBoundMention(mentions, IDENTIFIER_LABEL, desired)
  }

  val t7b = "If L falls below that of permanent wilting point ( Lpwp), then Ta = 0"
  passingTest should s"extract identifiers from t7b: ${t7b}" taggedAs(Somebody) in {
    val desired = Seq("L", "Lpwp", "Ta")
    val mentions = extractMentions(t7b)
    testTextBoundMention(mentions, IDENTIFIER_LABEL, desired)
  }

  val t8b = "Finally, Ta is calculated using s and L, Cp and Tp:"
  passingTest should s"extract identifiers from t8b: ${t8b}" taggedAs(Somebody) in {
    val desired = Seq("Ta", "s", "L", "Cp", "Tp") //'s' is not found (or is filtered out?)
    val mentions = extractMentions(t8b)
    testTextBoundMention(mentions, IDENTIFIER_LABEL, desired)
  }

  val t9b = "For this research Tx = 10 mm d−1, Lsc = −1100 J kg−1 and Lpwp = −2000 J kg−1."
  passingTest should s"extract identifiers from t9b: ${t9b}" taggedAs(Somebody) in {
    val desired = Seq("Tx", "Lsc", "Lpwp") //fixme: units found as identifiers; 'research TX' is found as identifier; need to apply looksLikeAVar to units and param settings, not only descrs
    val mentions = extractMentions(t9b)
    testTextBoundMention(mentions, IDENTIFIER_LABEL, desired)
  }

  val t10b = "In DSSAT, root water uptake is calculated in two steps."
  passingTest should s"extract identifiers from t10b: ${t10b}" taggedAs(Somebody) in {
    // TODO: Is DSSAT an identifier?
    val desired = Seq("DSSAT")
    val mentions = extractMentions(t10b)
    testTextBoundMention(mentions, IDENTIFIER_LABEL, desired)
  }

  val t11b = "First, water uptake per unit of root length is computed in each soil layer (Url, m3 m−1 d−1) as an exponential function that depends on:"
  failingTest should s"extract identifiers from t11b: ${t11b}" taggedAs(Somebody) in {
    val desired = Seq("Url") //fixme: units found as identifiers
    val mentions = extractMentions(t11b)
    testTextBoundMention(mentions, IDENTIFIER_LABEL, desired)
  }

  val t12b = "Second, the maximum potential water uptake for the profile (Ux, mm d−1) is obtained by multiplying Ta,rl times r for each layer and summing over the soil profile:"
  failingTest should s"extract identifiers from t12b: ${t12b}" taggedAs(Somebody) in {
    // TODO:  Ta,rl - identifier with subscripts incl commas---get rid of commas in preprocessing if no spaces around?
    val desired = Seq("Ux", "Ta,rl", "r")
    val mentions = extractMentions(t12b)
    testTextBoundMention(mentions, IDENTIFIER_LABEL, desired)
  }

  val t13b = "where s1 and s2 are parameters of a logistic curve (9 and 0.005, respectively), and w represents the soil limitation to water uptake of each layer."
  passingTest should s"extract identifiers from t13b: ${t13b}" taggedAs(Somebody) in {
    val desired = Seq("s1", "s2", "w")
    val mentions = extractMentions(t13b)
    testTextBoundMention(mentions, IDENTIFIER_LABEL, desired)
  }

  // sentences from 2013-Quantifying the Influence of Climate on Human Conflict_Burke-Science

  val t1c = "where locations are indexed by i, observational periods are indexed by t, b is the parameter of interest, and ∈ is the error."
  failingTest should s"extract identifiers from t1c: ${t1c}" taggedAs(Somebody) in {
    // TODO:  deal with "∈" somehow ?
    val desired = Seq("i", "t", "b", "∈") //fixme: i is probably filtered out; 'locations' is found as an identifier---???
    val mentions = extractMentions(t1c)
    testTextBoundMention(mentions, IDENTIFIER_LABEL, desired)
  }


  // sentences from 2006-Root Water Extraction and Limiting Soil Hydraulic Conditions Estimated by Numerical Simulation

//  val tX = ""
//  passingTest should "extract identifiers from tX: ${tX}" taggedAs(Somebody) in {
//    val desired = Seq()
//    val mentions = extractMentions(tX)
//    testTextBoundMention(mentions, IDENTIFIER_LABEL, desired)
//  }

}

//todo: The procedure, first presented in the FAO Irrigation and Drainage Paper No. 24 'Crop Water Requirements' - negative example for identifiers
//todo: Hourly dewpoint from four irrigated regions of southeast Idaho and from a desert weather station ( Flint Creek ) on July 6 , 2000 . - Flint Creek is the neg example for identifiers