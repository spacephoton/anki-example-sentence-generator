# import pandas as pd

# df = pd.read_pickle('word_sentences.pkl')

# # print(df)

import os
import openai
import json

openai.api_key = os.getenv("OPENAI_API_KEY")

from typing import TypedDict

class TranslationData(TypedDict):
    word: str
    sentence: str
    context: str

def translate(object: TranslationData):
  try:
    json_object = json.dumps(object)
    completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "system", 
        "content": \
          "You are a translator. You are given a json input with the following data:\n\
            word: a word in Portugal Portuguese.\n\
            sentence: a Portugal Portuguese sentence using this word.\n\
            context: The sentence in its context.\n\
            You return a response as a JSON object. Each field is a string without any special characters or new lines. You only return this object and nothing else. Follow the requirements for each field strictly. The fields are:\n\
            word_translation: An English translation of the word, considering the sentence and the context of the given sentence. This is a concise word only.\n\
            sentence_translation: An English translation of the sentence. Keep it simple and DO NOT INCLUDE the context (it's only there to help you understand the sentence).\
              The word translation has to be included! Sometimes the translation has some slang.\
              Don't give a literal translation. Translate the intended meaning in Portuguese of Portugal. Only translate the sentence and nothing else.\n\
            context_translation: An English translation of the context which includes the sentence. The sentence_translation should be included here.\
            "\
            },
        {"role": "user", "content": json_object}
      ]
    )
    content = completion["choices"][0]["message"]["content"]
    return json.loads(content)
  except Exception as e:
    # Exception handling code
    print(f"Error: {e}")
    return {}