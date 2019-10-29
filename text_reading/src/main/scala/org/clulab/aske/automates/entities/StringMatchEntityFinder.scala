package org.clulab.aske.automates.entities


import java.io.File

import ai.lum.common.ConfigUtils._
import ai.lum.common.FileUtils._
import ai.lum.regextools.RegexBuilder
import com.typesafe.config.Config
import org.clulab.aske.automates.grfn.{GrFNDocument, GrFNParser}
import org.clulab.odin.{ExtractorEngine, Mention}
import org.clulab.processors.Document

class StringMatchEntityFinder(strings: Set[String], label: String) extends EntityFinder {
  val regexBuilder = new RegexBuilder()
  regexBuilder.add(strings.toSeq.map(s => s"""\\b${s}\\b"""):_*)
  val regex = regexBuilder.mkPattern
  // alexeeva: added neg lookbehind to avoid equation # to be found as a variable
  //           |     (?<! [word = equation]) /\\Q${stringToMatch}\\E/
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
         |       (?<! [word = equation]) /${regex}/
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
    new StringMatchEntityFinder(strings.toSet, label)
  }

  def fromStrings(ss: Seq[String], label: String): StringMatchEntityFinder = new StringMatchEntityFinder(ss.toSet, label)
}

object GrFNEntityFinder {
  def getVariableShortNames(variableNames: Seq[String]): Seq[String] = for (
    name <- variableNames
  ) yield name.split("::").reverse.slice(1, 2).mkString("")

  def fromConfig(config: Config) = {
    val grfnPath: String = config[String]("grfnFile") // fixme (Becky): extend to a dir later
    val grfnFile = new File(grfnPath)
    val grfn = ujson.read(grfnFile.readString())
    // Full variable identifiers
    val variableNames = grfn("variables").arr.map(_.obj("name").str)
    // The variable names only (excluding the scope info)
    val variableShortNames = getVariableShortNames(variableNames)

    // Make a StringMatchEF based on the variable names
    StringMatchEntityFinder.fromStrings(variableShortNames, "Variable") // todo: GrFNVariable?
  }
}

