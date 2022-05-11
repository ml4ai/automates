# sample file to run the batch_tokenize_instructions_v2.py

python batch_tokenize_instructions_v3.py -I expr_v2_perfect/expr_v2_0236810-large \
-i expr_v2_0236810__Linux-5.4.0-81-generic-x86_64-with-glibc2.31__gcc-10.1.0-instructions.txt \
-D expr_v2_perfect/output

# tokenize all instructions.txt files in the expr_v2 folder recursively and put the
# result into the output folder
python batch_tokenize_instructions_v3.py -I expr_v2_perfect -D expr_v2_perfect/output