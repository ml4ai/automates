# AutoMATES TextReading
#### Contact Information
PI: Clayton T. Morrison (claytonm@email.arizona.edu)<br>
TR Pipeline: Rebecca Sharp (bsharp@email.arizona.edu)<br>
ModX: Paul D. Hein (pauldhein@email.arizona.edu)<br>
> NOTE: The text reading pipeline is currently tuned to emphasize 
> *recall* as our primary goal is gathering resources for linking. 
> You will likely see a number of false positives. This behavior 
> can be adjusted.

#### Installation and Running
- AutoMATES repository setup	- Clone the AutoMATES repository: `git clone --branch v0.2.0 git@github.com:ml4ai/automates.git`	- Install [docker](https://docs.docker.com/install/) and [docker-compose](https://docs.docker.com/compose/install/)

- Launch scienceparse
	> NOTE: This step can be done in batch using a different script, since this takes some time.

	- `cd` to the directory `/path/to/automates/text_reading/docker`
	- Run the command `docker-compose up scienceparse`
	- Leave this shell open for the duration of testing		(takes some time to launch)

- Setup the config
	- in `/path/to/automates/text_reading/src/main/resources/application.conf`
		set:
    	- apps.inputType = "pdf"

	    > NOTE: this assumes you are parsing a pdf. 
	    > Sicne pdf parsing with scienceparse takes some time, it is 
	    > possible to instead process pdfs in batch and save as 
	    > scienceparse-json files and then batch process the reading 
	    > of the json files.
	    > We have a script for this.

    	- apps.inputDirectory = path/to/your/pdfs
    	- apps.outputDirectory = path/to/where/dump/stuff
    	- exportAs = ["json"] (assuming you want json representation of the mentions)
	
- on the command line from `/path/to/automates/text_reading`:
  run:
    `sbt runMain org.clulab.aske.automates.apps.ExtractAndExport`

