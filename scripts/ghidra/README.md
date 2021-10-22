# Ghidra Refined/Unrefined Plugin

## Running Ghidra scripts in headless mode on carp

Ghidra has been downloaded onto carp into /usr/local/ghidra/ghidra_9.1.2_PUBLIC/. As the name suggests, we have version 9.1.2. In this directory, two scripts have been added to dump out the "refined" and raw P Code of a binary extracted by Ghidra. TODO what exactly does refined represent? 

You can use the following command to run ghidra with one of these scripts:

`/usr/local/ghidra/ghidra_9.1.2_PUBLIC/support/analyzeHeadless <WORKING DIR>/projects <PROJECT NAME> -import <BINARY NAME> -scriptPath <WORKING DIR> -postScript <SCRIPT NAME> -deleteProject`

For the command, substitute:

<WORKING DIR> = The directory you are working within. This directory can be located anywhere.
<PROJECT_NAME> = This is a name for ghidra to create a project under. The name does not matter too much as we have the `-deleteProject` flag is provided to delete it after execution, but it does have to be provided. A value such as NewProject works fine.
<BINARY NAME> = This is the path to the binary you want ghidra to evaluate.
<SCRIPT NAME> = This is the path to the script to run, either `DumpRefined.py` or `DumpUnrefined.py`. When `DumpRefined.py` is run, it puts its results into a file called `<BINARY NAME>-refined-PCode.txt`. Likewise, `DumpUnrefined.py` puts it into a file called `<BINARY NAME>-unrefined-PCode.txt`.