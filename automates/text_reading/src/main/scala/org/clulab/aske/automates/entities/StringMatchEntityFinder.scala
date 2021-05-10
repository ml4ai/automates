package org.clulab.aske.automates.entities


import java.io.File

import ai.lum.common.ConfigUtils._
import ai.lum.common.FileUtils._
import ai.lum.regextools.RegexBuilder
import com.typesafe.config.Config
import org.clulab.aske.automates.grfn.{GrFNDocument, GrFNParser}
import org.clulab.odin.{ExtractorEngine, Mention}
import org.clulab.processors.Document
import org.clulab.utils.AlignmentJsonUtils

class StringMatchEntityFinder(strings: Set[String], label: String, taxonomyPath: String) extends EntityFinder {
  println(s"from StringMatchEntityFinder: $strings")
  val regexBuilder = new RegexBuilder()
  regexBuilder.add(strings.toSeq:_*)
  val regex = regexBuilder.mkPattern
  //           |     (?<! [word = equation]) /\\Q${stringToMatch}\\E/
  def extract(doc: Document): Seq[Mention] = {
    val ruleTemplate =
      s"""
         |taxonomy: "${taxonomyPath}"
         |
         |rules:
         | - name: stringmatch
         |   label: ${label}
         |   priority: 1
         |   type: token
         |   pattern: |
         |       (?<! [word = equation]) /^(${regex})$$/
         |
        """.stripMargin
    val engine = ExtractorEngine(ruleTemplate)
    val mentions = engine.extractFrom(doc)
    mentions
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
  def apply(ms: Seq[Mention], validLabels: Seq[String], label: String, taxonomy: String = "org/clulab/aske_automates/grammars/taxonomy.yml"): StringMatchEntityFinder = {
    val strings = for {
      m <- ms
      m2 <- Seq(m) ++ m.arguments.valuesIterator.flatten
      if validLabels.contains(m2.label)
    } yield m2.text
    new StringMatchEntityFinder(strings.toSet, label, taxonomy)
  }

  def fromStrings(ss: Seq[String], label: String, taxonomy: String = "org/clulab/aske_automates/grammars/taxonomy.yml"): StringMatchEntityFinder = new StringMatchEntityFinder(ss.toSet, label, taxonomy)
}

object GrFNEntityFinder {


  def fromConfig(config: Config) = {
    val grfnPath: String = config[String]("grfnFile") // fixme (Becky): extend to a dir later
    val grfnFile = new File(grfnPath)
    val grfn = ujson.read(grfnFile.readString())

    // The identifier names only (excluding the scope info)
    val identifierShortNames = if (grfn.obj.get("variables").isDefined) {
      GrFNParser.getVariableShortNames(grfn)
    } else {
      AlignmentJsonUtils.getIdentifierShortNames(grfn)
    }

    // Make a StringMatchEF based on the identifier names
    // todo: send in the taxonomy path
    StringMatchEntityFinder.fromStrings(identifierShortNames, "Identifier") // todo: GrFNVariable?
  }
}

