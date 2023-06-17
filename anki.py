import pandas as pd

# selectedDeck = "pt"
# cards = invoke("findCards", query="deck:{}".format(selectedDeck))

# print(cards)

# decks = invoke('addNote', notes=[{
#     "deckName": "pt",
#     "modelName": "Basic",
#     "fields": {
#         "Front": "front content",
#         "Back": "back content"
#     },
# })

# print(decks)



def upload_to_anki(name: str):
    modelName = "Cotoki Word Sentence (and reversed card)"
    df = pd.read_pickle('{}.pkl'.format(name))
    print(df)
    print(df.columns)
    notesToAdd = []
    
    for index, row in df.iterrows():
        notesToAdd.append({
            "deckName": "pt",
            "modelName": modelName,
            "fields": {
                "Word": row['word'],
                "Sentence": row['sentence'],
                "WordTranslation": row['word_translation'],
                "SentenceTranslation": row['sentence_translation'],
            }
        })
        print(row)
    print(notesToAdd)
   
upload_to_anki("word_sentences_translated") 