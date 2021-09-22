
name := "automates_text_reading"
organization := "org.clulab"

scalaVersion := "2.12.4"
val json4sVersion = "3.5.2"

//EclipseKeys.withSource := true

libraryDependencies ++= {
  val procVer = "7.5.1"

  Seq(
    "org.clulab"    %% "processors-main"          % procVer,
    "org.clulab"    %% "processors-corenlp"       % procVer,
    "org.clulab"    %% "processors-odin"          % procVer,
    "org.clulab"    %% "processors-modelsmain"    % procVer,
    "org.clulab"    %% "processors-modelscorenlp" % procVer,
    "ai.lum"        %% "common"                   % "0.0.10",
    "ai.lum"        %% "regextools"               % "0.1.0-SNAPSHOT",
    "com.lihaoyi"   %% "ujson"                    % "0.7.0",
    "com.lihaoyi"   %% "requests"                 % "0.5.1",
    "com.lihaoyi"   %% "upickle"                  % "0.7.0",
    "com.lihaoyi"   %% "ujson-json4s"             % "0.7.0",
    "org.scalatest" %% "scalatest"                % "3.0.4" % "test",
    "com.typesafe"  %  "config"                   % "1.3.1",
    "org.json4s"    %%  "json4s-core"             % json4sVersion,
    "com.typesafe.scala-logging" %% "scala-logging" % "3.7.2",
    "org.apache.commons" % "commons-text" % "1.6",
    "com.typesafe.play" %% "play-json" % "2.7.0",
    "org.json4s" %% "json4s-jackson" % "0.1.0",
    "org.scala-lang.modules" %% "scala-xml" % "1.0.2",
    "org.apache.commons" % "commons-text" % "1.4"
//    "com.github.blemale" %% "scaffeine" % "4.0.2" % "compile" // can be used in future for in-memory caching of wikidata results
  )
}

libraryDependencies += guice

lazy val core = project in file(".")

lazy val webapp = project
  .enablePlugins(PlayScala)
  .aggregate(core)
  .dependsOn(core)
