package org.clulab.aske.automates.entities

import com.typesafe.config.Config
import org.clulab.odin.Mention
import org.clulab.processors.Document


trait EntityFinder {

  def extract(doc: Document): Seq[Mention]

}

object EntityFinder {
  def loadEntityFinder(finderType: String, config: Config): EntityFinder = {
    finderType match {
      case "rulebased" => RuleBasedEntityFinder.fromConfig(config)
      case "grobidquantities" => GrobidEntityFinder.fromConfig(config)
      case "gazetteer" => GazetteerEntityFinder.fromConfig(config)
      case "grfn" => GrFNEntityFinder.fromConfig(config)
      case _ => throw new RuntimeException(s"Unexpected entity finder type")
    }
  }
}
