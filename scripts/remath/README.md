## Top-level Parallel Corpus Generation

- `batch_corpus_generator_v2.py` : Top-level script to generate parallel 
  corpus by orchestrating the other scripts.
  Involves these steps:
  - generate C program using gen_c_v2
  - test execution of C program; if executes, then continue, otherwise try 
    again with a new generation.
  - compile binary using gcc-ast-dump plugin -- results in GCC-compiled binary 
    as gcc_ast file.
  - Ghidra-analyze binary to extract instructions
  - tokenize instructions.
  - translate gcc_ast into CAST
  - tokenize CAST.
  
  NOTE: This script uses python multiprocessing.
  It has been observed that the multiprocessing process dies after some 
  number of steps in the generation process and it's unclear why.


## Generate C Program

- `gen_c_prog_v1.py` : (Fall 2021) The initial prototype generator. This has 
  not been used for training models.
- `gen_c_prog_v2.py` : (Fall 2021) Generates expression trees within main.
- `gen_c_prog_v3.py` : (Spring 2022) Generates functions and main, globals.


## Ghidra binary analysis and instruction extraction

- `batch_ghidra_program_plugin.py`
Executes Ghidra with `DumpInstructionsByFunction.py` plugin (under 
  `<automates/scripts/ghidra/>`). 
Ghidra performs binary analysis, then plugin is executed: for each 
  Ghidra-identified function, extract the associated instructions (address, 
  instruction set, any interpreted values). The instructions per function 
  are saved to a `<binary-filename>-instructions.txt` file (this filename is 
  specified in 
  the `DumpInstructionsByFunction.py` Ghidra plugin). 


## Tokenization

- `batch_tokenize_instructions.py`
Read `<binary-filename>-instructions.txt` file and parse instructions to 
  generate `<>__tokens.txt` of input token sequence. This represents the 
  input token sequence to the NMT2Code model.
Also adds to `tokens_summary.txt`.

- `cast_to_token_cast.py`
Given CAST input, generates tokenized-CAST sequence. This represents the 
  output token sequence that NMT2Code model is to predict.


## Misc
Miscellaneous scripts that were developed at various points as stand-alone 
scripts but are not used in the coordinated parallel corpus generation.

- `batch_compile.py`
- `batch_execute_test.py`