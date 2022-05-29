#!/bin/bash
# Usage: convert_to_wav.sh [directory with mp3 files] [output directory]
# This script will convert all files in the provided directory to wav files and dump them in output directory.
# Specifically this will also resample the audio to 16khz, mono channel, and 16-bit depth.

mp3dir=$1
wavdir=$2

echo "input directory:  $mp3dir"
echo "output directory: $wavdir"

for i in $(ls $mp3dir)
do
	ffmpeg -i $mp3dir$i -acodec pcm_s16le -ar 16000 -ac 1 "$wavdir$(basename -s .mp3 "$i").wav"
	break
done
