# Author: Rosetta Pendleton
# This file is for creating transcription files (eaf) for the audio clips provided by Mozilla Common Voice
# https://commonvoice.mozilla.org/en/datasets
# Eaf files can have multiple tiers of annotation (eg. phonetic pronunciation, orthographic form, gloss, etc.)
# We could potentially have tier 0 be the orthorgraphic transcription and tier 1 be the corresponding digit

from read_tsv import *
import pympi

import logging

logging.basicConfig(level = logging.INFO)

def main(lang:str):
     '''
     lang: should be one of [cy|br|de]
     '''
     train_tsv = 'datasets/{}/tsv/train.tsv'.format(lang)
     digit_file = 'datasets/{}/welsh_digits.txt'.format(lang)
     train_df = load_data(train_tsv, digit_file)

     # Train_files.txt is just a text file that has the names of all the audio files in the train set.
     # Eg. common_voice_cy_22287428.wav
     # The eaf file will have the same name except .eaf instead of .wav
     train_file = 'datasets/{}/train_files.txt'.format(lang)
     logging.info("transcribing train set from: {}".format(train_file))

     train_clips = open(train_file, 'r')
     lines = train_clips.readlines()
     missing = 0
     for clip_name in lines:
          eaf_name = clip_name.replace(".wav\n", ".eaf")
          eaf_file = 'datasets/{}/transcribed/{}'.format(lang, eaf_name)

          # Create an eaf object
          eaf = pympi.Elan.Eaf()
          eaf.add_language(lang)

          # Grab word for this clip from the dataframe
          mp3_name = clip_name.replace(".wav\n", ".mp3")
          result_df = train_df[train_df['path'] == mp3_name]
          i = result_df.index[0]
          try:
               word = result_df.at[i,'sentence']
          except Exception as e:
               logging.info("Couldn't find the word for {} in the tsv file".format(mp3_name))
               missing +=1

          # Add annotations to the eaf object
          # NOTE: add_annotation(id_tier, start, end, value='', svg_ref=None); start/end timestamps need to be in miliseconds
          # TODO: Find where the utterance starts in the audio file.
          eaf.add_tier('Phrase') # I think I am also supposed to add a linguistic type??? but not sure what those are.
          eaf.add_annotation('Phrase', 0, 1000, word)
          # So ideally, we would also have each sound/letter in the word annotated to the millisecond
          # eaf.add_tier('Segment')
          # for sound in word:
          #    eaf.add_annotation('Segment', start, end, sound)
          
          # Write the eaf object to a file.
          eaf.to_file(eaf_file)
          break
     logging.info("Missing {} transcriptions of {} files".format(missing, len(lines)))

if __name__ == "__main__":
    main("cy")