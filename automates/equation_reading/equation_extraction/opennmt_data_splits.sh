#!/bin/bash

# as seen on https://unix.stackexchange.com/a/220394
get_seeded_random() {
    seed="$1"
    openssl enc -aes-256-ctr -pass pass:"$seed" -nosalt </dev/zero 2>/dev/null
}

# collect data and shuffle it
ls *src_images.txt    | sort | xargs cat | shuf --random-source=<(get_seeded_random 426) > all_images.txt
ls *tgt_equations.txt | sort | xargs cat | shuf --random-source=<(get_seeded_random 426) > all_equations.txt

# get number of datapoints
N_LINES=$(wc -l all_images.txt | awk '{print $1}')

# calculate data splits (80-10-10)
VAL_START=1
VAL_END=$(echo "$N_LINES / 10" | bc)
TEST_START=$((VAL_END+1))
TEST_END=$((TEST_START+VAL_END))
TRAIN_START=$((TEST_END+1))
TRAIN_END=$N_LINES

sed -n "$VAL_START,$VAL_END p" all_images.txt > src_val.txt
sed -n "$VAL_START,$VAL_END p" all_equations.txt > tgt_val.txt
sed -n "$TEST_START,$TEST_END p" all_images.txt > src_test.txt
sed -n "$TEST_START,$TEST_END p" all_equations.txt > tgt_test.txt
sed -n "$TRAIN_START,$TRAIN_END p" all_images.txt > src_train.txt
sed -n "$TRAIN_START,$TRAIN_END p" all_equations.txt > tgt_train.txt
