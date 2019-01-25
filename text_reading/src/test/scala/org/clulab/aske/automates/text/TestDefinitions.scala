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

  passingTest should "find definitions 2" in {

    val text = "where KEP (typically ranging from 0.5 to 0.8) is defined as an energy extinction coefficient of " +
      "the canopy for total solar irradiance, used for partitioning E0 to EPo and ESo (Ritchie, 1998)."

    val desired = Map(
      "KEP" -> Seq("energy extinction coefficient") // the def will eventually be the whole sentence
    )
    val mentions = extractMentions(text)
    testDefinitionEvent(mentions, desired)

  }

  passingTest should "find definitions 3" in {

    val text = "where Kcbmin is the minimum basal crop coefficient representing a dry, bare, or nearly bare soil surface."

    val desired = Map(
      "Kcbmin" -> Seq("minimum basal crop coefficient")
    )
    val mentions = extractMentions(text)
    testDefinitionEvent(mentions, desired)

  }

  passingTest should "find definitions 4" in {

    val text = "where Kcbmin is the minimum basal crop coefficient representing a dry, bare, or nearly bare soil surface."

    val desired = Map(
      "Kcbmin" -> Seq("minimum basal crop coefficient")
    )
    val mentions = extractMentions(text)
    testDefinitionEvent(mentions, desired)

  }

  passingTest should "find definitions 5" in {

    val text = "Second, the maximum potential water uptake for the profile (Ux, mm d−1) is obtained by multiplying Ta,rl " +
      "times pr for each layer and summing over the soil profile:"

    val desired = Map(
      "Ux" -> Seq("maximum potential water uptake") //for the profile? - not part of the concept
    )
    val mentions = extractMentions(text)
    testDefinitionEvent(mentions, desired)

  }

  passingTest should "find definitions 6" in {

    val text = "where s1 and s2 are parameters of a logistic curve (9 and 0.005, respectively), and w represents the " +
      "soil limitation to water uptake of each layer."

    val desired = Map(
      "s1" -> Seq("parameters of a logistic curve"),
      "s2" -> Seq("parameters of a logistic curve"),
      "w" -> Seq("soil limitation") // need to expand this to "to water uptake of each layer"
    )
    val mentions = extractMentions(text)
    testDefinitionEvent(mentions, desired)

  }


  passingTest should "find definitions 7" in {

    val text = "A convenient soil hydraulic property that will be used in this study is the matric flux potential " +
      "Mh0 (m2 d-1)"

    val desired = Map(
      "Mh0" -> Seq("matric flux potential")

    )
    val mentions = extractMentions(text)
    testDefinitionEvent(mentions, desired)

  }

  passingTest should "find definitions 8" in {

    val text = "where t is time (d), C is the differential water capacity (du/dh, m21), q is the water flux density " +
      "(m d21), r is the distance from the axial center (m), S is a sink or source term (d21), and H is the hydraulic " +
      "head (m)."

    val desired = Map(
      "t" -> Seq("time"),
      "C" -> Seq("differential water capacity"),
      "q" -> Seq("water flux density"),
      "r" -> Seq("distance from the axial center"),
      "S" -> Seq("sink or source term"), //two separate concepts, not going to pass without expansion?
      "H" -> Seq("hydraulic head")

    )
    val mentions = extractMentions(text)
    testDefinitionEvent(mentions, desired)

  }

  passingTest should "find definitions 9" in {

    val text = "u, ur, and us are water content, residual water content and saturated water content (m3 m-3), " +
      "respectively; h is pressure head (m); K and Ksat are hydraulic conductivity and saturated hydraulic conductivity, " +
      "respectively (m d21); and a (m21), n, and l are empirical parameters."

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
    val mentions = extractMentions(text)
    testDefinitionEvent(mentions, desired)

  }

  passingTest should "find definitions 10" in {

    val text = "Segment size (dr) was chosen smaller near the root and larger at greater distance, according to"

    val desired = Map(
      "dr" -> Seq("Segment size")

    )
    val mentions = extractMentions(text)
    testDefinitionEvent(mentions, desired)

  }

  passingTest should "find definitions 11" in {

    val text = "in which L (m) is the root length, z (m) is the total rooted soil depth, Ap (m2) is the surface area " +
      "and Ar (m2) is the root surface area."

    val desired = Map(
      "L" -> Seq("root length"),
      "z" -> Seq("total rooted soil depth"),
      "Ap" -> Seq("surface area"),
      "Ar" -> Seq("root surface area")

    )
    val mentions = extractMentions(text)
    testDefinitionEvent(mentions, desired)

  }

  passingTest should "find definitions 12" in {

    val text = "where: T = daily mean air temperature [°C] Tmax = daily maximum air temperature [°C] Tmin = daily " +
      "minimum air temperature [°C]"

    val desired = Map(
      "T" -> Seq("daily mean air temperature"), // [C] is caught as part of the concept
      "Tmax" -> Seq("daily maximum air temperature"),
      "Tmin" -> Seq("daily minimum air temperature")

    )
    val mentions = extractMentions(text)
    testDefinitionEvent(mentions, desired)

  }
}
