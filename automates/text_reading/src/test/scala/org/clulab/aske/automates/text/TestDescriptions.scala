package org.clulab.aske.automates.text

import org.clulab.aske.automates.TestUtils._

class TestDescriptions extends ExtractionTest {


  //todo: separate some of the tests---many fail because of one description being slightly off, so the tests don't really test all the cases

  // Tests from paper: 2017-IMPLEMENTING STANDARDIZED REFERENCE EVAPOTRANSPIRATION AND DUAL CROP COEFFICIENT APPROACH IN THE DSSAT CROPPING SYSTEM MODEL

  val t1a = "Crop coefficients (Kcs) are calculated for the current Penman-Monteith ET approach in DSSAT-CSM as:"
  passingTest should s"extract descriptions from t1a: ${t1a}" taggedAs(Somebody) in {
    val desired = Seq(
      "Kcs" -> Seq("Crop coefficients")
    )
    val mentions = extractMentions(t1a)
    testDescriptionEvent(mentions, desired)
  }

  val t2a = "where LAI is the simulated leaf area index, EORATIO is defined as the maximum Kcs at LAI = 6.0 " +
    "(Sau et al., 2004; Thorp et al., 2010), and Kcs is the DSSAT-CSM crop coefficient."
  failingTest should s"extract descriptions from t2a: ${t2a}" taggedAs(Somebody) in {
    val desired = Seq(
      "LAI" -> Seq("simulated leaf area index"),
      "EORATIO" -> Seq("maximum Kcs at LAI = 6.0"),
      "Kcs" -> Seq("DSSAT-CSM crop coefficient")
      // fixme: can't lose maximum as descr for Kcs
    )
    // fixme: maximum is found as descr for Kcs
    val mentions = extractMentions(t2a)
    testDescriptionEvent(mentions, desired)
  }

  val t3a = "where Kcdmin is the minimum crop coefficient or Kcd at LAI = 0, Kcdmax is the maximum crop " +
    "coefficient at high LAI, and SKc is a shaping parameter that determines the shape of the Kcd versus LAI curve."
  failingTest should s"find descriptions from t3a: ${t3a}" taggedAs(Somebody) in {
    val desired = Seq(
      "Kcdmin" -> Seq("minimum crop coefficient", "Kcd at LAI = 0"), // note: conjunction? is it possible to capture two different descriptions for one identifier?
      "Kcdmax" -> Seq("maximum crop coefficient at high LAI"),
      "SKc" -> Seq("shaping parameter") //todo: should this be expanded?
    )
    val mentions = extractMentions(t3a)

    testDescriptionEvent(mentions, desired)
  }

  val t4a = "DSSAT-CSM employs the following formula for calculation of E0 (potential crop ET):"
  failingTest should s"extract descriptions from t4a: ${t4a}" taggedAs(Somebody) in {
    val desired = Seq(
      "E0" -> Seq("potential crop ET")
      // fixme: can't get rid of potential crop as descr of ET
    )
    val mentions = extractMentions(t4a)
    testDescriptionEvent(mentions, desired)
  }

  val t5a = "The ESo calculation in equation 4 is implemented for the CSM-CERES-Maize model and several other crop models."
  passingTest should s"find NO descriptions from t5a: ${t5a}" taggedAs(Somebody) in {
    val desired = Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t5a)
    testDescriptionEvent(mentions, desired)
  }

   val t6a = "Similar to equation 2, E0 is calculated as the product of Kcd and ETpm."
   passingTest should s"find NO descriptions from t6a: ${t6a}" taggedAs(Somebody) in {
     val desired =  Seq.empty[(String, Seq[String])]
     val mentions = extractMentions(t6a)
     testDescriptionEvent(mentions, desired)
   }

  val t7a = "where KEP (typically ranging from 0.5 to 0.8) is defined as an energy extinction coefficient of " +
    "the canopy for total solar irradiance, used for partitioning E0 to EPo and ESo (Ritchie, 1998)."
    passingTest should s"find descriptions from t7a: ${t7a}" taggedAs(Somebody) in {
      val desired = Seq(
        "KEP" -> Seq("energy extinction coefficient of the canopy for total solar irradiance, used for partitioning E0 to EPo and ESo") // the descr will eventually be the whole sentence
      )
      val mentions = extractMentions(t7a)
      testDescriptionEvent(mentions, desired)
    }

  val t8a = "where Kcbmin is the minimum basal crop coefficient representing a dry, bare, or nearly bare soil surface."
    passingTest should s"find descriptions from t8a: ${t8a}" taggedAs(Somebody) in {
      val desired = Seq(
        "Kcbmin" -> Seq("minimum basal crop coefficient representing a dry, bare, or nearly bare soil surface") //fixme: is this expanding too far?
      )
      val mentions = extractMentions(t8a)
      testDescriptionEvent(mentions, desired)
    }


  val t9a = " The primary factor causing an increase in the crop coefficient is an increase in plant cover or leaf " +
    "area (Jensen and Allen, 2016); thus, Kc is correlated with LAI."
  passingTest should s"find NO descriptions from t9a: ${t9a}" taggedAs(Somebody) in {
    val desired =  Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t9a)
    testDescriptionEvent(mentions, desired)
  }

  val t10a = "Recommended values for Kcdmin and Kcdmax can be found in FAO-56, and DeJonge et al. (2012a) " +
    "recommended 0.5 < SKc < 1.0 as a typical shape to match past literature on the subject."
  passingTest should s"find NO descriptions from t10a: ${t10a}" taggedAs(Somebody) in {
    val desired =  Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t10a)
    testDescriptionEvent(mentions, desired)
  }

  val t11a = "Note that Kcdmax in equation 5 is different from Kcmax in equation A6."
  passingTest should s"find NO descriptions from t11a: ${t11a}" taggedAs(Somebody) in {
    val desired =  Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t11a)
    testDescriptionEvent(mentions, desired)
  }

  val t12a = "The approach uses model-simulated LAI to calculate the Kcb, which means Kcb is more dynamic and " +
    "responsive to cultivar, weather, and soil variability, as simulated by the model"
  passingTest should s"find NO descriptions from t12a: ${t12a}" taggedAs(Somebody) in {
    val desired =  Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t12a)
    testDescriptionEvent(mentions, desired)
  }

  val t13a = "Because the aim of equation 8 is potential soil evaporation, Ke is obtained from equation A5 with " +
    "Kr = 1.0."
  passingTest should s"find NO descriptions from t13a: ${t13a}" taggedAs(Somebody) in {
    val desired =  Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t13a)
    testDescriptionEvent(mentions, desired)

  }

  // Tests from paper: 2016-Camargo-and Kemanian-Six-crop-models differ-in-their-simulation-of water-uptake

  val t1b = "In APSIM, water uptake (Ta, mm d−1) is determined from potential transpiration demand (Tp, mm d−1), soil " +
    "water available (WA, mm d−1), and water supply (WS, mm d−1) for each ith day and soil layer as:"
  passingTest should s"find descriptions from t1b: ${t1b}" taggedAs(Somebody) in {
    val desired = Seq(
      "Ta" -> Seq("water uptake"),
      "Tp" -> Seq("potential transpiration demand"),
      "WA" -> Seq("soil water available"),
      "WS" -> Seq("water supply")
    )
    val mentions = extractMentions(t1b)
    testDescriptionEvent(mentions, desired)
  }

  val t2b = "where fi is the daily fractional light interception, ETo is the daily reference evapotranspiration (mm d−1)," +
    " pwp is the water content at permanent wilting point (m3 m−3), Δz is the soil layer thickness (m), and kl " +
    "is the water extraction rate, an empiric soil–root factor for the fraction of available water that can be " +
    "supplied to the plant from each rooted soil layer."
  failingTest should s"find descriptions from t2b: ${t2b}" taggedAs(Somebody) in {
    val desired = Seq(
      "fi" -> Seq("daily fractional light interception"),
      "ETo" -> Seq("daily reference evapotranspiration"),
      "pwp" -> Seq("water content at permanent wilting point"),
      "Δz" -> Seq("soil layer thickness"), //note: in order to capture "$z" as one identifier, a rule was added under compound_identifier rule.
      "kl" -> Seq("water extraction rate", "empiric soil–root factor for the fraction of available water that can " +
        "be supplied to the plant from each rooted soil layer") //note: is it possible to capture two different descriptions for one identifier?
    )
    val mentions = extractMentions(t2b)
    testDescriptionEvent(mentions, desired)
  }

  val t3b = "This means that kl represents a maximum supply determined by r and the resistance to water flow " +
    "(Passioura, 1983; Monteith, 1986)"
  passingTest should s"find descriptions from t3b: ${t3b}" taggedAs(Somebody) in {
    val desired = Seq(
      "kl" -> Seq("maximum supply determined by r and the resistance to water flow")
    )
    val mentions = extractMentions(t3b)
    testDescriptionEvent(mentions, desired)
  }

  val t4b = "The plant conductance is calculated by inverting the transpiration equation using a maximum expected " +
    "transpiration (Tx, mm d−1), the soil water potential at field capacity ( Sfc, J kg−1) and the leaf water " +
    "potential at the onset of stomatal closure ( Lsc, J kg−1):"
  passingTest should s"find descriptions from t4b: ${t4b}" taggedAs(Somebody) in {
    val desired = Seq(
      //"plant conductance" -> Seq("inverting the transpiration equation"), // todo: do we want this one?
      "Tx" -> Seq("maximum expected transpiration"),
      "Sfc" -> Seq("soil water potential at field capacity"),
      "Lsc" -> Seq("leaf water potential at the onset of stomatal closure")
    )
    val mentions = extractMentions(t4b)
    testDescriptionEvent(mentions, desired)
  }

  val t5b = "The average soil water potential (S, J kg−1) is calculated based on a representative root length " +
    "fraction for each soil layer (frj):"
  passingTest should s"find descriptions from t5b: ${t5b}" taggedAs(Somebody) in {
    val desired = Seq(
      "S" -> Seq("average soil water potential"),
      "frj" -> Seq("representative root length fraction for each soil layer")
    )
    val mentions = extractMentions(t5b)
    testDescriptionEvent(mentions, desired)
  }

  val t6b = "The L is calculated using T, Cp and  ̄S ."
  passingTest should s"find NO descriptions from t6b: ${t6b}" taggedAs(Somebody) in {
    val desired = Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t6b)
    testDescriptionEvent(mentions, desired)
  }

  val t7b = "If L falls below that of permanent wilting point (Lpwp), then Ta = 0"
  passingTest should s"find descriptions from t7b: ${t7b}" taggedAs(Somebody) in {
    val desired = Seq(
      "Lpwp" -> Seq("permanent wilting point") // todo: or "that of permanent wilting point" ?? (or L falls below that of permanent wilting point??) (needs to be reviewed)
    )
    val mentions = extractMentions(t7b)
    testDescriptionEvent(mentions, desired)
  }

  val t8b = "Finally, Ta is calculated using s and L, Cp and Tp:"
  passingTest should s"find NO descriptions from t8b: ${t8b}" taggedAs(Somebody) in {
    val desired =  Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t8b)
    testDescriptionEvent(mentions, desired)
  }

  val t9b = "For this research Tx = 10 mm d−1, Lsc = −1100 J kg−1 and Lpwp = −2000 J kg−1."
  passingTest should s"find NO descriptions from t9b: ${t9b}" taggedAs(Somebody) in {
    val desired =  Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t9b)
    testDescriptionEvent(mentions, desired)
  }

  val t10b = "In DSSAT, root water uptake is calculated in two steps."
  passingTest should s"find NO descriptions from t10b: ${t10b}" taggedAs(Somebody) in {
    val desired =  Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t10b)
    testDescriptionEvent(mentions, desired)
  }

  val t11b = "First, water uptake per unit of root length is computed in each soil layer (Url, m3 m−1 d−1) as an " +
    "exponential function that depends on:"
  passingTest should s"find descriptions from t11b: ${t11b}" taggedAs(Somebody) in {
    val desired = Seq(
      "Url" -> Seq("water uptake per unit of root length")
    )
    val mentions = extractMentions(t11b)
    testDescriptionEvent(mentions, desired)

  }
  val t12b = "Second, the maximum potential water uptake for the profile (Ux, mm d−1) is obtained by multiplying Tarl " +
    "times pr for each layer and summing over the soil profile:"
    passingTest should s"find descriptions from t12b: ${t12b}" taggedAs(Somebody) in {
      val desired = Seq(
        "Ux" -> Seq("maximum potential water uptake for the profile") //for the profile? - not part of the concept
      )
      val mentions = extractMentions(t12b)
      testDescriptionEvent(mentions, desired)

    }
  val t13b = "where s1 and s2 are parameters of a logistic curve (9 and 0.005, respectively), and w represents the " +
    "soil limitation to water uptake of each layer."
    passingTest should s"find descriptions from t13b: ${t13b}" taggedAs(Somebody) in {
      val desired = Seq(
        "s1" -> Seq("parameters of a logistic curve"),
        "s2" -> Seq("parameters of a logistic curve"), // fixme: description for s2 is captured twice by both identifier_cop_conj_description and identifier_cop_description.
        "w" -> Seq("soil limitation") // need to expand this to "to water uptake of each layer" (needs to be reviewed - expansion handler?)
      )
      val mentions = extractMentions(t13b)
      testDescriptionEvent(mentions, desired)
    }

    // Tests from paper: 2006-Root Water Extraction and Limiting Soil Hydraulic Conditions Estimated by Numerical Simulation

  val t1c = "A convenient soil hydraulic property that will be used in this study is the matric flux potential " +
    "Mh0 (m2 d-1)"
    passingTest should s"find descriptions from t1c: ${t1c}" taggedAs(Somebody) in {
      val desired = Seq(
        "Mh0" -> Seq("matric flux potential"),
        "Mh0" -> Seq("convenient soil hydraulic property")
      )
      val mentions = extractMentions(t1c)
      testDescriptionEvent(mentions, desired)
    }

  val t2c = "where t is time (d), C is the differential water capacity (du/dh, m21), q is the water flux density " +
    "(m d21), r is the distance from the axial center (m), S is a sink or source term (d21), and H is the hydraulic " +
    "head (m)."
    failingTest should s"find descriptions from t2c: ${t2c}" taggedAs(Somebody) in {
      val desired = Seq(
        "t" -> Seq("time"), // fixme: d is captured as a identifier here. needs to be fixed. (needs to be reviewed - difficulty of distinguishing "units" and "identifiers")
        "C" -> Seq("differential water capacity"),
        "q" -> Seq("water flux density"),
        "r" -> Seq("distance from the axial center"),
        "S" -> Seq("sink or source term"), //two separate concepts, not going to pass without expansion? (todo: try expand on conj_or!)
        "H" -> Seq("hydraulic head")
      )
      //fixme: "identifier_description_appos_bidir++selectShorter" rule wrongly extracted two additional descriptions.
      val mentions = extractMentions(t2c)
      testDescriptionEvent(mentions, desired)
    }

  val t4c = "Segment size (dr) was chosen smaller near the root and larger at greater distance, according to"
  passingTest should s"find descriptions from t4c: ${t4c}" taggedAs(Somebody) in {
      val desired = Seq(
        "dr" -> Seq("Segment size")
      )
      val mentions = extractMentions(t4c)
      testDescriptionEvent(mentions, desired)
    }

  val t5c = "in which L (m) is the root length, z (m) is the total rooted soil depth, Ap (m2) is the surface area " +
    "and Ar (m2) is the root surface area."
    failingTest should s"find descriptions from t5c: ${t5c}" taggedAs(Somebody) in {
      val desired = Seq(
        "L" -> Seq("root length"), //fixme: both L and z are captured as compound identifiers with "(m)". -> fixed
        "z" -> Seq("total rooted soil depth"), //z is not found as concept bc it's found as B-VP: need a surface rule where identifier is any word but use a looksLikeAVar on it? -> fixed
        "Ap" -> Seq("surface area"),
        "Ar" -> Seq("root surface area") //todo: bad parse; have to have a surface rule -> fixed
      )
      val mentions = extractMentions(t5c)
      testDescriptionEvent(mentions, desired)
    }


  val t7c = "with dr,min = 1028 m, dr,max = 5.1024 m, S = 0.5, r0 (m) is the root radius and rm (m) is the radius of " +
    "the root extraction zone, equal to the half-distance between roots (rm), which relates to the root density " +
    "R (m m23) as..."
  failingTest should s"find descriptions from t7c: ${t7c}" taggedAs(Somebody) in {

    val desired = Seq(
      "r0" -> Seq("root radius"), // fixme: when identifier and description are separated by parenthesis, it is not captured by identifier_cop_description rule. -> fixed
      "rm" -> Seq("radius of the root extraction zone"), // fixme: roots (rm) sequence is captured as descr (identifier) by comma_appos_identifier rule.
      "R" -> Seq("root density")
    )
    val mentions = extractMentions(t7c)
    testDescriptionEvent(mentions, desired)
  }

  val t8c = "where p is the iteration level."
  passingTest should s"find descriptions from t8c: ${t8c}" taggedAs(Somebody) in {
    val desired = Seq(
      "p" -> Seq("iteration level")
    )
    val mentions = extractMentions(t8c)
    testDescriptionEvent(mentions, desired)
  }


  // Tests from paper: 2005-THE ASCE STANDARDIZED REFERENCE EVAPOTRANSPIRATION EQUATION

  val t1d = "The density of water (ρw) is taken as 1.0 Mg m-3."
  passingTest should s"find descriptions from t1d: ${t1d}" taggedAs(Somebody) in {
    val desired = Seq(
      "ρw" -> Seq("density of water")
    )
    val mentions = extractMentions(t1d)
    testDescriptionEvent(mentions, desired)
  }

  val t1e = "Since eS is not a linear function of temperature"
  passingTest should s"find NO descriptions from t1e: ${t1e}" taggedAs(Somebody) in {
    val desired = Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t1e)
    testDescriptionEvent(mentions, desired)
  }

  val t2e = "Rnl, net long-wave radiation, is the difference between upward long-wave radiation from the standardized surface (Rlu) and downward long-wave radiation from the sky (Rld)"
  failingTest should s"find descriptions from t2e: ${t2e}" taggedAs(Somebody) in {
    val desired = Seq(
      "Rnl" -> Seq("net long-wave radiation"), //fixme: identifier_cop_description overrode the identifier_appos_descr rule. (maybe due to "keep the longest" principle?) -> fixed, but now two descriptions are captured
      "Rlu" -> Seq("upward long-wave radiation from the standardized surface"), //fixme: description was not captured. (maybe due to the overlapping?)
      "Rld" -> Seq("downward long-wave radiation from the sky"), //fixme: needs to expand to include the "downward long-wave radiation from the" part (issue occurred due to bad parsing)
    )
    val mentions = extractMentions(t2e)
    testDescriptionEvent(mentions, desired)
  }

  val t3e = "Extraterrestrial radiation, Ra, defined as the short-wave solar radiation in the absence of an atmosphere, is a well-behaved function of the day of the year, time of day, and latitude."
  failingTest should s"find definitions from t3e: ${t3e}" taggedAs(Somebody) in {
    val desired = Seq(
      "Ra" -> Seq("Extraterrestrial radiation"), // fixme: only a part of it ("extraterrestrial") is captured. (why is "radiation" not a concept?)
      "Ra" -> Seq("short-wave solar radiation in the absence of an atmosphere"), // fixme: this definition is not captured at all.
      "Ra" -> Seq("well-behaved function of the day of the year, time of day, and latitude.") // fixme: function definition not captured.
    )
    val mentions = extractMentions(t3e)
    testDescriptionEvent(mentions, desired)
  }

  val t4e = "For daily (24-hour) periods, Ra can be estimated from the solar constant, the solar declination, and the day of the year."
  passingTest should s"find NO definitions from t4e: ${t4e}" taggedAs(Somebody) in {
    val desired = Seq.empty[(String, Seq[String])] // fixme: comma_appos_var rule wrongly captured a definition for Ra.
    val mentions = extractMentions(t4e)
    testDescriptionEvent(mentions, desired)
  }

//  val t9c = "Assuming no sink or source (S = 0) and no gravitational or osmotic component (H = h), Eq. [4] reduces to..."
//  failingTest should s"find descriptions from t9c: ${t9c}" taggedAs(Somebody) in {
//    val desired = Seq(
//
//    )
//    val mentions = extractMentions(t9c)
//    testDescriptionEvent(mentions, desired)
//  }

// Tests from paper: 2020-08-04-CHIME-documentation

  // slightly modified from the paper
  val t3f = "β can be interpreted as the effective contact rate. It is the transmissibility τ multiplied by the average number of people exposed c."
  passingTest should s"find descriptions from t3f: ${t3f}" taggedAs(Somebody) in {
    val desired = Seq(
      "β" -> Seq("effective contact rate"),
      "τ" -> Seq("transmissibility"),
      "c." -> Seq("average number of people exposed") //fixme: period(.) should be deleted after c & needs to check if it is average number or just number
    )
    val mentions = extractMentions(t3f)
    testDescriptionEvent(mentions, desired)
  }

  val t4f = "γ is the inverse of the mean recovery time"
  passingTest should s"find descriptions from t4f: ${t4f}" taggedAs(Somebody) in {
    val desired = Seq(
      "γ" -> Seq("inverse of the mean recovery time")
    )
    val mentions = extractMentions(t4f)
    testDescriptionEvent(mentions, desired)
  }

  val t5f = "An important descriptive parameter is the basic reproduction number, or R0."
  passingTest should s"find descriptions from t5f: ${t5f}" taggedAs(Somebody) in {
    val desired = Seq(
      "R0" -> Seq("basic reproduction number")
    )
    val mentions = extractMentions(t5f)
    testDescriptionEvent(mentions, desired)
  }

  val t6f = "If this happens at time t, then the effective reproduction rate is Rt, which will be lower than R0."
  passingTest should s"find descriptions from t6f: ${t6f}" taggedAs(Somebody) in {
    val desired = Seq(
      "t" -> Seq("time"),
      "Rt" -> Seq("effective reproduction rate")
    )
    val mentions = extractMentions(t6f)
    testDescriptionEvent(mentions, desired)
  }

  val t7f = "The AHA says to expect a doubling time Td of 7-10 days."
  passingTest should s"find descriptions from t7f: ${t7f}" taggedAs(Somebody) in {
    val desired = Seq(
      "Td" -> Seq("doubling time")
    )
    val mentions = extractMentions(t7f)
    testDescriptionEvent(mentions, desired)
  }

  val t8f = "Since the rate of new infections in the SIR model is g = βS − γ and we've already computed γ,"
  passingTest should s"find descriptions from t8f: ${t8f}" taggedAs(Somebody) in {
    val desired = Seq(
      "g" -> Seq("rate of new infections in the SIR model")
    )
    val mentions = extractMentions(t8f)
    testDescriptionEvent(mentions, desired)
  }

  val t9f = "This is the initial S (Susceptible) input in the SIR model."
  passingTest should s"find descriptions from t9f: ${t9f}" taggedAs(Somebody) in {
    val desired = Seq(
      "S" -> Seq("Susceptible") // fixme: can't get rid of initial as descr without disallowing adj-only descriptions
    )
    val mentions = extractMentions(t9f)
    testDescriptionEvent(mentions, desired)
  }

  val t10f = "This will affect projections for the number infected and the numbers requiring hospitalization, intensive care (ICU), and ventilation."
  passingTest should s"find descriptions from t10f: ${t10f}" taggedAs(Somebody) in {
    val desired = Seq(
      "ICU" -> Seq("intensive care")
    )
    val mentions = extractMentions(t10f)
    testDescriptionEvent(mentions, desired)
  }

  val t11f = "The number of patients currently hospitalized with COVID-19 at your hospital(s)."
  passingTest should s"find NO descriptions from t11f: ${t11f}" taggedAs(Somebody) in {
    val desired =  Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t11f)
    testDescriptionEvent(mentions, desired)
  }

// Tests from paper: 2003-A_double_epidemic_model_for_the_SARS_propagation

  val t1g = "the susceptibles, S, who can catch the disease; the infectives, I, who have the disease and can transmit it; " +
    "and the removed class, R, namely those  who  have  either  had  the  disease, or are recovered, immune or isolated until recovered."
  failingTest should s"find descriptions from t1g: ${t1g}" taggedAs(Somebody) in {
    val desired =  Seq(
      "S" -> Seq("susceptibles who can catch the disease"), // fixme: [error] Vector((S,susceptibles)) did not contain element (S,susceptibles who can catch the disease) (TestUtils.scala:123)
      "I" -> Seq("infectives who have the disease and can transmit it"),
      "R" -> Seq("removed class namely those who have either had the disease, or are recovered, immune or isolated until recovered"),
    )
    val mentions = extractMentions(t1g)
    testDescriptionEvent(mentions, desired)
  }

    val t2g = "Let S(t), I(t) and R(t) be the number of individuals in each of the corresponding class at time t. "
  failingTest should s"find descriptions from t2g: ${t2g}" taggedAs(Somebody) in {
    val desired =  Seq(
      "S(t)" -> Seq("number of individuals in class at time t"),
      "I(t)" -> Seq("number of individuals in class at time t"),
      "R(t)" -> Seq("number of individuals in class at time t"),
      "t" -> Seq("time") // fixme: needs to limit the range of description. it is too extreme.
    )
    val mentions = extractMentions(t2g)
    testDescriptionEvent(mentions, desired)
  }

  val t2gToy = "Let S(t), I(t) and R(t) be the number of individuals in each class."
  passingTest should s"find descriptions from t2gToy: ${t2gToy}" taggedAs(Somebody) in {
    val desired =  Seq(
      "S(t)" -> Seq("number of individuals in each class"),
      "I(t)" -> Seq("number of individuals in each class"),
      "R(t)" -> Seq("number of individuals in each class")
    )
    val mentions = extractMentions(t2gToy)
    testDescriptionEvent(mentions, desired)
  }

    val t3g = "This new model will be called SEIRP model (E stands for the Exposed class while P stands for protection)."
  passingTest should s"find descriptions from t3g: ${t3g}" taggedAs(Somebody) in {
    val desired =  Seq(
      "E" -> Seq("Exposed class"),
      "P" -> Seq("protection")
    )
    val mentions = extractMentions(t3g)
    testDescriptionEvent(mentions, desired)
  }

    val t4g = "where r is the infection rate and a the removal rate of infectives."
  passingTest should s"find descriptions from t4g: ${t4g}" taggedAs(Somebody) in {
    val desired =  Seq(
      "r" -> Seq("infection rate"),
      "a" -> Seq("removal rate of infectives")
    )
    val mentions = extractMentions(t4g)
    testDescriptionEvent(mentions, desired)
  }


// Tests from unknown papers

    val t1h = "where Rn is the net radiation, H the sensible heat, G the soil heat flux and λET the latent heat flux."
  passingTest should s"find descriptions from t1h: ${t1h}" taggedAs(Somebody) in {
    val desired =  Seq(
      "Rn" -> Seq("net radiation"),
      "H" -> Seq("sensible heat"),
      "G" -> Seq("soil heat flux"),
      "λET" -> Seq("latent heat flux")
    )
    val mentions = extractMentions(t1h)
    testDescriptionEvent(mentions, desired)
  }

    val t2h = "The only factors affecting ETo are climatic parameters."
  passingTest should s"find NO descriptions from t2h: ${t2h}" taggedAs(Somebody) in {
    val desired =  Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t2h)
    testDescriptionEvent(mentions, desired)
  }

    val t3h = "The crop evapotranspiration under standard conditions, denoted as ETc, " +
      "is the evapotranspiration from disease-free, well-fertilized crops, grown in large fields, " +
      "under optimum soil water conditions, and achieving full production under the given climatic conditions."
  failingTest should s"find descriptions from t3h: ${t3h}" taggedAs(Somebody) in {
    val desired =  Seq(
      "ETc" -> Seq("crop evapotranspiration under standard conditions"), // todo: ETc should be captured as an identifier. -> fixed (descriptions not captured properly. needs new rules.)
      "ETc" -> Seq("evapotranspiration from disease-free, well-fertilized crops, grown in large fields, " + // fixme: this should be captured as the description.
      "under optimum soil water conditions, and achieving full production under the given climatic conditions") // todo: need to allow two descriptions per identifier.
    )
    val mentions = extractMentions(t3h)
    testDescriptionEvent(mentions, desired)
  }
  val t3hToy = "The crop evapotranspiration under standard conditions, denoted as ETc..."
  passingTest should s"find descriptions from t3hToy: ${t3hToy}" taggedAs(Somebody) in {
    val desired =  Seq(
      "ETc" -> Seq("crop evapotranspiration under standard conditions")
    )
    val mentions = extractMentions(t3hToy)
    testDescriptionEvent(mentions, desired)
  }

    val t4h = "First, the limiting value R∞, called the total size of the epidemic which is the total number of people having the disease at the end of the epidemic."
  failingTest should s"find descriptions from t4h: ${t4h}" taggedAs(Somebody) in {
    val desired =  Seq(
      "R∞" -> Seq("limiting value"),
      "R∞" -> Seq("total size of the epidemic"),
      "R∞" -> Seq("total number of people having the disease at the end of the epidemic")
    )
    val mentions = extractMentions(t4h)
    testDescriptionEvent(mentions, desired)
  }

  val t4hToy = "First, the limiting value R∞..."
  passingTest should s"find descriptions from t4hToy: ${t4hToy}" taggedAs(Somebody) in {
    val desired =  Seq(
      "R∞" -> Seq("limiting value")
    )
    val mentions = extractMentions(t4hToy)
    testDescriptionEvent(mentions, desired)
  }

    val t5h = "Second, R0 = r/a, the basic reproduction number which is the average number of secondary infections produced when one infected individual is introduced into " +
      "a host population where everyone is susceptible."
  failingTest should s"find descriptions from t5h: ${t5h}" taggedAs(Somebody) in {
    val desired =  Seq(
      "R0" -> Seq("the basic reproduction number"),
      "R0" -> Seq("the average number of secondary infections produced when one infected individual is introduced into a host population where everyone is susceptible")
    ) // todo: needs a new rule
    val mentions = extractMentions(t5h)
    testDescriptionEvent(mentions, desired)
  }

    val t6h = "Wilting point Wp and field capacity Wc were calculated from soil depth and soil texture information, i.e., the relative proportion of sand, silt and clay, according to a set of prediction equations developed by Saxton et al. (1986)."
  failingTest should s"find descriptions from t6h: ${t6h}" taggedAs(Somebody) in {
    val desired =  Seq(
      "Wp" -> Seq("Wilting point"), // fixme: description for Wp is not captured.
      "Wc" -> Seq("field capacity")
    )
    val mentions = extractMentions(t6h)
    testDescriptionEvent(mentions, desired)
  }

// Tests from paper: Covid_Act_Now_Model_Reference

    val t1i = "Susceptible (S) individuals may become exposed (E) to the virus, then infected (I) at varying " +
      "levels of disease severity (mild, moderate, or severe, illustrated as I1, I2, and I3 respectively)."
  failingTest should s"find descriptions from t1i: ${t1i}" taggedAs(Somebody) in {
    val desired =  Seq(
      "S" -> Seq("Susceptible"),
      "E" -> Seq("exposed"), // fixme: Descriptions of I1, I2, I3 are not extracted (needs to be reviewed - needs a new conj_rule?) // todo: check if I1, I2, I3 are actually identifiers (covid act now p.2)
      "I" -> Seq("infected"),
      "I1" -> Seq("mild"),
      "I2" -> Seq("moderate"),
      "I3" -> Seq("severe")
    )
    val mentions = extractMentions(t1i)
    testDescriptionEvent(mentions, desired)
  }

  // sacrificing this for the greater good (too many adjectives are extracted as definitions---for now disallow definitions without nouns or participles/gerunds)
  val t1iToy = "Susceptible (S) individuals may become exposed (E) to the virus, then infected (I) at varying " +
    "levels of disease severity."
  failingTest should s"find descriptions from t1iToy: ${t1iToy}" taggedAs(Somebody) in {
    val desired =  Seq(
      "S" -> Seq("Susceptible"),
      "E" -> Seq("exposed"), 
      "I" -> Seq("infected")
    )
    val mentions = extractMentions(t1iToy)
    testDescriptionEvent(mentions, desired)
  }

// Tests from paper: ideal_sir_model_without_vital_dynamics

    val t1j = "This idea can probably be more readily seen if we say that the typical time between contacts is Tc = β-1, " +
      "and the typical time until recovery is Tr = γ-1."
  passingTest should s"find descriptions from t1j: ${t1j}" taggedAs(Somebody) in {
    val desired =  Seq(
      "Tc" -> Seq("typical time between contacts"),
      "Tr" -> Seq("typical time until recovery")
    )
    val mentions = extractMentions(t1j)
    testDescriptionEvent(mentions, desired)
  }

// Tests from paper: PT-2012-ET Measurement and Estimation Using Modified PT in Maise with Mulching-petpt_2012

    val t1k = "where θ is soil water content in 0–1.0 m soil (cm3 cm−3), θF is field capacity (cm3 cm−3) and θw is wilting point (cm3 cm−3)."
  passingTest should s"find descriptions from t1k: ${t1k}" taggedAs(Somebody) in {
    val desired =  Seq(
      "θ" -> Seq("soil water content in 0–1.0 m soil"),
      "θF" -> Seq("field capacity"),
      "θw" -> Seq("wilting point")
    )
    val mentions = extractMentions(t1k)
    testDescriptionEvent(mentions, desired)
  }

    val t2k = "κ, canopy extinction coefficient of radiation, is dependent on foliage orientation and solar zenith angle, 0.45 for this study (Campbell and Norman, 1998)."
  passingTest should s"find descriptions from t2k: ${t2k}" taggedAs(Somebody) in {
    val desired =  Seq(
      "κ" -> Seq("canopy extinction coefficient of radiation")
    )
    val mentions = extractMentions(t2k)
    testDescriptionEvent(mentions, desired)
  }

// Tests from paper: THE ASCE STANDARDIZED REFERENCE EVAPOTRANSPIRATION EQUATION

    val t1l = "Reference evapotranspiration (ETref) is the rate at which readily available soil water is vaporized from specified vegetated surfaces (Jensen et al., 1990)."
  passingTest should s"find descriptions from t1l: ${t1l}" taggedAs(Somebody) in {
    val desired =  Seq(
      "ETref" -> Seq("Reference evapotranspiration"),
      "ETref" -> Seq("rate at which readily available soil water is vaporized from specified vegetated surfaces")
    )
    val mentions = extractMentions(t1l)
    testDescriptionEvent(mentions, desired)
  }

    val t2l = "ETsz = standardized reference crop evapotranspiration for short (ETos) or tall (ETrs) surfaces (mm d-1 for daily time steps or mm h-1 for hourly time steps),"
  failingTest should s"find descriptions from t2l: ${t2l}" taggedAs(Somebody) in {
    val desired =  Seq(
      "ETsz" -> Seq("standardized reference crop evapotranspiration for short (ETos) or tall (ETrs) surfaces") //fixme: short is captured as the description of ETos
    )
    val mentions = extractMentions(t2l)
    testDescriptionEvent(mentions, desired)
  }

    val t3l = "Latent Heat of Vaporization (λ)"
  passingTest should s"find descriptions from t3l: ${t3l}" taggedAs(Somebody) in {
    val desired =  Seq(
      "λ" -> Seq("Latent Heat of Vaporization")
    )
    val mentions = extractMentions(t3l)
    testDescriptionEvent(mentions, desired)
  }

    val t4l = "e°(Tmax) = saturation vapor pressure at daily maximum temperature [kPa]"
  passingTest should s"find descriptions from t4l: ${t4l}" taggedAs(Somebody) in {
    val desired =  Seq(
      "e°(Tmax)" -> Seq("= saturation vapor pressure at daily maximum temperature") // can't remove expansion on amod, so have to make peace with the = in the def
    )
    val mentions = extractMentions(t4l)
    testDescriptionEvent(mentions, desired)
  }

    val t5l = "The inverse of λ = 2.45 MJ kg-1 is approximately 0.408 kg MJ-1."
  passingTest should s"find NO descriptions from t5l: ${t5l}" taggedAs(Somebody) in {
    val desired =  Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t5l)
    testDescriptionEvent(mentions, desired)
  }

  // Tests from paper: PEN-2018-Step by Step Calculation of the Penman-Monteith ET-petpen_PM

    val t1m = "Reference evapotranspiration (ETo) is defined as the rate at which readily available soil water is vaporized from specified vegetated surfaces (Jensen et al., 1990)."
  passingTest should s"find definitions from t1m: ${t1m}" taggedAs(Somebody) in {
    val desired = Seq(
      "ETo" -> Seq("Reference evapotranspiration"),
      "ETo" -> Seq("rate at which readily available soil water is vaporized from specified vegetated surfaces")
    )
    val mentions = extractMentions(t1m)
    testDescriptionEvent(mentions, desired)
  }


  // Tests from paper: model for predicting evaporation from a row crop with incomplete cover

  val t1n = "Wind speed, Rno, and the vapor pressure deficit are all lowered in approximate proportion to the canopy density."
  passingTest should s"find NO definitions from t1n: ${t1n}" taggedAs(Somebody) in {
    val desired = Seq.empty[(String, Seq[String])] // fixme: Wind speed is captured as a definition for Rno. -> fixed by changing comma_appos_var rule
    val mentions = extractMentions(t1n)
    testDescriptionEvent(mentions, desired)
  }

  val t2n = "Since the soil was relatively dry before the rainfall was received, Es would be expected to be lower than the value predicted by the model."
  failingTest should s"find NO definitions from t2n: ${t2n}" taggedAs(Somebody) in {
    val desired = Seq.empty[(String, Seq[String])] // fixme: "was" and "rainfall was received" is captured as definitions for Es. (needs to be fixed by finding a cause from comma_appos_var rule.
    val mentions = extractMentions(t2n)
    testDescriptionEvent(mentions, desired)
  }

  val t3n = "For example, consider a case in which the average air temperature is 32°C, Lai = 2.7, Rn0 = 5.0, E0 = 5.0, and ΣEs1 < U."
  failingTest should s"find NO definitions from t3n: ${t3n}" taggedAs(Somebody) in {
    val desired = Seq.empty[(String, Seq[String])] // fixme: "average air temperature" is captured as a definition for C in 32°C.
    val mentions = extractMentions(t3n)
    testDescriptionEvent(mentions, desired)
  }

  // Tests from LPJmL_LPJmL4 \u2013 a dynamic global vegetation model with managed land \u2013 Part 1 Model description.pdf
  val t1o = "where α = λ/c is thermal diffusivity, λ thermal conductivity, and c heat capacity"
  failingTest should s"find descriptions from t1o: ${t1o}" taggedAs(Somebody) in {
    val desired =  Seq(
      "α" -> Seq("thermal diffusivity"),
      "λ" -> Seq("thermal conductivity"),
      "c" -> Seq("heat capacity")
    )
    val mentions = extractMentions(t1o)
    testDescriptionEvent(mentions, desired)
  }

  val t2o = "where α = λ/c is thermal diffusivity"
  // alpha is not reached with any rule because of lambda/c
  failingTest should s"find descriptions from t2o: ${t2o}" taggedAs(Somebody) in {
    val desired =  Seq(
      "α" -> Seq("thermal diffusivity")
    )
    val mentions = extractMentions(t2o)
    testDescriptionEvent(mentions, desired)
  }


  // SuperMaaS tests

  val u1a = "the daily herbage harvest (grazed) is 400 kg DM/ha."
  failingTest should s"find NO descriptions from u1a: ${u1a}" taggedAs(Somebody) in {
    val desired = Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(u1a)
    testDescriptionEvent(mentions, desired)
  }

  // this is a test based on a real, not well-processed document, so some symbols don't make sense; the point of the test, though, is to prevent incorrect copy-with-arg-ing or grouping of mentions---each descr mention in this document should be contained within one sentence
  val multiSent1 = "The exponent b controls the shape of the demand curve, and can be interpreted as a short-term price elasticity of world market demand. We investigate two different versions of the model: One (called FixCons, for ﬁxed consumption) in which is prescribed to match ﬁnal consumption Qout observed annual consumption; and one (called FlexCons, for ﬂexible consumption) in which annual deviations from the observed long-term consumption trend are determined within the model based on simulated prices, according to ð Þed ð7Þ QoutðtÞ ¼ Qout;refðtÞ⋅ PðtÞ / PaveðtÞ."
  // alpha is not reached with any rule because of lambda/c
  passingTest should s"have each description mention contained within one sentence: ${multiSent1}" taggedAs(Somebody) in {
    val descrMentions = extractMentions(multiSent1).filter(_.label contains "Description")
    withinOneSentenceTest(descrMentions)
  }

}
