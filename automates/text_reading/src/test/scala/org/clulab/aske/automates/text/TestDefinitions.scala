package org.clulab.aske.automates.text

import org.clulab.aske.automates.TestUtils._

class TestDefinitions extends ExtractionTest {


  //todo: separate some of the tests---many fail because of one definition being slightly off, so the tests don't really test all the cases

  // Tests from paper: 2017-IMPLEMENTING STANDARDIZED REFERENCE EVAPOTRANSPIRATION AND DUAL CROP COEFFICIENT APPROACH IN THE DSSAT CROPPING SYSTEM MODEL

  val t1a = "Crop coefficients (Kcs) are calculated for the current Penman-Monteith ET approach in DSSAT-CSM as:"
  passingTest should s"extract definitions from t1a: ${t1a}" taggedAs(Somebody) in {
    val desired = Seq(
      "Kcs" -> Seq("Crop coefficients")
    )
    val mentions = extractMentions(t1a)
    testDefinitionEvent(mentions, desired)
  }

  val t2a = "where LAI is the simulated leaf area index, EORATIO is defined as the maximum Kcs at LAI = 6.0 " +
    "(Sau et al., 2004; Thorp et al., 2010), and Kcs is the DSSAT-CSM crop coefficient."
  failingTest should s"extract definitions from t2a: ${t2a}" taggedAs(Somebody) in {
    val desired = Seq(
      "LAI" -> Seq("simulated leaf area index"),
      "EORATIO" -> Seq("maximum Kcs at LAI = 6.0"), //todo: how to attach param setting to definition?
      "Kcs" -> Seq("DSSAT-CSM crop coefficient")
    )
    val mentions = extractMentions(t2a)
    val defMentions = mentions.seq.filter(_ matches "Definition")
    testDefinitionEvent(mentions, desired)
  }

  val t3a = "where Kcdmin is the minimum crop coefficient or Kcd at LAI = 0, Kcdmax is the maximum crop " +
    "coefficient at high LAI, and SKc is a shaping parameter that determines the shape of the Kcd versus LAI curve."
  failingTest should s"find definitions from t3a: ${t3a}" taggedAs(Somebody) in {
    val desired = Seq(
      "Kcdmin" -> Seq("minimum crop coefficient", "Kcd at LAI = 0"),
      "Kcdmax" -> Seq("maximum crop coefficient at high LAI"),
      "SKc" -> Seq("shaping parameter") //todo: should this be expanded?
    )
    val mentions = extractMentions(t3a)

    testDefinitionEvent(mentions, desired)
  }

  val t4a = "DSSAT-CSM employs the following formula for calculation of E0 (potential crop ET):"
  passingTest should s"extract definitions from t4a: ${t4a}" taggedAs(Somebody) in {
    val desired = Seq(
      "E0" -> Seq("potential crop ET")
    )
    val mentions = extractMentions(t4a)
    testDefinitionEvent(mentions, desired)
  }

  val t5a = "The ESo calculation in equation 4 is implemented for the CSM-CERES-Maize model and several other crop models."
  passingTest should s"find NO definitions from t5a: ${t5a}" taggedAs(Somebody) in {
    val desired = Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t5a)
    testDefinitionEvent(mentions, desired)
  }

  val t6a = "Similar to equation 2, E0 is calculated as the product of Kcd and ETpm."
  passingTest should s"find NO definitions from t6a: ${t6a}" taggedAs(Somebody) in {
//    val desired = Seq(
//      "E0" -> Seq("product of Kcd and ETpm")
//    )
    val desired =  Seq.empty[(String, Seq[String])] //todo: do we consider calculations to be definitions?
    val mentions = extractMentions(t6a)
    testDefinitionEvent(mentions, desired)
  }
  val t7a = "where KEP (typically ranging from 0.5 to 0.8) is defined as an energy extinction coefficient of " +
    "the canopy for total solar irradiance, used for partitioning E0 to EPo and ESo (Ritchie, 1998)."
    passingTest should s"find definitions from t7a: ${t7a}" taggedAs(Somebody) in {
      val desired = Seq(
        "KEP" -> Seq("energy extinction coefficient of the canopy for total solar irradiance, used for partitioning E0 to EPo and ESo") // the def will eventually be the whole sentence
      )
      val mentions = extractMentions(t7a)
      testDefinitionEvent(mentions, desired)
    }

  val t8a = "where Kcbmin is the minimum basal crop coefficient representing a dry, bare, or nearly bare soil surface."
    passingTest should s"find definitions from t8a: ${t8a}" taggedAs(Somebody) in {
      val desired = Seq(
        "Kcbmin" -> Seq("minimum basal crop coefficient representing a dry, bare, or nearly bare soil surface") //fixme: is this expanding too far?
      )
      val mentions = extractMentions(t8a)
      testDefinitionEvent(mentions, desired)
    }


  val t9a = " The primary factor causing an increase in the crop coefficient is an increase in plant cover or leaf " +
    "area (Jensen and Allen, 2016); thus, Kc is correlated with LAI."
  passingTest should s"find NO definitions from t9a: ${t9a}" taggedAs(Somebody) in {
    val desired =  Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t9a)
    testDefinitionEvent(mentions, desired)
  }

  val t10a = "Recommended values for Kcdmin and Kcdmax can be found in FAO-56, and DeJonge et al. (2012a) " +
    "recommended 0.5 < SKc < 1.0 as a typical shape to match past literature on the subject."
  passingTest should s"find NO definitions from t11a: ${t10a}" taggedAs(Somebody) in {
    val desired =  Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t10a)
    testDefinitionEvent(mentions, desired)
  }

  val t11a = "Note that Kcdmax in equation 5 is different from Kcmax in equation A6."
  passingTest should s"find NO definitions from t12a: ${t11a}" taggedAs(Somebody) in {
    val desired =  Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t11a)
    testDefinitionEvent(mentions, desired)
  }

  val t12a = "The approach uses model-simulated LAI to calculate the Kcb, which means Kcb is more dynamic and " +
    "responsive to cultivar, weather, and soil variability, as simulated by the model"
  passingTest should s"find NO definitions from t12a: ${t12a}" taggedAs(Somebody) in {
    val desired =  Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t12a)
    testDefinitionEvent(mentions, desired)
  }

  val t13a = "Because the aim of equation 8 is potential soil evaporation, Ke is obtained from equation A5 with " +
    "Kr = 1.0."
  passingTest should s"find NO definitions from t13a: ${t13a}" taggedAs(Somebody) in {
    val desired =  Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t13a)
    testDefinitionEvent(mentions, desired)

  }

  // Tests from paper: 2016-Camargo-and Kemanian-Six-crop-models differ-in-their-simulation-of water-uptake

  val t1b = "In APSIM, water uptake (Ta, mm d−1) is determined from potential transpiration demand (Tp, mm d−1), soil " +
    "water available (WA, mm d−1), and water supply (WS, mm d−1) for each ith day and soil layer as:"
  passingTest should s"find definitions from t1b: ${t1b}" taggedAs(Somebody) in {
    val desired = Seq(
      "Ta" -> Seq("water uptake"),
      "Tp" -> Seq("potential transpiration demand"),
      "WA" -> Seq("soil water available"),
      "WS" -> Seq("water supply")
    )
    val mentions = extractMentions(t1b)
    testDefinitionEvent(mentions, desired)
  }

  val t2b = "where fi is the daily fractional light interception, ETo is the daily reference evapotranspiration (mm d−1)," +
    " pwp is the water content at permanent wilting point (m3 m−3), $z is the soil layer thickness (m), and kl " +
    "is the water extraction rate, an empiric soil–root factor for the fraction of available water that can be " +
    "supplied to the plant from each rooted soil layer."
  failingTest should s"find definitions from t2b: ${t2b}" taggedAs(Somebody) in {
    val desired = Seq(
      "fi" -> Seq("daily fractional light interception"),
      "ETo" -> Seq("daily reference evapotranspiration"), //fixme: expansion is too extreme; limit
      "pwp" -> Seq("water content at permanent wilting point"),//fixme: modify lookslikeavar to accommodate lower-case letters as vars
      "$z" -> Seq("soil layer thickness"),
      "kl" -> Seq("water extraction rate", "empiric soil–root factor for the fraction of available water that can " +
        "be supplied to the plant from each rooted soil layer")
    )
    val mentions = extractMentions(t2b)
    testDefinitionEvent(mentions, desired)
  }

  val t3b = "This means that kl represents a maximum supply determined by r and the resistance to water flow " +
    "(Passioura, 1983; Monteith, 1986)"
  passingTest should s"find definitions from t3b: ${t3b}" taggedAs(Somebody) in {
    val desired = Seq(
      "kl" -> Seq("maximum supply determined by r and the resistance to water flow")
    )
    val mentions = extractMentions(t3b)
    testDefinitionEvent(mentions, desired)
  }

  val t4b = "The plant conductance is calculated by inverting the transpiration equation using a maximum expected " +
    "transpiration (Tx, mm d−1), the soil water potential at field capacity ( Sfc, J kg−1) and the leaf water " +
    "potential at the onset of stomatal closure ( Lsc, J kg−1):"
  passingTest should s"find definitions from t4b: ${t4b}" taggedAs(Somebody) in {
    val desired = Seq(
      //"plant conductance" -> Seq("inverting the transpiration equation"), // todo: do we want this one?
      "Tx" -> Seq("maximum expected transpiration"),
      "Sfc" -> Seq("soil water potential at field capacity"),
      "Lsc" -> Seq("leaf water potential at the onset of stomatal closure")
    )
    val mentions = extractMentions(t4b)
    testDefinitionEvent(mentions, desired)
  }

  val t5b = "The average soil water potential (S, J kg−1) is calculated based on a representative root length " +
    "fraction for each soil layer (fr,j):" //fixme: allow commas in var in the lookslikeavar rule? r,j are two comma-separated subscripts here.
  failingTest should s"find definitions from t5b: ${t5b}" taggedAs(Somebody) in {
    val desired = Seq(
      "S" -> Seq("average soil water potential"),
      "fr,j" -> Seq("representative root length fraction for each soil layer")
    )
    val mentions = extractMentions(t5b)
    testDefinitionEvent(mentions, desired)
  }

  val t6b = "The L is calculated using T, Cp and  ̄S ."
  passingTest should s"find NO definitions from t6b: ${t6b}" taggedAs(Somebody) in {
    val desired = Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t6b)
    testDefinitionEvent(mentions, desired)
  }

  val t7b = "If L falls below that of permanent wilting point ( Lpwp), then Ta = 0"
  passingTest should s"find definitions from t7b: ${t7b}" taggedAs(Somebody) in {
    val desired = Seq(
      "Lpwp" -> Seq("permanent wilting point") // todo: or "that of permanent wilting point" ??
    )
    val mentions = extractMentions(t7b)
    testDefinitionEvent(mentions, desired)
  }

  val t8b = "Finally, Ta is calculated using s and L, Cp and Tp:"
  passingTest should s"find NO definitions from t8b: ${t8b}" taggedAs(Somebody) in {
    val desired =  Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t8b)
    testDefinitionEvent(mentions, desired)
  }

  val t9b = "For this research Tx = 10 mm d−1, Lsc = −1100 J kg−1 and Lpwp = −2000 J kg−1."
  failingTest should s"find NO definitions from t9b: ${t9b}" taggedAs(Somebody) in {
    val desired =  Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t9b)
    testDefinitionEvent(mentions, desired)
    //fixme: without the comma after 'research', 'research' is found as the definition for Tx because of the 'sort_of_appos' rule
  }

  val t10b = "In DSSAT, root water uptake is calculated in two steps."
  passingTest should s"find NO definitions from t10b: ${t10b}" taggedAs(Somebody) in {
    val desired =  Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t10b)
    testDefinitionEvent(mentions, desired)
  }

  val t11b = "First, water uptake per unit of root length is computed in each soil layer (Url, m3 m−1 d−1) as an " +
    "exponential function that depends on:"
  passingTest should s"find definitions from t11b: ${t11b}" taggedAs(Somebody) in {
    val desired = Seq(
      "Url" -> Seq("water uptake per unit of root length") // todo: add a rule?
    )
    val mentions = extractMentions(t11b)
    testDefinitionEvent(mentions, desired)

  }
  val t12b = "Second, the maximum potential water uptake for the profile (Ux, mm d−1) is obtained by multiplying Ta,rl " +
    "times pr for each layer and summing over the soil profile:"
    passingTest should s"find definitions from t12b: ${t12b}" taggedAs(Somebody) in {
      val desired = Seq(
        "Ux" -> Seq("maximum potential water uptake for the profile") //for the profile? - not part of the concept
      )
      val mentions = extractMentions(t12b)
      testDefinitionEvent(mentions, desired)

    }
  val t13b = "where s1 and s2 are parameters of a logistic curve (9 and 0.005, respectively), and w represents the " +
    "soil limitation to water uptake of each layer."
    failingTest should s"find definitions from t13b: ${t13b}" taggedAs(Somebody) in {
      val desired = Seq(
        "s1" -> Seq("parameters of a logistic curve"),
        "s2" -> Seq("parameters of a logistic curve"),
        "w" -> Seq("soil limitation") // need to expand this to "to water uptake of each layer"
      )
      val mentions = extractMentions(t13b)
      testDefinitionEvent(mentions, desired)
    }

    // Tests from paper: 2006-Root Water Extraction and Limiting Soil Hydraulic Conditions Estimated by Numerical Simulation

  val t1c = "A convenient soil hydraulic property that will be used in this study is the matric flux potential " +
    "Mh0 (m2 d-1)"
    failingTest should s"find definitions from t1c: ${t1c}" taggedAs(Somebody) in {
      val desired = Seq(
        "Mh0" -> Seq("matric flux potential")
      )
      val mentions = extractMentions(t1c)
      testDefinitionEvent(mentions, desired)
    }

  val t2c = "where t is time (d), C is the differential water capacity (du/dh, m21), q is the water flux density " +
    "(m d21), r is the distance from the axial center (m), S is a sink or source term (d21), and H is the hydraulic " +
    "head (m)."
    failingTest should s"find definitions from t2c: ${t2c}" taggedAs(Somebody) in {
      val desired = Seq(
        "t" -> Seq("time"),
        "C" -> Seq("differential water capacity"),
        "q" -> Seq("water flux density"), //fixme: m is found as entity by definition_var_appos despite the [!entity = "B-unit"]
        "r" -> Seq("distance from the axial center"),
        "S" -> Seq("sink or source term"), //two separate concepts, not going to pass without expansion?
        "H" -> Seq("hydraulic head")
      )
      val mentions = extractMentions(t2c)
      testDefinitionEvent(mentions, desired)
    }

  val t3c = "u, ur, and us are water content, residual water content and saturated water content (m3 m-3), " +
    "respectively; h is pressure head (m); K and Ksat are hydraulic conductivity and saturated hydraulic conductivity, " +
    "respectively (m d21); and a (m21), n, and l are empirical parameters."
    failingTest should s"find definitions from t3c: ${t3c}" taggedAs(Somebody) in {
      val desired = Seq(
        "u" -> Seq("water content"),
        "ur" -> Seq("residual water content"),
        "us" -> Seq("saturated water content"),
        "h" -> Seq("pressure head"),
        "K" -> Seq("hydraulic conductivity"), //two separate concepts, not going to pass without expansion?
        "Ksat" -> Seq("saturated hydraulic conductivity"),
        "a" -> Seq("empirical parameters"),
        "n" -> Seq("empirical parameters"),
        "l" -> Seq("empirical parameters")
      )
      val mentions = extractMentions(t3c)
      testDefinitionEvent(mentions, desired)

    }
  val t4c = "Segment size (dr) was chosen smaller near the root and larger at greater distance, according to"
  passingTest should s"find definitions from t4c: ${t4c}" taggedAs(Somebody) in {
      val desired = Seq(
        "dr" -> Seq("Segment size") //fixme: filtered out by looksLikeAVar action
      )
      val mentions = extractMentions(t4c)
      testDefinitionEvent(mentions, desired)
    }

  val t5c = "in which L (m) is the root length, z (m) is the total rooted soil depth, Ap (m2) is the surface area " +
    "and Ar (m2) is the root surface area."
    failingTest should s"find definitions from t5c: ${t5c}" taggedAs(Somebody) in {
      val desired = Seq(
        "L" -> Seq("root length"),
        "z" -> Seq("total rooted soil depth"), //z is not found as concept bc it's found as B-VP: need a surface rule where var is any word but use a looksLikeAVar on it?
        "Ap" -> Seq("surface area"),
        "Ar" -> Seq("root surface area") //todo: bad parse; have to have a surface rule
      )
      val mentions = extractMentions(t5c)
      testDefinitionEvent(mentions, desired)
    }

  //fixme: this test should not be here; it would be processed with the edge case preprocessor before rule application

//    failingTest should s"find definitions from t6c: ${t6c}" taggedAs(Somebody) in {
//      val desired = Seq(
//        "T" -> Seq("daily mean air temperature"), // [C] is caught as part of the concept
//        "Tmax" -> Seq("daily maximum air temperature"),
//        "Tmin" -> Seq("daily minimum air temperature")
//      )
//      val mentions = extractMentions(t6c)
//      testDefinitionEvent(mentions, desired)
//    }

  val t7c = "with dr,min = 1028 m, dr,max = 5.1024 m, S = 0.5, r0 (m) is the root radius and rm (m) is the radius of " +
    "the root extraction zone, equal to the half-distance between roots (rm), which relates to the root density " +
    "R (m m23) as..."
  failingTest should s"find definitions from t7c: ${t7c}" taggedAs(Somebody) in {

    val desired = Seq(
      "r0" -> Seq("root radius"),
      "rm" -> Seq("radius of the root extraction zone"),
      "R" -> Seq("root density")
    )
    val mentions = extractMentions(t7c)
    testDefinitionEvent(mentions, desired)
  }

  val t8c = "where p is the iteration level."
  passingTest should s"find definitions from t8c: ${t8c}" taggedAs(Somebody) in {
    val desired = Seq(
      "p" -> Seq("iteration level")
    )
    val mentions = extractMentions(t8c)
    testDefinitionEvent(mentions, desired)
  }


  // Tests from paper: 2005-THE ASCE STANDARDIZED REFERENCE EVAPOTRANSPIRATION EQUATION

  val t1d = "The density of water (ρw) is taken as 1.0 Mg m-3."
  passingTest should s"find definitions from t1d: ${t1d}" taggedAs(Somebody) in {
    val desired = Seq(
      "ρw" -> Seq("density of water")
    )
    val mentions = extractMentions(t1d)
    testDefinitionEvent(mentions, desired)
  }

  val t1e = "Since eS is not a linear function of temperature"
  passingTest should s"find NO definitions from t1e: ${t1e}" taggedAs(Somebody) in {
    val desired = Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t5a)
    testDefinitionEvent(mentions, desired)
  }


//  val t9c = "Assuming no sink or source (S = 0) and no gravitational or osmotic component (H = h), Eq. [4] reduces to..."
//  failingTest should s"find definitions from t9c: ${t9c}" taggedAs(Somebody) in {
//    val desired = Seq(
//
//    )
//    val mentions = extractMentions(t9c)
//    testDefinitionEvent(mentions, desired)
//  }

// Tests from paper: 2020-08-04-CHIME-documentation

  val t1f = "The CHIME (COVID-19 Hospital Impact Model for Epidemics) App"
  failingTest should s"find definitions from t1f: ${t1f}" taggedAs(Somebody) in {
    val desired = Seq(
      "CHIME" -> Seq("COVID-19 Hospital Impact Model for Epidemics")
    )
    val mentions = extractMentions(t1f)
    testDefinitionEvent(mentions, desired)
  }

  val t2f = "The model consists of individuals who are either Susceptible (S), Infected (I), or Recovered (R)."
  failingTest should s"find definitions from t2f: ${t2f}" taggedAs(Somebody) in {
    val desired = Seq(
      "S" -> Seq("either Susceptible"), //fixme: it should be just Susceptible (either should be deleted)
      "I" -> Seq("Infected"),
      "R" -> Seq("Recovered") //fixme: Recovered is not captured as a concept
    )
    val mentions = extractMentions(t2f)
    testDefinitionEvent(mentions, desired)
  }

  val t3f = "β can be interpreted as the effective contact rate: β=τ×c which is the transmissibility τ multiplied by the average number of people exposed c."
  passingTest should s"find definitions from t3f: ${t3f}" taggedAs(Somebody) in {
    val desired = Seq(
      "β" -> Seq("effective contact rate"),
      "τ" -> Seq("transmissibility"),
      "c." -> Seq("average number of people exposed") //fixme: period(.) should be deleted after c & needs to check if it is average number or just number
    )
    val mentions = extractMentions(t3f)
    testDefinitionEvent(mentions, desired)
  }

  val t4f = "γ is the inverse of the mean recovery time"
  passingTest should s"find definitions from t4f: ${t4f}" taggedAs(Somebody) in {
    val desired = Seq(
      "γ" -> Seq("inverse of the mean recovery time")
    )
    val mentions = extractMentions(t4f)
    testDefinitionEvent(mentions, desired)
  }

  val t5f = "An important descriptive parameter is the basic reproduction number, or R0."
  passingTest should s"find definitions from t5f: ${t5f}" taggedAs(Somebody) in {
    val desired = Seq(
      "R0" -> Seq("basic reproduction number")
    )
    val mentions = extractMentions(t5f)
    testDefinitionEvent(mentions, desired)
  }

  val t6f = "If this happens at time t, then the effective reproduction rate is Rt, which will be lower than R0."
  passingTest should s"find definitions from t6f: ${t6f}" taggedAs(Somebody) in {
    val desired = Seq(
      "t" -> Seq("time"),
      "Rt" -> Seq("effective reproduction rate")
    )
    val mentions = extractMentions(t6f)
    testDefinitionEvent(mentions, desired)
  }

  val t7f = "The AHA says to expect a doubling time Td of 7-10 days."
  passingTest should s"find definitions from t7f: ${t7f}" taggedAs(Somebody) in {
    val desired = Seq(
      "Td" -> Seq("doubling time")
    )
    val mentions = extractMentions(t7f)
    testDefinitionEvent(mentions, desired)
  }

  val t8f = "Since the rate of new infections in the SIR model is g = βS − γ and we've already computed γ,"
  failingTest should s"find definitions from t8f: ${t8f}" taggedAs(Somebody) in {
    val desired = Seq(
      "g" -> Seq("rate of new infections")
    )
    val mentions = extractMentions(t8f)
    testDefinitionEvent(mentions, desired)
  }

  val t9f = "This is the initial S (Susceptible) input in the SIR model."
  passingTest should s"find definitions from t9f: ${t9f}" taggedAs(Somebody) in {
    val desired = Seq(
      "S" -> Seq("Susceptible")
    )
    val mentions = extractMentions(t9f)
    testDefinitionEvent(mentions, desired)
  }

  val t10f = "This will affect projections for the number infected and the numbers requiring hospitalization, intensive care (ICU), and ventilation."
  passingTest should s"find definitions from t10f: ${t10f}" taggedAs(Somebody) in {
    val desired = Seq(
      "ICU" -> Seq("intensive care")
    )
    val mentions = extractMentions(t10f)
    testDefinitionEvent(mentions, desired)
  }

  val t11f = "The number of patients currently hospitalized with COVID-19 at your hospital(s)."
  passingTest should s"find NO definitions from t11f: ${t11f}" taggedAs(Somebody) in {
    val desired =  Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t11f)
    testDefinitionEvent(mentions, desired)
  }

// Tests from paper: 2003-A_double_epidemic_model_for_the_SARS_propagation

  val t1g = "the susceptibles, S, who can catch the disease; the infectives, I, who have the disease and can transmit it; " +
    "and the removed class, R, namely those  who  have  either  had  the  disease, or are recovered, immune or isolated until recovered."
  failingTest should s"find definitions from t1g: ${t1g}" taggedAs(Somebody) in {
    val desired =  Seq(
      "S" -> Seq("susceptibles who can catch the disease"), // fixme: [error] Vector((S,susceptibles)) did not contain element (S,susceptibles who can catch the disease) (TestUtils.scala:123)
      "I" -> Seq("infectives who have the disease and can transmit it"),
      "R" -> Seq("removed class namely those who have either had the disease, or are recovered, immune or isolated until recovered"),
    )
    val mentions = extractMentions(t1g)
    testDefinitionEvent(mentions, desired)
  }

    val t2g = "Let S(t), I(t) and R(t) be the number of individuals in each of the corresponding class at time t. "
  failingTest should s"find definitions from t2g: ${t2g}" taggedAs(Somebody) in {
    val desired =  Seq(
      "S(t)" -> Seq("number of individuals in class at time t"),
      "I(t)" -> Seq("number of individuals in class at time t"),
      "R(t)" -> Seq("number of individuals in class at time t"),
      "t" -> Seq("time")
    )
    val mentions = extractMentions(t2g)
    testDefinitionEvent(mentions, desired)
  }

    val t3g = "This new model will be called SEIRP model (E stands for the Exposed class while P stands for protection)" +
    "which can be considered as a variant of the standard SIR."
  failingTest should s"find definitions from t3g: ${t3g}" taggedAs(Somebody) in {
    val desired =  Seq(
      "SEIRP" -> Seq("variant of the standard SIR") // todo: check if this is the one that should be extracted here. ask Paul.
    )
    val mentions = extractMentions(t3g)
    testDefinitionEvent(mentions, desired)
  }

    val t4g = "where r is the infection rate and a the removal rate of infectives."
  failingTest should s"find definitions from t4g: ${t4g}" taggedAs(Somebody) in {
    val desired =  Seq(
      "r" -> Seq("infection rate"),
      "a" -> Seq("removal rate of infectives") // fixme: "removal rate of infectives" is not extracted as a definition
    )
    val mentions = extractMentions(t4g)
    testDefinitionEvent(mentions, desired)
  }


// Tests from unknown papers

    val t1h = "where Rn is the net radiation, H the sensible heat, G the soil heat flux and λET the latent heat flux."
  failingTest should s"find definitions from t1h: ${t1h}" taggedAs(Somebody) in {
    val desired =  Seq(
      "Rn" -> Seq("net radiation"),
      "H" -> Seq("sensible heat"), //todo: H, G, λET should be annotated as variables.
      "G" -> Seq("soil heat flux"),
      "λET" -> Seq("latent heat flux")
    )
    val mentions = extractMentions(t1h)
    testDefinitionEvent(mentions, desired)
  }

    val t2h = "The only factors affecting ETo are climatic parameters."
  passingTest should s"find NO definitions from t2h: ${t2h}" taggedAs(Somebody) in {
    val desired =  Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t2h)
    testDefinitionEvent(mentions, desired)
  }

    val t3h = "The crop evapotranspiration under standard conditions, denoted as ETc, " +
      "is the evapotranspiration from disease-free, well-fertilized crops, grown in large fields, " +
      "under optimum soil water conditions, and achieving full production under the given climatic conditions."
  failingTest should s"find definitions from t3h: ${t3h}" taggedAs(Somebody) in {
    val desired =  Seq(
      "ETc" -> Seq("crop evapotranspiration under standard conditions"),
      "ETc" -> Seq("evapotranspiration from disease-free, well-fertilized crops, grown in large fields, " + // fixme: this should be captured as the definition.
      "under optimum soil water conditions, and achieving full production under the given climatic conditions") // todo: need to allow two definitions per variable.
    )
    val mentions = extractMentions(t3h)
    testDefinitionEvent(mentions, desired)
  }

// Tests from paper: Covid_Act_Now_Model_Reference

    val t1i = "Susceptible (S) individuals may become exposed (E) to the virus, then infected (I) at varying " +
      "levels of disease severity (mild, moderate, or severe, illustrated as I1, I2, and I3 respectively)."
  failingTest should s"find definitions from t1i: ${t1i}" taggedAs(Somebody) in {
    val desired =  Seq(
      "S" -> Seq("Susceptible"),
      "E" -> Seq("exposed"), // fixme: Definitions of E, I, I1, I2, I3 are not extracted
      "I" -> Seq("infected"),
      "I1" -> Seq("mild"),
      "I2" -> Seq("moderate"),
      "I3" -> Seq("severe")
    )
    val mentions = extractMentions(t1i)
    testDefinitionEvent(mentions, desired)
  }

// Tests from paper: ideal_sir_model_without_vital_dynamics

    val t1j = "This idea can probably be more readily seen if we say that the typical time between contacts is Tc = β-1, " +
      "and the typical time until recovery is Tr = γ-1."
  failingTest should s"find definitions from t1j: ${t1j}" taggedAs(Somebody) in {
    val desired =  Seq(
      "Tc" -> Seq("typical time between contacts"), // fixme: both of the definitions were not extracted
      "Tr" -> Seq("typical time until recovery")
    )
    val mentions = extractMentions(t1j)
    testDefinitionEvent(mentions, desired)
  }

// Tests from paper: PT-2012-ET Measurement and Estimation Using Modified PT in Maise with Mulching-petpt_2012

    val t1k = "where θ is soil water content in 0–1.0 m soil (cm3 cm−3), θF is field capacity (cm3 cm−3) and θw is wilting point (cm3 cm−3)."
  failingTest should s"find definitions from t1k: ${t1k}" taggedAs(Somebody) in {
    val desired =  Seq(
      "θ" -> Seq("soil water content in 0–1.0 m soil"),
      "θF" -> Seq("field capacity"), // fixme: "F" only is captured as the variable here. Should be fixed to capture θF as one variable.
      "θw" -> Seq("wilting point")   // fixme: Definition of "θw" is not extracted.
    )
    val mentions = extractMentions(t1k)
    testDefinitionEvent(mentions, desired)
  }

    val t2k = "κ, canopy extinction coefficient of radiation, is dependent on foliage orientation and solar zenith angle, 0.45 for this study (Campbell and Norman, 1998)."
  failingTest should s"find definitions from t2k: ${t2k}" taggedAs(Somebody) in {
    val desired =  Seq(
      "κ" -> Seq("canopy extinction coefficient of radiation") // fixme: Definition of "κ" is not extracted.
    )
    val mentions = extractMentions(t2k)
    testDefinitionEvent(mentions, desired)
  }

}
