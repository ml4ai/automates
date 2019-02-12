package org.clulab.aske.automates.entities

import org.clulab.odin.{ExtractorEngine, Mention}
import org.clulab.processors.Document

class StringMatchEntityFinder(strings: Set[String], label: String) extends EntityFinder {

  def extract(doc: Document): Seq[Mention] = {
    val mentions = for {
      stringToMatch <- strings
      ruleTemplate =
        s"""
           | - name: stringmatch
           |   label: ${label}
           |   priority: 1
           |   type: token
           |   pattern: |
           |       /${stringToMatch}/
           |
        """.stripMargin
      engine = ExtractorEngine(ruleTemplate)
    } yield engine.extractFrom(doc)
    mentions.flatten.toSeq
  }

}

object StringMatchEntityFinder {

  /**
    * Construct a StringMatchEntityFinder from a set of mentions, i.e., match additional mentions of previously found
    * mentions.
    * @param ms previously found mentions
    * @param validLabels
    * @return
    */
  def apply(ms: Seq[Mention], validLabels: Seq[String], label: String): StringMatchEntityFinder = {
    val strings = for {
      m <- ms
      m2 <- Seq(m) ++ m.arguments.valuesIterator.flatten
      if validLabels.contains(m2.label)
    } yield m2.text
    val noSpecSymbolsStrings = replaceSpecialSymbols(strings)
    println(noSpecSymbolsStrings)
    new StringMatchEntityFinder(noSpecSymbolsStrings.toSet, label) //todo: write method that will replace regex special symbols, e.g., "(" -> "\(" (scala method regex escape)
  }

  def replaceSpecialSymbols(strings: Seq[String]): Seq[String] = {
   val regexString = for {
     str <- strings
   } yield str.replaceAll("[)(]","") //"[\\[\\^\\.\\|\\?\\*\\+\\(\\)\\]]"
    regexString
  }

}
