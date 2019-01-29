package org.clulab.aske.automates.text

import org.clulab.aske.automates.TestUtils._

class TestDefinitions extends ExtractionTest {

  // Tests from paper: 2017-IMPLEMENTING STANDARDIZED REFERENCE EVAPOTRANSPIRATION AND DUAL CROP COEFFICIENT APPROACH IN THE DSSAT CROPPING SYSTEM MODEL

  val t1 = "Crop coefficients (Kcs) are calculated for the current Penman-Monteith ET approach in DSSAT-CSM as:"
  passingTest should s"extract definitions from t1: ${t1}" taggedAs(Somebody) in {
    val desired = Map(
      "Kcs" -> Seq("Crop coefficients")
    )
    val mentions = extractMentions(t1)
    testDefinitionEvent(mentions, desired)
  }

  val t2 = "where LAI is the simulated leaf area index, EORATIO is defined as the maximum Kcs at LAI = 6.0 " +
    "(Sau et al., 2004; Thorp et al., 2010), and Kcs is the DSSAT-CSM crop coefficient."
  passingTest should "extract definitions from t2" taggedAs(Somebody) in {
    val desired = Map(
      "LAI" -> Seq("simulated leaf area index"),
      "EORATIO" -> Seq("maximum Kcs at LAI = 6.0")
    )
    val mentions = extractMentions(t2)
    testDefinitionEvent(mentions, desired)
  }

  val t3 = "where Kcdmin is the minimum crop coefficient or Kcd at LAI = 0, Kcdmax is the maximum crop " +
    "coefficient at high LAI, and SKc is a shaping parameter that determines the shape of the Kcd versus LAI curve."
  passingTest should "find definitions from t3" taggedAs(Somebody) in {
    val desired = Map(
      "Kcdmin" -> Seq("minimum crop coefficient"),
      "Kcdmax" -> Seq("maximum crop coefficient"), // Seq("maximum crop coefficient at high LAI"), fixme?
      "SKc" -> Seq("shaping parameter")
    )
    val mentions = extractMentions(t3)
    testDefinitionEvent(mentions, desired)
  }

  val t4 = "DSSAT-CSM employs the following formula for calculation of E0 (potential crop ET):"
  passingTest should "extract definitions from t4" taggedAs(Somebody) in {
    val desired = Map(
      "E0" -> Seq("potential crop ET")
    )
    val mentions = extractMentions(t4)
    testDefinitionEvent(mentions, desired)
  }

  val t5 = "The ESo calculation in equation 4 is implemented for the CSM-CERESMaize model and several other crop models."
  passingTest should "find NO definitions from t5" taggedAs(Somebody) in {
    val desired = Map.empty[String, Seq[String]]
    val mentions = extractMentions(t5)
    testDefinitionEvent(mentions, desired)
  }

  val t6 = "Similar to equation 2, E0 is calculated as the product of Kcd and ETpm."
  passingTest should "find definitions from t6" taggedAs(Somebody) in {
    val desired = Map(
      "E0" -> Seq("product of Kcd and ETpm")
    )
    val mentions = extractMentions(t6)
    testDefinitionEvent(mentions, desired)
  }
  val t7 = "where KEP (typically ranging from 0.5 to 0.8) is defined as an energy extinction coefficient of " +
    "the canopy for total solar irradiance, used for partitioning E0 to EPo and ESo (Ritchie, 1998)."
    passingTest should "find definitions from t7" taggedAs(Somebody) in {
      val desired = Map(
        "KEP" -> Seq("energy extinction coefficient") // the def will eventually be the whole sentence
      )
      val mentions = extractMentions(t7)
      testDefinitionEvent(mentions, desired)
    }

  val t8 = "where Kcbmin is the minimum basal crop coefficient representing a dry, bare, or nearly bare soil surface."
    passingTest should "find definitions from t8" taggedAs(Somebody) in {
      val desired = Map(
        "Kcbmin" -> Seq("minimum basal crop coefficient")
      )
      val mentions = extractMentions(t8)
      testDefinitionEvent(mentions, desired)
    }

  val t9 = "where Kcbmin is the minimum basal crop coefficient representing a dry, bare, or nearly bare soil surface."
    passingTest should "find definitions from t9" taggedAs(Somebody) in {
      val desired = Map(
        "Kcbmin" -> Seq("minimum basal crop coefficient")
      )
      val mentions = extractMentions(t9)
      testDefinitionEvent(mentions, desired)
    }

  val t10 = " The primary factor causing an increase in the crop coefficient is an increase in plant cover or leaf " +
    "area (Jensen and Allen, 2016); thus, Kc is correlated with LAI."
  passingTest should "find NO definitions from t10" taggedAs(Somebody) in {
    val desired =  Map.empty[String, Seq[String]]
    val mentions = extractMentions(t10)
    testDefinitionEvent(mentions, desired)
  }

  val t11 = "Recommended values for Kcdmin and Kcdmax can be found in FAO-56, and DeJonge et al. (2012a) " +
    "recommended 0.5 < SKc < 1.0 as a typical shape to match past literature on the subject."
  passingTest should "find NO definitions from t11" taggedAs(Somebody) in {
    val desired =  Map.empty[String, Seq[String]]
    val mentions = extractMentions(t11)
    testDefinitionEvent(mentions, desired)
  }

  val t12 = "Note that Kcdmax in equation 5 is different from Kcmax in equation A6."
  passingTest should "find NO definitions from t12" taggedAs(Somebody) in {
    val desired =  Map.empty[String, Seq[String]]
    val mentions = extractMentions(t12)
    testDefinitionEvent(mentions, desired)
  }

  val t13 = "The approach uses model-simulated LAI to calculate the Kcb, which means Kcb is more dynamic and " +
    "responsive to cultivar, weather, and soil variability, as simulated by the model"
  passingTest should "find NO definitions from t13" taggedAs(Somebody) in {
    val desired =  Map.empty[String, Seq[String]]
    val mentions = extractMentions(t13)
    testDefinitionEvent(mentions, desired)
  }

  val t14 = "Because the aim of equation 8 is potential soil evaporation, Ke is obtained from equation A5 with " +
    "Kr = 1.0."
  passingTest should "find NO definitions from t14" taggedAs(Somebody) in {
    val desired =  Map.empty[String, Seq[String]]
    val mentions = extractMentions(t14)
    testDefinitionEvent(mentions, desired)
  }


  // Tests from paper: 2016-Camargo-and Kemanian-Six-crop-models differ-in-their-simulation-of water-uptake

  val t15 = "In APSIM, water uptake (Ta, mm d−1) is determined from potential transpiration demand (Tp, mm d−1), soil " +
    "water available (WA, mm d−1), and water supply (WS, mm d−1) for each ith day and soil layer as:"
  passingTest should "find definitions from t15" taggedAs(Somebody) in {
    val desired = Map(
      "Ta" -> Seq("water uptake"),
      "Tp" -> Seq("potential transpiration demand"),
      "WA" -> Seq("soil water available"),
      "WS" -> Seq("water supply")
    )
    val mentions = extractMentions(t15)
    testDefinitionEvent(mentions, desired)
  }

  val t16 = "where fi is the daily fractional light interception, ETo is the daily reference evapotranspiration (mm d−1)," +
    " \\\"pwp is the water content at permanent wilting point (m3 m−3), $z is the soil layer thickness (m), and kl " +
    "is the water extraction rate, an empiric soil–root factor for the fraction of available water that can be " +
    "supplied to the plant from each rooted soil layer."
  passingTest should s"find definitions from t16: ${t16}" taggedAs(Somebody) in {
    val desired = Map(
      "fi" -> Seq("daily fractional light interception"),
      "ETo" -> Seq("daily reference evapotranspiration"),
      "pwp" -> Seq("water content at permanent wilting point"),
      "$z" -> Seq("soil layer thickness"),
      "kl" -> Seq("water extraction rate", "empiric soil–root factor for the fraction of available water that can " +
        "be supplied to the plant from each rooted soil layer")
    )
    val mentions = extractMentions(t16)
    testDefinitionEvent(mentions, desired)
  }

  val t17 = "This means that kl represents a maximum supply determined by !r and the resistance to water flow " +
    "(Passioura, 1983; Monteith, 1986)"
  passingTest should "find definitions from t17" taggedAs(Somebody) in {
    val desired = Map(
      "kl" -> Seq("maximum supply determined by !r and the resistance to water flow")
    )
    val mentions = extractMentions(t17)
    testDefinitionEvent(mentions, desired)
  }

  val t18 = "The plant conductance is calculated by inverting the transpiration equation using a maximum expected " +
    "transpiration (Tx, mm d−1), the soil water potential at field capacity ( Sfc, J kg−1) and the leaf water " +
    "potential at the onset of stomatal closure ( Lsc, J kg−1):"
  passingTest should "find definitions from t18" taggedAs(Somebody) in {
    val desired = Map(
      //"plant conductance" -> Seq("inverting the transpiration equation"), // todo: do we want this one?
      "Tx" -> Seq("maximum expected transpiration"),
      "Sfc" -> Seq("soil water potential at field capacity"),
      "Lsc" -> Seq("leaf water potential at the onset of stomatal closure")
    )
    val mentions = extractMentions(t18)
    testDefinitionEvent(mentions, desired)
  }

  val t19 = "The average soil water potential ( ̄S , J kg−1) is calculated based on a representative root length " +
    "fraction for each soil layer (fr,j):"
  passingTest should "find definitions from t19" taggedAs(Somebody) in {
    val desired = Map(
      "S" -> Seq("average soil water potential"),
      "fr,j" -> Seq("representative root length fraction for each soil layer")
    )
    val mentions = extractMentions(t19)
    testDefinitionEvent(mentions, desired)
  }

  val t20 = "The L is calculated using T, Cp and  ̄S ."
  passingTest should "find NO definitions from t20" taggedAs(Somebody) in {
    val desired = Map.empty[String, Seq[String]]
    val mentions = extractMentions(t20)
    testDefinitionEvent(mentions, desired)
  }

  val t21 = "If L falls below that of permanent wilting point ( Lpwp), then Ta = 0"
  passingTest should "find definitions from t21" taggedAs(Somebody) in {
    val desired = Map(
      "Lpwp" -> Seq("permanent wilting point") // todo: or "that of permanent wilting point" ??
    )
    val mentions = extractMentions(t21)
    testDefinitionEvent(mentions, desired)
  }

  val t22 = "Finally, Ta is calculated using s and L, Cp and Tp:"
  passingTest should "find NO definitions from t22" taggedAs(Somebody) in {
    val desired =  Map.empty[String, Seq[String]]
    val mentions = extractMentions(t22)
    testDefinitionEvent(mentions, desired)
  }

  val t23 = "For this research Tx = 10 mm d−1, Lsc = −1100 J kg−1 and Lpwp = −2000 J kg−1."
  passingTest should "find NO definitions from t23" taggedAs(Somebody) in {
    val desired =  Map.empty[String, Seq[String]]
    val mentions = extractMentions(t23)
    testDefinitionEvent(mentions, desired)
  }

  val t24 = "In DSSAT, root water uptake is calculated in two steps."
  passingTest should "find NO definitions from t24" taggedAs(Somebody) in {
    val desired =  Map.empty[String, Seq[String]]
    val mentions = extractMentions(t24)
    testDefinitionEvent(mentions, desired)
  }

  val t25 = "First, water uptake per unit of root length is computed in each soil layer (Url, m3 m−1 d−1) as an " +
    "exponential function that depends on:"
  passingTest should "find definitions from t25" taggedAs(Somebody) in {
    val desired = Map(
      "Url" -> Seq("water uptake per unit of root length") // todo: is this right ??
    )
    val mentions = extractMentions(t25)
    testDefinitionEvent(mentions, desired)

  }
  val t26 = "Second, the maximum potential water uptake for the profile (Ux, mm d−1) is obtained by multiplying Ta,rl " +
    "times pr for each layer and summing over the soil profile:"
    passingTest should "find definitions from t26" taggedAs(Somebody) in {
      val desired = Map(
        "Ux" -> Seq("maximum potential water uptake") //for the profile? - not part of the concept
      )
      val mentions = extractMentions(t26)
      testDefinitionEvent(mentions, desired)

    }
  val t27 = "where s1 and s2 are parameters of a logistic curve (9 and 0.005, respectively), and w represents the " +
    "soil limitation to water uptake of each layer."
    passingTest should "find definitions from t27" taggedAs(Somebody) in {
      val desired = Map(
        "s1" -> Seq("parameters of a logistic curve"),
        "s2" -> Seq("parameters of a logistic curve"),
        "w" -> Seq("soil limitation") // need to expand this to "to water uptake of each layer"
      )
      val mentions = extractMentions(t27)
      testDefinitionEvent(mentions, desired)
    }

    // Tests from paper: 2006-Root Water Extraction and Limiting Soil Hydraulic Conditions Estimated by Numerical Simulation

  val t28 = "A convenient soil hydraulic property that will be used in this study is the matric flux potential " +
    "Mh0 (m2 d-1)"
    passingTest should "find definitions from t28" taggedAs(Somebody) in {
      val desired = Map(
        "Mh0" -> Seq("matric flux potential")
      )
      val mentions = extractMentions(t28)
      testDefinitionEvent(mentions, desired)
    }

  val t29 = "where t is time (d), C is the differential water capacity (du/dh, m21), q is the water flux density " +
    "(m d21), r is the distance from the axial center (m), S is a sink or source term (d21), and H is the hydraulic " +
    "head (m)."
    passingTest should "find definitions from t29" taggedAs(Somebody) in {
      val desired = Map(
        "t" -> Seq("time"),
        "C" -> Seq("differential water capacity"),
        "q" -> Seq("water flux density"),
        "r" -> Seq("distance from the axial center"),
        "S" -> Seq("sink or source term"), //two separate concepts, not going to pass without expansion?
        "H" -> Seq("hydraulic head")
      )
      val mentions = extractMentions(t29)
      testDefinitionEvent(mentions, desired)
    }

  val t30 = "u, ur, and us are water content, residual water content and saturated water content (m3 m-3), " +
    "respectively; h is pressure head (m); K and Ksat are hydraulic conductivity and saturated hydraulic conductivity, " +
    "respectively (m d21); and a (m21), n, and l are empirical parameters."
    passingTest should "find definitions from t30" taggedAs(Somebody) in {
      val desired = Map(
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
      val mentions = extractMentions(t30)
      testDefinitionEvent(mentions, desired)

    }
  val t31 = "Segment size (dr) was chosen smaller near the root and larger at greater distance, according to"
    passingTest should "find definitions from t31" taggedAs(Somebody) in {
      val desired = Map(
        "dr" -> Seq("Segment size")
      )
      val mentions = extractMentions(t31)
      testDefinitionEvent(mentions, desired)
    }

  val t32 = "in which L (m) is the root length, z (m) is the total rooted soil depth, Ap (m2) is the surface area " +
    "and Ar (m2) is the root surface area."
    passingTest should "find definitions from t32" taggedAs(Somebody) in {
      val desired = Map(
        "L" -> Seq("root length"),
        "z" -> Seq("total rooted soil depth"),
        "Ap" -> Seq("surface area"),
        "Ar" -> Seq("root surface area")
      )
      val mentions = extractMentions(t32)
      testDefinitionEvent(mentions, desired)
    }

  val t33 = "where: T = daily mean air temperature [°C] Tmax = daily maximum air temperature [°C] Tmin = daily " +
    "minimum air temperature [°C]"
    passingTest should "find definitions from t33" taggedAs(Somebody) in {
      val desired = Map(
        "T" -> Seq("daily mean air temperature"), // [C] is caught as part of the concept
        "Tmax" -> Seq("daily maximum air temperature"),
        "Tmin" -> Seq("daily minimum air temperature")
      )
      val mentions = extractMentions(t33)
      testDefinitionEvent(mentions, desired)
    }

  val t34 = "with dr,min = 1028 m, dr,max = 5.1024 m, S = 0.5, r0 (m) is the root radius and rm (m) is the radius of " +
    "the root extraction zone, equal to the half-distance between roots (rm), which relates to the root density " +
    "R (m m23) as..."
  passingTest should "find definitions from t34" taggedAs(Somebody) in {

    val desired = Map(
      "r0" -> Seq("root radius"),
      "rm" -> Seq("radius of the root extraction zone"),
      "R" -> Seq("root density"),
    )
    val mentions = extractMentions(t34)
    testDefinitionEvent(mentions, desired)
  }

  val t35 = "where p is the iteration level."
  passingTest should "find definitions from t35" taggedAs(Somebody) in {
    val desired = Map(
      "r0" -> Seq("root radius"),
      "rm" -> Seq("radius of the root extraction zone"),
      "R" -> Seq("root density"),
    )
    val mentions = extractMentions(t35)
    testDefinitionEvent(mentions, desired)
  }

  val t36 = "Assuming no sink or source (S = 0) and no gravitational or osmotic component (H = h), Eq. [4] reduces to..."
  passingTest should "find definitions from t36" taggedAs(Somebody) in {
    val desired = Map(
      "r0" -> Seq("root radius"),
      "rm" -> Seq("radius of the root extraction zone"),
      "R" -> Seq("root density"),
    )
    val mentions = extractMentions(t36)
    testDefinitionEvent(mentions, desired)
  }

}
