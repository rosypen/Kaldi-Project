from read_tsv import *
from collections import defaultdict

def calculate_wer(df, transcriptions:list):
    '''
    predict has the form [audio.wav prediction]
    '''
    gold_word_count = 0
    incorrect = 0

    for line in transcriptions:
        temp = line.strip().split()
        if not temp:
            continue
        audio_file = temp[0]
        predicted = temp[1:]
        if "h" in predicted:
            predicted.remove("h")

        # Grab word for this clip from the dataframe
        mp3_name = audio_file.replace(".wav", ".mp3")
        result_df = df[df['path'] == mp3_name]
        i = result_df.index[0]
        try:
            word = result_df.at[i,'sentence']
            gold_word_count += 1
            digit = result_df.at[i, 'digit']
        except Exception as e:
            logging.info("Couldn't find the word for {} in the tsv file".format(mp3_name))
            raise(e)
        if word in predicted:
            predicted.remove(word)
        # for i, word in enumerate(words):
        #     gold_word_count +=1
        #     if i > len(predicted):
        #         incorrect +=1
        #         continue
        #     predict = predicted[i]
        #     if word != predict:
        #         incorrect += 1
        if len(predicted) > 0:
            incorrect += (len(predicted))
    print(incorrect)
    print(gold_word_count)
    return incorrect/gold_word_count


def main():
    results = ""
    languages = ["cy", "de"]
    datadir = ["transcribed", "untranscribed"]
    for lang in languages:
        train_tsv = 'datasets/{}/tsv/train.tsv'.format(lang)
        dev_tsv = 'datasets/{}/tsv/dev.tsv'.format(lang)
        digit_file = 'datasets/{}/digits.txt'.format(lang)

        for dir in datadir:
            if dir == "transcribed":
                df = load_data(train_tsv, digit_file)
                results += f"{lang} train WER: "
            else:
                df = load_data(dev_tsv, digit_file)
                results += f"{lang} test WER:  "
            with open(f'datasets/{lang}/{dir}/transcriptions.txt') as transcriptions:
                wer = calculate_wer(df, transcriptions.readlines())
                results += "{:.2f}%\n".format(wer * 100)
    print(results)
            




if __name__ == "__main__":
    main()