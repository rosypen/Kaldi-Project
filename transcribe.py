# Author: Rosetta Pendleton
# This file is for creating transcription files (eaf) for the audio clips provided by Mozilla Common Voice
# https://commonvoice.mozilla.org/en/datasets
# Eaf files can have multiple tiers of annotation (eg. phonetic pronunciation, orthographic form, gloss, etc.)
# We could potentially have tier 0 be the orthorgraphic transcription and tier 1 be the corresponding digit

from read_tsv import *

import logging, wave, json

import pympi
from vosk import Model, KaldiRecognizer, SetLogLevel
import Word as word

logging.basicConfig(level = logging.INFO)
# Disable logs for vosk
SetLogLevel(-1)

def get_wav_duration(f):
     frames = f.getnframes()
     rate = f.getframerate()
     duration = frames / float(rate)
     # print(duration)
     return duration

def duration_is_zero(result_dict):
     start = float(result_dict['start'])
     end = float(result_dict['end'])
     return end - start < 0.5

def get_timestamps(wav_file:str)->word.Word:
     '''
     Given a wave file path, this method actually returns a single Word that was spoken in the audio.
     The word looks something like:

     {'conf': 0.84, # confidence
     'end': 4.5, # end time
     'start': 4.05, # start time
     'word': 'test'},

     This is information is extracted by using a small model trained on German from Vosk.
     The predicted transcribed word itself is not that important to us right now.

     We want the start and end times.

     Most of this code is from the Vosk Getting Started template
     https://towardsdatascience.com/speech-recognition-with-timestamps-934ede4234b2
     '''
     model_path = "vosk-model-small-de-0.15"
     audio_filename = wav_file

     model = Model(model_path)
     wf = wave.open(audio_filename, "rb")
     rec = KaldiRecognizer(model, wf.getframerate())
     rec.SetWords(True)

     # get the list of JSON dictionaries, tbh I'm not sure if we even need to do this for one word.
     results = []
     # recognize speech using vosk model
     while True:
          data = wf.readframes(4000)
          if len(data) == 0:
               break
          if rec.AcceptWaveform(data):
               part_result = json.loads(rec.Result())
               results.append(part_result)
     part_result = json.loads(rec.FinalResult())
     results.append(part_result)
     
     # So by default I'm just going to assume that for all utterances the word starts at the first second and ends by the end of the clip.
     audio_end = get_wav_duration(wf)
     default = word.Word({'conf':0.0, 'start':'1', 'end':str(audio_end), 'word':""})
     wf.close()

     # Return the last non-empty "result/word" that was detected from the KaldiRecognizer
     for i in range(len(results) -1, -1, -1):
          final_result = results[i]
          if len(final_result) == 1 or duration_is_zero(final_result['result'][0]):
               # Apparently this indicates the result is empty
               continue
          info = word.Word(final_result['result'][0])
          return info
     # If no word was found return the default
     return default

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
          wav_file = 'datasets/{}/transcribed/{}'.format(lang, clip_name.strip())
          timestamp_results = get_timestamps(wav_file)
          start = int(float(timestamp_results.start) *1000)
          end = int(float(timestamp_results.end) *1000)

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
               digit = result_df.at[i, 'digit']
          except Exception as e:
               logging.info("Couldn't find the word for {} in the tsv file".format(mp3_name))
               missing +=1
               continue

          # Add annotations to the eaf object
          # NOTE: add_annotation(id_tier, start, end, value='', svg_ref=None); start/end timestamps need to be in miliseconds
          eaf.add_tier('Phrase') # I think I am also supposed to add a linguistic type??? but not sure what those are.
          eaf.add_annotation('Phrase', start, end, word)
          eaf.add_tier('Digit') # I think I am also supposed to add a linguistic type??? but not sure what those are.
          eaf.add_annotation('Digit', start, end, str(digit))
          
          # Write the eaf object to a file.
          eaf.to_file(eaf_file)
     logging.info("Missing {} transcriptions of {} files".format(missing, len(lines)))

if __name__ == "__main__":
    main("cy")