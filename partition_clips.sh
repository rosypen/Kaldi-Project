#!/bin/bash
# Usage: partition_clips.sh [dataset base path]
# This script will read the train_files.txt, dev_files.txt, and test_files.txt files
# in the dataset base path and partition the audio files
# train_files.txt > transcribed
# dev_files.txt > untranscribed
# test_files.txt >  untranscribed-test

base_dir=$1

# Move the train files
echo "Moving train files into $base_dir transcribed/"
while read -r line
do 
    source="$base_dir""clips-wav/$line"
    dest="$base_dir""transcribed/"
    mv $source $dest
done < "$base_dir""train_files.txt"

# Move the dev files
echo "Moving dev files into $base_dir untranscribed/"
while read -r line
do 
    source="$base_dir""clips-wav/$line"
    dest="$base_dir""untranscribed/"
    mv $source $dest
done < "$base_dir""dev_files.txt"

# Move the test files
echo "Moving test files into $base_dir untranscribed-test/"
while read -r line
do 
    source="$base_dir""clips-wav/$line"
    dest="$base_dir""untranscribed-test/"
    mv $source $dest
done < "$base_dir""test_files.txt"