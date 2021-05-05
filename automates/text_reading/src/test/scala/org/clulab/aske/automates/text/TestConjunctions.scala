package org.clulab.aske.automates.text

import org.clulab.aske.automates.TestUtils._

class TestConjunctions extends ExtractionTest {

  // conj tests
  val t1 = "The model consists of individuals who are either Susceptible (S), Infected (I), or Recovered (R)."
  passingTest should s"find descriptions from t1: ${t1}" taggedAs (Somebody) in {

    val desired = Seq(

//      "S" -> Seq("individuals who are Susceptible"), //TODO: getDiscontCharOffset doesn't seem to work properly. needs to be fixed to skip unwanted parts.

      "S" -> Seq("individuals who are either Susceptible"),
      "I" -> Seq("individuals who are Infected"),
      "R" -> Seq("individuals who are Recovered")
    )
    val mentions = extractMentions(t1)
    testDescriptionEvent(mentions, desired)
  }

  val t2 = "where RHmax and RHmin are maximum and minimum relative humidity, respectively"
  failingTest should s"find descriptions from t2: ${t2}" taggedAs (Somebody) in {

    val desired = Seq(
      "RHmax" -> Seq("maximum relative humidity"), // todo: how to extract two distinct descriptions for the two identifiers?
      "RHmin" -> Seq("minimum relative humidity")
    )
    val mentions = extractMentions(t2)
    testDescriptionEvent(mentions, desired)
  }

  val t3 = "while b, c and d are the removal rate of individuals in class I, IP and E respectively"
  passingTest should s"find descriptions from t3: ${t3}" taggedAs (Somebody) in {

    val desired = Seq(
      "b" -> Seq("removal rate of individuals in class I"),
      "c" -> Seq("removal rate of individuals in class IP"),
      "d" -> Seq("removal rate of individuals in class E")
    )
    val mentions = extractMentions(t3)
    testDescriptionEvent(mentions, desired)
  }


  val t4 = "Where S is the stock of susceptible population, I is the stock of infected, and R is the stock of " +
    "recovered population."
  failingTest should s"find descriptions from t4: ${t4}" taggedAs (Somebody) in {

    val desired = Seq(
      "S" -> Seq("stock of susceptible population"),
      "I" -> Seq("stock of infected population"), // fix me: "population" needs to be captured as a part of the description.
      "R" -> Seq("stock of recovered population")
    )
    val mentions = extractMentions(t4)
    testDescriptionEvent(mentions, desired)
  }

  val t5 = "where S(0) and R(0) are the initial numbers of, respectively, susceptible and removed subjects"
  failingTest should s"find descriptions from t5: ${t5}" taggedAs(Somebody) in {
    val desired =  Seq(
      "S(0)" -> Seq("initial number of susceptible subjects"),
      "R(0)" -> Seq("initial number of removed subjects")      //fixme: the description is not expanded over 'respectively'
    )
    val mentions = extractMentions(t5)
    testDescriptionEvent(mentions, desired)
  }

  val t6 = "where H(x) and H(y) are entropies of x and y,respectively."
  passingTest should s"find descriptions from t5: ${t6}" taggedAs (Somebody) in {

    val desired = Seq(
      "H(x)" -> Seq("entropies of x"), //fixme: ideally, should be entropy
      "H(y)" -> Seq("entropies of y")
    )
    val mentions = extractMentions(t6)
    testDescriptionEvent(mentions, desired)
  }

    val t7 = "where Rns and Rnc are net radiation obtained by soil surface and intercepted by crop canopy (W m−2), respectively; αs and αc are soil " +
      "evaporation coefficient and crop transpiration coefficient, respectively."
  failingTest should s"find descriptions from t7: ${t7}" taggedAs(Somebody) in {
    val desired =  Seq(
      "Rns" -> Seq("net radiation obtained by soil surface"), // fixme: Only "Rns" is captured as identifier here. The description is also incomplete. ("net radiation")
      "Rnc" -> Seq("net radiation intercepted by crop canopy"),
      "αs" -> Seq("soil evaporation coefficient"), // fixme: Only "αs" is captured as identifier here.
      "αc" -> Seq("crop transpiration coefficient") // fixme: The description for "αc" was not captured.
    )
    val mentions = extractMentions(t7)
    testDescriptionEvent(mentions, desired)

  }

  // tests moved from description test

    val t8 = "K and Ksat are hydraulic conductivity and saturated hydraulic conductivity, respectively."
  passingTest should s"find descriptions from t8: ${t8}" taggedAs(Somebody) in {
      val desired = Seq(
        "K" -> Seq("hydraulic conductivity"),
        "Ksat" -> Seq("saturated hydraulic conductivity")
      )
      val mentions = extractMentions(t8)
      testDescriptionEvent(mentions, desired)

  }

  val t9 = "u, ur, and us are water content, residual water content and saturated water content (m3 m-3), " +
    "respectively; h is pressure head (m); K and Ksat are hydraulic conductivity and saturated hydraulic conductivity, " +
    "respectively (m d21); and a (m21), n, and l are empirical parameters."
  failingTest should s"find descriptions from t9: ${t9}" taggedAs(Somebody) in {
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
    val mentions = extractMentions(t9)
    testDescriptionEvent(mentions, desired)

  }

}

// Panels ( C ) and ( D ) shows virus uptake for the same cells as in panels A and B respectively .
// where k ~ 1z1 = T c is the total branching factor and k A , k B are the isolated branching factors of layer A and B respectively .
// Panels A , B , and C illustrate the three separate multi-site , farrow-to-finish production flows within the pork production system which are referred to as flows A , B , and C respectively .
// Based on the best fitted distributions , the estimated median incubation periods were 4.4 ( 95 % CI 3.8 – 5.1 ) days , 4.7 ( 95 % CI 4.5 – 5.1 ) days and 5.7 ( 95 % CI 4.6 – 7.0 ) days for children in kindergartens , primary schools and secondary schools respectively .
// Protomer A and B are denoted as P1 and P2 respectively .
//Y0 and B are the minimum and maximum fraction of triplex formation respectively .
//HSA and E-AFP are the negative control and positive control respectively .
// For clinical URTI , n = 55 and n = 51 in the gargling and control groups respectively . - good example for param setting where same var has diff values
// neg example	Closed and open circles respectively indicate methylated and unmethylated CpG sites .
//Here r and r P are related to the infection rate of disease A and B respectively , while a , a P and b are the removal rate of individuals in class I , I P and E respectively .
// The mean FICO 2 values at rest were 8.2 mmHg , 10.7 mmHg and 7.8 mmHg for the participants without mask , with mask , and with mask and MF respectively .
// where g, r (0.04 in this study) and s (0.36 in this study) denote measured, residual and saturated water content in 0–10 cm soil depth(cm3 cm−3), respectively.


