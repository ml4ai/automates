
name := "automates_text_reading"
organization := "org.clulab"

scalaVersion := "2.12.4"
val json4sVersion = "3.5.2"

//EclipseKeys.withSource := true

libraryDependencies ++= {
  val procVer = "7.4.2"

  Seq(
    "org.clulab"    %% "processors-main"          % procVer,
    "org.clulab"    %% "processors-corenlp"       % procVer,
    "org.clulab"    %% "processors-odin"          % procVer,
    "org.clulab"    %% "processors-modelsmain"    % procVer,
    "org.clulab"    %% "processors-modelscorenlp" % procVer,
    "ai.lum"        %% "common"                   % "0.0.8",
    "com.lihaoyi"   %% "ujson"                    % "0.7.1",
    "com.lihaoyi"   %% "requests"                 % "0.1.4",
    // "com.lihaoyi" %% "upickle" % "0.7.1",
    "org.scalatest" %% "scalatest"                % "3.0.4" % "test",
    "com.typesafe"  %  "config"                   % "1.3.1",
    "org.json4s"              %%  "json4s-core"               % json4sVersion,

    "com.typesafe.scala-logging" %% "scala-logging" % "3.7.2"
  )
}


lazy val core = project in file(".")

lazy val webapp = project
  .enablePlugins(PlayScala)
  .aggregate(core)
  .dependsOn(core)
