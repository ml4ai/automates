package org.clulab.aske.automates

import org.clulab.odin.Mention

import scala.collection.mutable.ArrayBuffer

class TestResult(val mention: Option[Mention], val complaints: Seq[String])

class Tester(ieSystem: OdinEngine, text: String) {

  //val mentions = extractMentions(clean(text))
  val mentions: Seq[Mention] = TestUtils.extractMentions(ieSystem, text)

  val testResults = new ArrayBuffer[TestResult]

  protected def toString(mentions: Seq[Mention]): String = {
    mentions.zipWithIndex.map{case (mention, index) => {
      s"$index: ${mention.text} ${mention.attachments.mkString(", ")}"
    }}.mkString("\n")
  }

  protected def annotateTest(result: Seq[String]): Seq[String] =
    if (result == TestUtils.successful)
      result
    else
      result ++ Seq("Mentions:\n" + toString(mentions))

//  def test(nodeSpec: NodeSpec): Seq[String] = {
//    val testResult = nodeSpec.test(mentions, useTimeNorm, useGeoNorm, testResults)
//
//    annotateTest(testResult.complaints)
//  }
//
//  def test(edgeSpec: EdgeSpec): Seq[String] = {
//    val testResult = edgeSpec.test(mentions, useTimeNorm, useGeoNorm, testResults)
//
//    annotateTest(testResult.complaints)
//  }

}