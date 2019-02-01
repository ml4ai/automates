package org.clulab.aske.automates.text

import org.clulab.aske.automates.TestUtils._

class TestDefinitions extends ExtractionTest {

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
  passingTest should s"extract definitions from t2a: ${t2a}" taggedAs(Somebody) in {
    val desired = Seq(
      "LAI" -> Seq("simulated leaf area index"),
      "EORATIO" -> Seq("maximum Kcs at LAI = 6.0"),
      "Kcs" -> Seq("DSSAT-CSM crop coefficient") //todo: include model?
    )
    val mentions = extractMentions(t2a)
    testDefinitionEvent(mentions, desired)
  }

  val t3a = "where Kcdmin is the minimum crop coefficient or Kcd at LAI = 0, Kcdmax is the maximum crop " +
    "coefficient at high LAI, and SKc is a shaping parameter that determines the shape of the Kcd versus LAI curve."
  passingTest should s"find definitions from t3a: ${t3a}" taggedAs(Somebody) in {
    val desired = Seq(
      "Kcdmin" -> Seq("minimum crop coefficient"),
      "Kcdmax" -> Seq("maximum crop coefficient"), // Seq("maximum crop coefficient at high LAI"), fixme?
      "SKc" -> Seq("shaping parameter")
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

  val t5a = "The ESo calculation in equation 4 is implemented for the CSM-CERESMaize model and several other crop models."
  passingTest should s"find NO definitions from t5a: ${t5a}" taggedAs(Somebody) in {
    val desired = Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t5a)
    testDefinitionEvent(mentions, desired)
  }

  val t6a = "Similar to equation 2, E0 is calculated as the product of Kcd and ETpm."
  passingTest should s"find definitions from t6a: ${t6a}" taggedAs(Somebody) in {
    val desired = Seq(
      "E0" -> Seq("product of Kcd and ETpm")
    )
    val mentions = extractMentions(t6a)
    testDefinitionEvent(mentions, desired)
  }
  val t7a = "where KEP (typically ranging from 0.5 to 0.8) is defined as an energy extinction coefficient of " +
    "the canopy for total solar irradiance, used for partitioning E0 to EPo and ESo (Ritchie, 1998)."
    passingTest should s"find definitions from t7a: ${t7a}" taggedAs(Somebody) in {
      val desired = Seq(
        "KEP" -> Seq("energy extinction coefficient") // the def will eventually be the whole sentence
      )
      val mentions = extractMentions(t7a)
      testDefinitionEvent(mentions, desired)
    }

  val t8a = "where Kcbmin is the minimum basal crop coefficient representing a dry, bare, or nearly bare soil surface."
    passingTest should s"find definitions from t8a: ${t8a}" taggedAs(Somebody) in {
      val desired = Seq(
        "Kcbmin" -> Seq("minimum basal crop coefficient")
      )
      val mentions = extractMentions(t8a)
      testDefinitionEvent(mentions, desired)
    }

  val t9a = "where Kcbmin is the minimum basal crop coefficient representing a dry, bare, or nearly bare soil surface."
    passingTest should s"find definitions from t9a: ${t9a}" taggedAs(Somebody) in {
      val desired = Seq(
        "Kcbmin" -> Seq("minimum basal crop coefficient")
      )
      val mentions = extractMentions(t9a)
      testDefinitionEvent(mentions, desired)
    }

  val t10a = " The primary factor causing an increase in the crop coefficient is an increase in plant cover or leaf " +
    "area (Jensen and Allen, 2016); thus, Kc is correlated with LAI."
  passingTest should s"find NO definitions from t10a: ${t10a}" taggedAs(Somebody) in {
    val desired =  Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t10a)
    testDefinitionEvent(mentions, desired)
  }

  val t11a = "Recommended values for Kcdmin and Kcdmax can be found in FAO-56, and DeJonge et al. (2012a) " +
    "recommended 0.5 < SKc < 1.0 as a typical shape to match past literature on the subject."
  passingTest should s"find NO definitions from t11a: ${t11a}" taggedAs(Somebody) in {
    val desired =  Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t11a)
    testDefinitionEvent(mentions, desired)
  }

  val t12a = "Note that Kcdmax in equation 5 is different from Kcmax in equation A6."
  passingTest should s"find NO definitions from t12a: ${t12a}" taggedAs(Somebody) in {
    val desired =  Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t12a)
    testDefinitionEvent(mentions, desired)
  }

  val t13a = "The approach uses model-simulated LAI to calculate the Kcb, which means Kcb is more dynamic and " +
    "responsive to cultivar, weather, and soil variability, as simulated by the model"
  passingTest should s"find NO definitions from t13a: ${t13a}" taggedAs(Somebody) in {
    val desired =  Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t13a)
    testDefinitionEvent(mentions, desired)
  }

  val t14a = "Because the aim of equation 8 is potential soil evaporation, Ke is obtained from equation A5 with " +
    "Kr = 1.0."
  passingTest should s"find NO definitions from t14a: ${t14a}" taggedAs(Somebody) in {
    val desired =  Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t14a)
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
    " \\\"pwp is the water content at permanent wilting point (m3 m−3), $z is the soil layer thickness (m), and kl " +
    "is the water extraction rate, an empiric soil–root factor for the fraction of available water that can be " +
    "supplied to the plant from each rooted soil layer."
  passingTest should s"find definitions from t2b: ${t2b}" taggedAs(Somebody) in {
    val desired = Seq(
      "fi" -> Seq("daily fractional light interception"),
      "ETo" -> Seq("daily reference evapotranspiration"),
      "pwp" -> Seq("water content at permanent wilting point"),
      "$z" -> Seq("soil layer thickness"),
      "kl" -> Seq("water extraction rate", "empiric soil–root factor for the fraction of available water that can " +
        "be supplied to the plant from each rooted soil layer")
    )
    val mentions = extractMentions(t2b)
    testDefinitionEvent(mentions, desired)
  }

  val t3b = "This means that kl represents a maximum supply determined by !r and the resistance to water flow " +
    "(Passioura, 1983; Monteith, 1986)"
  passingTest should s"find definitions from t3b: ${t3b}" taggedAs(Somebody) in {
    val desired = Seq(
      "kl" -> Seq("maximum supply determined by !r and the resistance to water flow")
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

  val t5b = "The average soil water potential ( ̄S , J kg−1) is calculated based on a representative root length " +
    "fraction for each soil layer (fr,j):"
  passingTest should s"find definitions from t5b: ${t5b}" taggedAs(Somebody) in {
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
  passingTest should s"find NO definitions from t9b: ${t9b}" taggedAs(Somebody) in {
    val desired =  Seq.empty[(String, Seq[String])]
    val mentions = extractMentions(t9b)
    testDefinitionEvent(mentions, desired)
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
      "Url" -> Seq("water uptake per unit of root length") // todo: is this right ??
    )
    val mentions = extractMentions(t11b)
    testDefinitionEvent(mentions, desired)

  }
  val t12b = "Second, the maximum potential water uptake for the profile (Ux, mm d−1) is obtained by multiplying Ta,rl " +
    "times pr for each layer and summing over the soil profile:"
    passingTest should s"find definitions from t12b: ${t12b}" taggedAs(Somebody) in {
      val desired = Seq(
        "Ux" -> Seq("maximum potential water uptake") //for the profile? - not part of the concept
      )
      val mentions = extractMentions(t12b)
      testDefinitionEvent(mentions, desired)

    }
  val t13b = "where s1 and s2 are parameters of a logistic curve (9 and 0.005, respectively), and w represents the " +
    "soil limitation to water uptake of each layer."
    passingTest should s"find definitions from t13b: ${t13b}" taggedAs(Somebody) in {
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
    passingTest should s"find definitions from t1c: ${t1c}" taggedAs(Somebody) in {
      val desired = Seq(
        "Mh0" -> Seq("matric flux potential")
      )
      val mentions = extractMentions(t1c)
      testDefinitionEvent(mentions, desired)
    }

  val t2c = "where t is time (d), C is the differential water capacity (du/dh, m21), q is the water flux density " +
    "(m d21), r is the distance from the axial center (m), S is a sink or source term (d21), and H is the hydraulic " +
    "head (m)."
    passingTest should s"find definitions from t2c: ${t2c}" taggedAs(Somebody) in {
      val desired = Seq(
        "t" -> Seq("time"),
        "C" -> Seq("differential water capacity"),
        "q" -> Seq("water flux density"),
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
    passingTest should s"find definitions from t3c: ${t3c}" taggedAs(Somebody) in {
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
        "dr" -> Seq("Segment size")
      )
      val mentions = extractMentions(t4c)
      testDefinitionEvent(mentions, desired)
    }

  val t5c = "in which L (m) is the root length, z (m) is the total rooted soil depth, Ap (m2) is the surface area " +
    "and Ar (m2) is the root surface area."
    passingTest should s"find definitions from t5c: ${t5c}" taggedAs(Somebody) in {
      val desired = Seq(
        "L" -> Seq("root length"),
        "z" -> Seq("total rooted soil depth"),
        "Ap" -> Seq("surface area"),
        "Ar" -> Seq("root surface area")
      )
      val mentions = extractMentions(t5c)
      testDefinitionEvent(mentions, desired)
    }

  val t6c = "where: T = daily mean air temperature [°C] Tmax = daily maximum air temperature [°C] Tmin = daily " +
    "minimum air temperature [°C]"
    passingTest should s"find definitions from t6c: ${t6c}" taggedAs(Somebody) in {
      val desired = Seq(
        "T" -> Seq("daily mean air temperature"), // [C] is caught as part of the concept
        "Tmax" -> Seq("daily maximum air temperature"),
        "Tmin" -> Seq("daily minimum air temperature")
      )
      val mentions = extractMentions(t6c)
      testDefinitionEvent(mentions, desired)
    }

  val t7c = "with dr,min = 1028 m, dr,max = 5.1024 m, S = 0.5, r0 (m) is the root radius and rm (m) is the radius of " +
    "the root extraction zone, equal to the half-distance between roots (rm), which relates to the root density " +
    "R (m m23) as..."
  passingTest should s"find definitions from t7c: ${t7c}" taggedAs(Somebody) in {

    val desired = Seq(
      "r0" -> Seq("root radius"),
      "rm" -> Seq("radius of the root extraction zone"),
      "R" -> Seq("root density"),
    )
    val mentions = extractMentions(t7c)
    testDefinitionEvent(mentions, desired)
  }

  val t8c = "where p is the iteration level."
  passingTest should s"find definitions from t8c: ${t8c}" taggedAs(Somebody) in {
    val desired = Seq(
      "r0" -> Seq("root radius"),
      "rm" -> Seq("radius of the root extraction zone"),
      "R" -> Seq("root density"),
    )
    val mentions = extractMentions(t8c)
    testDefinitionEvent(mentions, desired)
  }

  val t9c = "Assuming no sink or source (S = 0) and no gravitational or osmotic component (H = h), Eq. [4] reduces to..."
  passingTest should s"find definitions from t9c: ${t9c}" taggedAs(Somebody) in {
    val desired = Seq(
      "r0" -> Seq("root radius"),
      "rm" -> Seq("radius of the root extraction zone"),
      "R" -> Seq("root density"),
    )
    val mentions = extractMentions(t9c)
    testDefinitionEvent(mentions, desired)
  }

}
