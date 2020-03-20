## Text Reading

The team has been working on the following tasks (all in progress):

1. Analyzing the relevant scientific publications with two goals in mind:
	- finding additional relations to include in the taxonomy, e.g., calculations ("E0 is calculated as the product of Kcd and ETpm.") and non-precise parameter settings ("Rns and Rnl are generally positive or zero in value."); this work will help increase extraction coverage and will be done in close collaboration with the Model Analysis team to make sure the relations included in the taxonomy are relevant to the project needs; 
	- finding additional test cases to include in the test set for the existing relations (including both positive and negative examples); this work will help increase precision and recall.
2. Working on the rules used for extraction:
analyzing the output of the system for false positives and adding constraints on rules and actions used for extraction to eliminate the false positives; this work will help increase precision; writing additional rules; this work will help increase recall;
3. Implementing the functionality to extract units; this work is needed to substitute the [grobid](https://github.com/kermitt2/grobid)-quantities unit extractor, which has shown to be inadequate for our needs---with grobid-quantities, units are only extracted when preceded by a value; the units we need to extract are frequently compound (multi-word) and are not consistently extracted by grobid-quantities (e.g., "kg ha-1 mm-1").
To this end we are including an entity finder based on a gazetteer in the current extraction system; 
Building a gazetteer (a lexicon) of units based on the Guide for the Use of the International System of Units (SI) (Thompson and Taylor, 2008) to be used with the gazetteer entity finder.

In the following weeks, the team will continue to work on the current tasks. The work on having the tests pass has been put on hold temporarily to make sure the tests reflect the needs of the downstream consumers (e.g., the Model Analysis team). After a meeting with the Model Analysis team, the potential test cases will be added to the current set of tests and the team will continue the work on having the tests pass.