package org.clulab.aske.automates.serialization

import org.clulab.aske.automates.TestUtils.{ExtractionTest, Somebody}
import org.clulab.aske.automates.mentions.CrossSentenceEventMention
import org.clulab.aske.automates.serializer.AutomatesJSONSerializer
import org.clulab.odin.TextBoundMention


   // first, let's make crossSentenceMentions to export to JSON file

class TestConjDescrSerialization extends ExtractionTest {

  val t1 = "The model consists of individuals who are either Susceptible (S), Infected (I), or Recovered (R)."
  passingTest should s"serialize and deserialize the mention successfully from t1: ${t1}" taggedAs (Somebody) in {
    val mentions = extractMentions(t1)
    val conjDefMention = mentions.filter(m => m.labels.contains("ConjDescription"))
    val uJson = AutomatesJSONSerializer.serializeMentions(conjDefMention)
    val deserializedMentions = AutomatesJSONSerializer.toMentions(uJson)
    assert(conjDefMention == deserializedMentions)
  }

  val t2 = "while b, c and d are the removal rate of individuals in class I, IP and E respectively"
  passingTest should s"serialize and deserialize the mention successfully from t2: ${t2}" taggedAs (Somebody) in {
    val mentions = extractMentions(t2)
    val conjDefMention = mentions.filter(m => m.labels.contains("ConjDescription"))
    val uJson = AutomatesJSONSerializer.serializeMentions(conjDefMention)
    println("HERE!! " + uJson)
    val deserializedMentions = AutomatesJSONSerializer.toMentions(uJson)
    assert(conjDefMention == deserializedMentions)
  }

  val t3 = "Where S is the stock of susceptible population, I is the stock of infected, and R is the stock of recovered population."
  passingTest should s"serialize and deserialize the mention successfully from t3: ${t3}" taggedAs (Somebody) in {
    val mentions = extractMentions(t3)
    val conjDefMention = mentions.filter(m => m.labels.contains("ConjDescription"))
    val uJson = AutomatesJSONSerializer.serializeMentions(conjDefMention)
    val deserializedMentions = AutomatesJSONSerializer.toMentions(uJson)
    assert(conjDefMention == deserializedMentions)
  }

  val t4 = "where H(x) and H(y) are entropies of x and y,respectively."
  passingTest should s"serialize and deserialize the mention successfully from t4: ${t4}" taggedAs (Somebody) in {
    val mentions = extractMentions(t4)
    val conjDefMention = mentions.filter(m => m.labels.contains("ConjDescription"))
    val uJson = AutomatesJSONSerializer.serializeMentions(conjDefMention)
    val deserializedMentions = AutomatesJSONSerializer.toMentions(uJson)
    assert(conjDefMention == deserializedMentions)
  }
}