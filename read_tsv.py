# Author: Rosetta Pendleton
# This file is for reading the tsv files provided by Common Voice
# https://commonvoice.mozilla.org/en/datasets
# In addition to the Common Voice dataset, this library also relies on a
# text file that holds the translations of word to digit for digits 0-9

import pandas as pd
from collections import defaultdict
import logging

logging.basicConfig(level = logging.INFO)

def get_word_to_digit_dict(file_path:str) -> dict:
    ''''Given a file where each line has the form 
    <text> <digit>
    This function returns a dictionary matching the word for the digit in some language
    and the digit as an integer.'''
    digits_file = open(file_path)
    word_to_digit = dict()
    for line in digits_file:
        word, digit = line.strip().split()
        word_to_digit[word] = int(digit)
    digits_file.close()
    return word_to_digit

def load_data(file_path:str) -> pd.DataFrame:
    '''
    This function takes in a file path to a tsv file and returns a dataframe that has
    client_id
    path
    sentence
    age	
    gender	
    accent	
    locale	
    segment
    '''
    # Create digit dictionary
    welsh_to_digit = get_word_to_digit_dict('welsh_digits.txt')

    # Read TSV file
    logging.info("Loading data from '{}'".format(file_path))
    df = pd.read_csv(file_path,sep='\t', header=0)
    df['digit'] = pd.NaT
    logging.info("Approximately {} speakers in the data.".format(len(df)//10))
    # Speakers = { gender: 
    #               { age: count}
    #             }
    speakers = dict()

    # Add digit column and collect speaker data
    for ind in df.index:
        word = df['sentence'][ind]
        digit = welsh_to_digit[word]
        df['digit'][ind] = digit
        # This is kind of a hack, roughly every 10 lines is a new speaker but that
        # is an assumption I am making based on the data.
        if ind%10 == 0:
            gender = df['gender'][ind]
            age = df['age'][ind]
            if gender not in speakers:
                speakers[gender] = defaultdict(int)
            speakers[gender][age] += 1
    logging.info(speakers_as_string(speakers))
    return df

def speakers_as_string(speakers:dict):
    result = "Speakers\nGender > Age\n"
    for gender, age_dict in speakers.items():
        total = sum([count for count in age_dict.values()])
        result += str(gender) + " ({})\n".format(total)
        for age, count in age_dict.items():
            result += "> {}: {}".format(age, count) + "\n"
    return result

if __name__ == "__main__":
    dev_df = load_data('common-voice-digits/cy/dev.tsv')