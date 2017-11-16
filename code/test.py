from gtts import gTTS
import os
import re

def playAudio():
    text = "Hello"
    tts = gTTS(text=text, lang='en')
    file_mp3 = "sound.mp3"
    tts.save(file_mp3)
    os.system("mpg123\mpg123.exe " + file_mp3)
    os.system("clear")

if "__main__" == __name__:
    playAudio()