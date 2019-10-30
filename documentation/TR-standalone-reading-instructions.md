# AutoMATES TextReading

#### Contact Information
PI: Clayton T. Morrison (claytonm@email.arizona.edu)<br>
TR Pipeline: Rebecca Sharp (bsharp@email.arizona.edu)<br>
ModX: Paul D. Hein (pauldhein@email.arizona.edu)<br>

#### Notes

The following instructions describe the installation of the core
TextReading pipeline, and running the `ExtractAndExport` process.
> NOTE: The text reading pipeline is currently tuned to emphasize 
> *recall* as our primary goal is gathering resources for linking. 
> You will likely see a number of false positives. This behavior 
> can be adjusted.

> NOTE: Text within \<...> describes user-chosen name or appropriate path.

#### Installation and Running
- AutoMATES repository setup	- Clone the AutoMATES repository: `git clone --branch v0.2.0 git@github.com:ml4ai/automates.git`	- Install [docker](https://docs.docker.com/install/) and [docker-compose](https://docs.docker.com/compose/install/)

- Launch scienceparse
	> NOTE: A different script is available to do batch processing of pdfs
	> by scienceparse, since running scienceparse can take some time. 
	> Here, the assumption is that you process a paper by science parse
	> followed by processing by AutoMATES TextReading.

	- `cd` to the directory `<automates_root>/text_reading/docker`
	- Run the command `docker-compose up scienceparse`
	- Leave this shell open for the duration of running `ExtractAndExport` 		(takes some time to launch)

- Create a config file
	- Place the file here:
	
	`<automates_root>/text_reading/src/main/resources/<name>.conf`
	
	- Add the following lines:

		> The following assumes that you are directly processing pdf 
		> documents using scienceparse.
		> Pdf processing with scienceparse takes some time.
		> It is possible to batch process pdfs using sciencparse
		> (a separate script is available for this),
		> producing sciencepars-json files that can then be 
		> processed by the TextReading pipeline. To parse the
		> resulting scienceparse-json files, set apps.inputType = "json".
	
		```
		include "application"
    	apps.inputType = "pdf"
    	apps.inputDirectory = <path_to_source_pdf_directory>
    	apps.outputDirectory = <path_to_output_directory>
    	apps.exportAs = ["json"]
    	```
	
- On the command line from `<automates_root>/text_reading` run:
    `sbt  -Dconfig.file=<automates_root>/text_reading/src/main/resources/<name>.conf "runMain org.clulab.aske.automates.apps.ExtractAndExport"`
  
  Successful parsing results in one or more json files containing
  the extracted mentions saved to the `apps.outputDirectory`.

