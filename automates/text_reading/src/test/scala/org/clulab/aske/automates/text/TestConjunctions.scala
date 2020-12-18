package org.clulab.aske.automates.text

import org.clulab.aske.automates.TestUtils._

class TestConjunctions extends ExtractionTest {


  // conj tests
  val t1 = "individuals who are either Susceptible (S), Infected (I), or Recovered (R)"
  failingTest should s"find definitions from t1: ${t1}" taggedAs (Somebody) in {

    val desired = Seq(
      "S" -> Seq("individuals who are Susceptible"),
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
  failingTest should s"find definitions from t3: ${t3}" taggedAs (Somebody) in {

    val desired = Seq(
      "b" -> Seq("removal rate of individuals in class B"),
      "c" -> Seq("removal rate of individuals in class C"),
      "d" -> Seq("removal rate of individuals in class D")
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

  val t5 = "S(0) and R(0) are the initial numbers of, respectively, susceptible and removed subjects."
  failingTest should s"find definitions from t5: ${t5}" taggedAs (Somebody) in {

    val desired = Seq(
      "S(0)" -> Seq("initial numbers of susceptible subjects"),
      "R(0)" -> Seq("initial numbers of removed subjects")
    )
    val mentions = extractMentions(t5)
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