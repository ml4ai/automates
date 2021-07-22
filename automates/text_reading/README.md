# ASKE AutoMATES Text Reading project

Using Processors, Odin and a webapp, this project is read scientific papers and
extract information about models, variables, and related concepts.

## Running the webapp

Once installed, from the project root run:
`$ sbt webapp/run`
and point a browser to `localhost:9000`

## Running the shell

As an alternative to the webapp, you can see the results of extraction using the shell. From the project root run:

```bash
> sh shell
```
or 
```
> sbt 'runMain org.clulab.aske.automates.apps.AutomatesShell'
```
and enter the text to process at the prompt to see the extracted event mentions (including semantic and syntactic heads for each) along with the tokens, part of speech tags, and syntactic dependencies for each sentence. 

## Scala project installation notes

### Mac (High Sierra 10.13.5)

- Requires Java 1.8 (Java 8)
    - http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html

- IntelliJ
    - Open project, select project root (containing build.sbt)
    - Dialog box:
        - Select options: (a) download sbt sources and (b) using sbt console
        - Ensure you're using Java 1.8 JDK and JRE

- First run will take a while as it downloads all related packages
    - The following maintain the project-specific sbt and scala
        - `~/.ivy2`  # storage of package cache ; ends up about 1.6G
        - `~/.sbt`   # storage of sbt and scala versions

## Prerequistes for using Python interface

The Python interface depends on pygraphviz to render plots of the dependency parse, 
and this in turn depends on graphviz.

### Mac (High Sierra 10.13.5)

If you have installed graphviz using Homebrew 
and you are then installing pygraphviz using pip, you need to do the following:
```bash
pip install --install-option="--include-path=/usr/local/include/" \
            --install-option="--library-path=/usr/local/lib" pygraphviz
```
