import json
import urllib.request

import pandas as pd
from tatoebatools import ParallelCorpus
import spacy
nlp = spacy.load("zh_core_web_sm")
from zhconv import convert

def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}

def invoke(action, **params):
    requestJson = json.dumps(request(action, **params)).encode('utf-8')
    response = json.load(urllib.request.urlopen(urllib.request.Request('http://localhost:8765', requestJson)))
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error'])
    return response['result']

def toSimplified(str):
    return convert(str, "zh-cn")


FIELD_WORD = "Simplified"
FIELD_SENTENCE = "SentenceSimplified"
FIELD_CLOZE = "SentenceSimplifiedCloze"
FIELD_TRANSLATION = "SentenceMeaning"


def getChineseCards():
    selectedDeck = "..P::.LANG::Chinese"
    # selectedDeck = "deck:zTEST::Chinese"
    print("Chinese cards....", "deck:{}".format(selectedDeck))
    # chineseCards = invoke("findCards", query='deck:...P::.LANG::Chinese')
    # chineseCards = invoke("findCards", query='deck:current')
    chineseCards = invoke("findCards", query=selectedDeck)
    # cardsToNotes
    chineseNotes = invoke("cardsToNotes", cards=chineseCards)
    print("Chinese NOTES are")
    print(chineseNotes, "...")

    # find notes with missing sentence
    print("Chinese NOTES with MISSING SENTENCE")
    notes = []
    notesInfo = invoke("notesInfo", notes=chineseNotes)

    notesInfoWithoutSentence = [noteInfo for noteInfo in notesInfo if noteInfo['fields'][FIELD_SENTENCE]['value'] == '']

    # word - noteId - [sentences] - [clozeSentences] - [translations]
    words = {}
    for noteInfo in notesInfoWithoutSentence:
        word = noteInfo['fields'][FIELD_WORD]['value']
        noteId = noteInfo['noteId']
        words[word] = [word, noteId, [], [], []]
        # print(noteInfo['fields'][FIELD_SENTENCE])
        print(word)
    print(words)

    chineseSentences = ParallelCorpus("cmn", "eng")
    count = 0
    for sentence, translation in chineseSentences:
        # print(sentence.text, translation.text)
        if count < 1000000:
            if (count % 100 == 0):
                print(count)
            sentence_text = toSimplified(sentence.text)
            zh_tokens = nlp(sentence_text)
            for token in zh_tokens:
                if token.text in words and len(words[token.text][2]) <= 5:
                    # Add sentence
                    words[token.text][2].append(sentence_text)
                    # add cloze deletion
                    words[token.text][3].append(sentence_text.replace(token.text, "[ ]"))
                    # add translation
                    words[token.text][4].append(translation.text)
            count+=1
        else:
            break
    df = pd.DataFrame.from_dict(words, orient='index', columns=['word', 'note_id', 'sentences', 'sentences_cloze', 'en_translations'])
    df.to_csv("./sentences.csv")
    return df

def df_to_anki(df):
    #save the sentences to anki
    for index, row in df.iterrows():
        print(row, row['sentences'])
        word = row['word']
        note_id = row['note_id']
        sentences = row['sentences']
        sentences_cloze = row['sentences_cloze']
        en_translations = row['en_translations']
        if len(sentences) > 0:
            # print(row, sentences[0])
            index = 0
            # keep sentence short
            for i in range(len(sentences) - 1):
                if len(sentences[i]) > 25:
                    index += 1

            #update
            invoke("updateNoteFields", note={"id":note_id, "fields":{
                FIELD_SENTENCE:sentences[index],
                FIELD_CLOZE:sentences_cloze[index],
                FIELD_TRANSLATION:en_translations[index],
            }})
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    sentences_df = getChineseCards()
    df_to_anki(sentences_df)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
