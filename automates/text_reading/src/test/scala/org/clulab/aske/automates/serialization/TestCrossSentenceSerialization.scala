package org.clulab.aske.automates.serialization


import org.clulab.aske.automates.TestUtils.{ExtractionTest, Somebody}
import org.clulab.aske.automates.mentions.CrossSentenceEventMention
import org.clulab.aske.automates.serializer.AutomatesJSONSerializer
import org.clulab.odin.{Mention, TextBoundMention}


   // first, let's make crossSentenceMentions to export to JSON file

  class TestCrossSentenceSerialization extends ExtractionTest {

    val textToTest = "Rn depends on RS, but also on T and RH. The only additional parameter appearing in the suggested formula is the extraterrestrial radiation, RA."
    failingTest should s"serialize and deserialize the mention successfully: ${textToTest}" taggedAs (Somebody) in {
      val mentions = extractMentions(textToTest)
      val crossSentenceMentions = mentions.filter(m => m.isInstanceOf[CrossSentenceEventMention])
      val value = mentions.filter(m => m.isInstanceOf[TextBoundMention])
      val uJson = AutomatesJSONSerializer.serializeMentions(crossSentenceMentions)
      // next, let's try to export the mentions to JSON file (how can I use export method??)
      val deserializedMentions = AutomatesJSONSerializer.toMentions(uJson)
      assert(crossSentenceMentions == deserializedMentions)
    }
  }