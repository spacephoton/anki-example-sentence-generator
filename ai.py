# import pandas as pd

# df = pd.read_pickle('word_sentences.pkl')

# # print(df)

import os
import openai
import json

openai.api_key = os.getenv("OPENAI_API_KEY")

def translate(object):
  json_object = json.dumps(object)
  completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
      {"role": "system", 
       "content": \
        "You are a translator. You are given a json input with the following data:\n\
          word: a word in Portuguese.\n\
          sentence: a Portuguese sentence using this word.\n\
          You return a response as a JSON object. Each field is a string without any special characters or new lines. You only return this object and nothing else. The fields are:\n\
          word_translation: An English translation of the word, considering the context of the given sentence. This is a concise word only.\n\
          sentence_translation: An English translation of the sentence. Keep it simple and complete.\n\
          "\
          },
      {"role": "user", "content": json_object}
    ]
  )
  return completion

response = (translate({
  "word": "casa",
  "sentence": "Eu moro em uma casa"
}))

print(response)
content = response["choices"][0]["message"]["content"]
print(content)

parsedResponse = json.loads(content)
print(parsedResponse)