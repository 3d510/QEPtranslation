from gtts import gTTS
import os
import re


def playAudio(text_path):
    if not os.path.exists(text_path):
        print('Text path %s is incorrect' % text_path)
        return
    with open(text_path, 'r') as f:
        text = f.read().replace(".", " point ")

    text = re.sub(r'(?<=[\d])\.(?=[\d])', ' point ', text)  # replace floating point with 'point' for voice

    tts = gTTS(text=text, lang='en')
    file_mp3 = os.path.join('..', 'data', 'mp3', text_path.split(os.path.sep)[-1].replace('.txt', '.mp3'))
    tts.save(file_mp3)
    print(file_mp3)

    os.system("mpg123\mpg123.exe " + file_mp3)
    os.system("clear")

