package org.clulab.aske.automates.data

import org.clulab.aske.automates.OdinEngine

trait Router {
  def route(text: String): OdinEngine
}

// todo: Masha/Andrew make some Routers
class TextRouter(val engines: Seq[(String, OdinEngine)]) extends Router {
  def route(text: String): OdinEngine = engines.head._2
}