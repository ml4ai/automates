package org.clulab.aske.automates.serialization


import org.clulab.aske.automates.TestUtils.{ExtractionTest, Somebody}
import org.clulab.aske.automates.mentions.CrossSentenceEventMention
import org.clulab.aske.automates.serializer.AutomatesJSONSerializer

  class TestCrossSentenceSerialization extends ExtractionTest {

    val textToTest = "Rn depends on RS, but also on T and RH. The only additional parameter appearing in the suggested formula is the extraterrestrial radiation, RA."
    passingTest should s"serialize and deserialize the mention successfully: ${textToTest}" taggedAs (Somebody) in {
      val mentions = extractMentions(textToTest)
      val crossSentenceMentions = mentions.filter(m => m.isInstanceOf[CrossSentenceEventMention]).distinct
      // serialize mentions (into a json object)
      val uJson = AutomatesJSONSerializer.serializeMentions(crossSentenceMentions)
      // and read them back in from the json
      val deserializedMentions = AutomatesJSONSerializer.toMentions(uJson)
      // check if all mentions have been deserialized
      deserializedMentions should have size (crossSentenceMentions.size)
      // check the documents idea has been preserved
      deserializedMentions.head.document.equivalenceHash should equal (crossSentenceMentions.head.document.equivalenceHash)
      // check text of mention (probably redundant, but just in case)
      deserializedMentions.head.text should equal(crossSentenceMentions.head.text)
      // make sure sentences were preserved (only CrossSentEventMentions have attribute "sentences", so cast the mention as a CrossSentEventMention
      deserializedMentions.head.asInstanceOf[CrossSentenceEventMention].sentences should equal(crossSentenceMentions.head.asInstanceOf[CrossSentenceEventMention].sentences)
      // check if mention ids match---use hashes created with our CrossSentenceEventMentionOps---not generic CrossSentenceMentionOps found in clulab processors;
      // for other types of mentions, it should be fine to use Ops from processors
      // this might be a little overcomplicated, but it seems to work
      val hashesDeser = deserializedMentions.map(m => AutomatesJSONSerializer.CrossSentenceEventMentionOps(m.asInstanceOf[CrossSentenceEventMention]).equivalenceHash).toSet
      val hashesOrig = crossSentenceMentions.map(m =>  AutomatesJSONSerializer.CrossSentenceEventMentionOps(m.asInstanceOf[CrossSentenceEventMention]).equivalenceHash).toSet
      hashesDeser should equal(hashesOrig)
    }
  }