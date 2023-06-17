import pandas as pd
from ai import translate

def translate_sentences(name: str, skip=False):
    df = pd.read_pickle('{}.pkl'.format(name))

    print(df)
    print(df.columns)
    if ('word_translation' not in df.columns):
        print('setting skip to false, no translations here')
        skip = False

    for index, row in df.iterrows():
        if (not skip) or (skip and ((not isinstance(row['word_translation'], str) or (not isinstance(row['sentence_translation'], str))))):
            translation = translate({
                            "word": row['word'],
                            "sentence": row['sentence'],
                            })
            if (translation.get("word_translation") and translation.get("sentence_translation")):
                df.loc[index, 'word_translation'] = translation["word_translation"]
                df.loc[index, 'sentence_translation'] = translation["sentence_translation"]
                # df.loc[index, 'context_translation'] = translation["context_translation"]
                print(row)
            else:
                print("Invalid translation", translation)
        else:
            print("Skipping row")
                
        df.to_csv('{}.csv'.format(name), index=False)
        df.to_pickle('{}.pkl'.format(name))
    
    
translate_sentences("word_sentences", True)