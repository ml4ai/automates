package org.clulab.aske.automates.entities

import org.clulab.aske.automates.TestUtils.jsonStringToDocument
import org.scalatest.{FlatSpec, Matchers}

class TestStringMatchEntityFinder extends FlatSpec with Matchers {

  val finder = StringMatchEntityFinder.fromStrings(Seq("MATCH", "OTHER"), "Matched", "testTaxonomy.yml")

  it should "not find mentions when no string match" in {

    // Text: "This should have no match."
    val doc = jsonStringToDocument("{\"sentences\":[{\"words\":[\"This\",\"should\",\"have\",\"no\",\"match\",\".\"],\"startOffsets\":[0,5,12,17,20,25],\"endOffsets\":[4,11,16,19,25,26],\"raw\":[\"This\",\"should\",\"have\",\"no\",\"match\",\".\"],\"graphs\":{}}]}")
    val ms = finder.extract(doc)
    ms.length should be (0)
  }

  ignore should "find one mention match when sting matches one place" in {
    // Text: "This should MATCH for sure!"
    val doc = jsonStringToDocument("{\"sentences\":[{\"words\":[\"This\",\"should\",\"MATCH\",\"for\",\"sure\",\"!\"],\"startOffsets\":[0,5,12,18,22,26],\"endOffsets\":[4,11,17,21,26,27],\"raw\":[\"This\",\"should\",\"MATCH\",\"for\",\"sure\",\"!\"],\"graphs\":{}}]}")
    val ms = finder.extract(doc)
    ms.length should be (1)
    val m = ms.head
    m.text should be ("MATCH")
    m.label should be ("Matched")
  }

  ignore should "match several instances of same string" in {
    // Text; "This should MATCH twice, because of the second MATCH."
    val doc = jsonStringToDocument("{\"sentences\":[{\"words\":[\"This\",\"should\",\"MATCH\",\"twice\",\",\",\"because\",\"of\",\"the\",\"second\",\"MATCH\",\".\"],\"startOffsets\":[0,5,12,18,23,25,33,36,40,47,52],\"endOffsets\":[4,11,17,23,24,32,35,39,46,52,53],\"raw\":[\"This\",\"should\",\"MATCH\",\"twice\",\",\",\"because\",\"of\",\"the\",\"second\",\"MATCH\",\".\"],\"graphs\":{}}]}")
    val ms = finder.extract(doc)
    ms.length should be (2)
    ms foreach { m =>
      m.text should be ("MATCH")
      m.label should be ("Matched")
    }

  }

  ignore should "match more than one string" in {
    // Text: "This should MATCH twice, since OTHER is also here."
    val doc = jsonStringToDocument("{\"sentences\":[{\"words\":[\"This\",\"should\",\"MATCH\",\"twice\",\",\",\"since\",\"OTHER\",\"is\",\"also\",\"here\",\".\"],\"startOffsets\":[0,5,12,18,23,25,31,37,40,45,49],\"endOffsets\":[4,11,17,23,24,30,36,39,44,49,50],\"raw\":[\"This\",\"should\",\"MATCH\",\"twice\",\",\",\"since\",\"OTHER\",\"is\",\"also\",\"here\",\".\"],\"graphs\":{}}]}")
    val ms = finder.extract(doc)
    ms.length should be (2)
    ms.exists(m => m.text == "MATCH" && m.label == "Matched") should be (true)
    ms.exists(m => m.text == "OTHER" && m.label == "Matched") should be (true)
  }
}
