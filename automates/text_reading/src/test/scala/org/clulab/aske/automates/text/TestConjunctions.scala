package org.clulab.aske.automates.text

import org.clulab.aske.automates.TestUtils._

class TestConjunctions extends ExtractionTest {

  // conj tests
  val t1 = "The model consists of individuals who are either Susceptible (S), Infected (I), or Recovered (R)."
  passingTest should s"find definitions from t1: ${t1}" taggedAs (Somebody) in {

    val desired = Seq(
      "S" -> Seq("individuals who are either Susceptible"),
      "I" -> Seq("individuals who are Infected"),
      "R" -> Seq("individuals who are Recovered")
    )
    val mentions = extractMentions(t1)
    testDefinitionEvent(mentions, desired)
  }

  val t2 = "where RHmax and RHmin are maximum and minimum relative humidity, respectively"
  failingTest should s"find definitions from t2: ${t2}" taggedAs (Somebody) in {

    val desired = Seq(
      "RHmax" -> Seq("maximum relative humidity"),
      "RHmin" -> Seq("minimum relative humidity")
    )
    val mentions = extractMentions(t2)
    testDefinitionEvent(mentions, desired)
  }

  val t3 = "while b, c and d are the removal rate of individuals in class I, IP and E respectively"
  passingTest should s"find definitions from t3: ${t3}" taggedAs (Somebody) in {

    val desired = Seq(
      "b" -> Seq("removal rate of individuals in class I"),
      "c" -> Seq("removal rate of individuals in class IP"),
      "d" -> Seq("removal rate of individuals in class E"),
      "I" -> Seq("class") // this one is not ideal, but is not the focus of the test, so it's okay to keep it this way (ideally, would be class I, class IP, and class E or no class defs, but this is not crucial)
    )
    val mentions = extractMentions(t3)
    testDefinitionEvent(mentions, desired)
  }


  val t4 = "Where S is the stock of susceptible population, I is the stock of infected, and R is the stock of " +
    "recovered population."
  failingTest should s"find definitions from t4: ${t4}" taggedAs (Somebody) in {

    val desired = Seq(
      "S" -> Seq("stock of susceptible population"),
      "I" -> Seq("stock of infected population"),
      "R" -> Seq("stock of recovered population")
    )
    val mentions = extractMentions(t4)
    testDefinitionEvent(mentions, desired)
  }

  val t5 = "where S(0) and R(0) are the initial numbers of, respectively, susceptible and removed subjects"
  failingTest should s"find definitions from t5: ${t5}" taggedAs(Somebody) in {
    val desired =  Seq(
      "S(0)" -> Seq("initial number of susceptible subjects"),
      "R(0)" -> Seq("initial number of removed subjects")      //fixme: the definition is not expanded over 'respectively'
    )
    val mentions = extractMentions(t5)
    testDefinitionEvent(mentions, desired)
  }

  val t6 = "where H(x) and H(y) are entropies of x and y,respectively."
  passingTest should s"find definitions from t5: ${t6}" taggedAs (Somebody) in {

    val desired = Seq(
      "H(x)" -> Seq("entropies of x"), //fixme: ideally, should be entropy
      "H(y)" -> Seq("entropies of y")
    )
    val mentions = extractMentions(t6)
    testDefinitionEvent(mentions, desired)
  }

    val t7 = "where Rns and Rnc are net radiation obtained by soil surface and intercepted by crop canopy (W m−2), respectively; αs and αc are soil " +
      "evaporation coefficient and crop transpiration coefficient, respectively."
  failingTest should s"find definitions from t7: ${t7}" taggedAs(Somebody) in {
    val desired =  Seq(
      "Rns" -> Seq("net radiation obtained by soil surface"), // fixme: Only "Rns" is captured as variable here. The definition is also incomplete. ("net radiation")
      "Rnc" -> Seq("net radiation intercepted by crop canopy"),
      "αs" -> Seq("soil evaporation coefficient"), // fixme: Only "αs" is captured as variable here.
      "αc" -> Seq("crop transpiration coefficient") // fixme: The definition for "αc" was not captured.
    )
    val mentions = extractMentions(t7)
    testDefinitionEvent(mentions, desired)
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