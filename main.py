import pysubs2
import spacy
import re
import pandas as pd
from collections import defaultdict, Counter
from connect import invoke


print('running main.py')

nlp = spacy.load("pt_core_news_sm")

word_frequencies = Counter()
word_sentences = defaultdict(lambda: {"sentence": "", "sentence_previous": "", "sentence_next": ""})

subs = pysubs2.load("tide_pt.srt", format_="srt", encoding="utf-8")
subs.shift(s=2.5)

events = []
used_sentences = set()

for event in subs:
    text = event.text

    # Remove unwanted text
    text = re.sub(r'\[.*?\]', '', text)  # Remove text within []
    text = text.replace('\\N', ' ').replace('{\\an8}', '').replace('{\\i0}', '') # Remove unwanted special characters
    text = text.replace('i0}', '').replace('{\\i1}', '')
    text = re.sub(r'[^\w\s.,?!]', '', text)  # Remove any character that is not a word character, space or .,?!

    doc = nlp(text)
    for sent in doc.sents:
        events.append({"text": sent.text, "start": event.start, "end": event.end})

for i in range(len(events)):
    event = events[i]
    sentence = nlp(event["text"].strip())
    non_stop_words = [word for word in sentence if not word.is_stop and not word.is_punct]
    if len(non_stop_words) < 2:  # Skip sentence if it contains less than two non-stop words
        continue
    
    named_entities = {ent.text for ent in sentence.ents}  # Set of all named entities in the sentence

    for word in non_stop_words:
        if word.text in named_entities:  # Skip named entities
            continue
        if len(sentence.text) > len(word_sentences[word.text]["sentence"]) and len(sentence.text) < 70 and len(sentence.text) > 14:
            word_frequencies[word.text] += 1
            if (sentence.text not in used_sentences):
                if (word_sentences[word.text]["sentence"] in used_sentences):
                    used_sentences.remove(word_sentences[word.text]["sentence"])
                start_time = str(event["start"])
                end_time = str(event["end"])
                word_sentences[word.text] = {
                    "sentence": sentence.text,
                    "start_time": start_time, 
                    "end_time": end_time, 
                    "lemma": word.lemma_,
                    "sentence_previous": events[i - 1]["text"] if i > 0 else "", 
                    "sentence_next": events[i + 1]["text"] if i < len(events) - 1 else "",
                    "words": [w.text for w in non_stop_words], # Add the non-stop words of the sentence
                    "lemmas": [w.lemma_ for w in non_stop_words]  # Add the non-stop words of the sentence
                }
                used_sentences.add(sentence.text)

filtered_word_sentences = {word: data for word, data in word_sentences.items() if (len(word) >= 3 and word_frequencies[word] >= 3 and data.get('start_time'))}

# Convert the filtered_word_sentences dictionary to a pandas DataFrame
df = pd.DataFrame.from_records([
    {"word": word,
     "lemma": data["lemma"],
     "sentence": data["sentence"],
     "start_time": data["start_time"],
     "end_time": data["end_time"],
     "sentence_previous": data["sentence_previous"],
     "sentence_next": data["sentence_next"],
     "occurrences": word_frequencies[word],
     "words": data["words"],
     "lemmas": data["lemmas"]
     }  # Include the sentence words
    for word, data in filtered_word_sentences.items()
])

# Save DataFrame to a CSV file
df.to_csv('word_sentences.csv', index=False)
df.to_pickle('word_sentences.pkl')
