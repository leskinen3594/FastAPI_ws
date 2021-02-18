from google.cloud import translate_v2 as translate
import os
import pandas as pd

def translation(input_text):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"./GoogleCloudKey_GoogleTranslate.json"

    translate_client = translate.Client()

    #  input_text = "Good Morning"
    target = 'de'   # de = German Language

    result = translate_client.translate(input_text, target_language=target)

    getLang_result = translate_client.get_languages()
    #  language_list = pd.DataFrame(getLang_result)

    #  print(f"Translated: {result}")
    #  print(language_list)
    return result

#  translation("Good morning")
