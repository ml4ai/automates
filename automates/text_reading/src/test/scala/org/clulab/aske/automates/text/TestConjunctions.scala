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


  val t4 = "while b, c and d are the removal rate of individuals in class I, IP and E respectively"
  failingTest should s"find definitions from t4: ${t4}" taggedAs (Somebody) in {

    val desired = Seq(
      "b" -> Seq("removal rate of individuals in class B"),
      "c" -> Seq("removal rate of individuals in class C"),
      "d" -> Seq("removal rate of individuals in class D")
    )
    val mentions = extractMentions(t4)
    testDefinitionEvent(mentions, desired)
  }
}