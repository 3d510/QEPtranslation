from gtts import gTTS
import os

def playAudio(text):
    tts = gTTS(text=text, lang='en')
    file_mp3 = "sound.mp3"
    tts.save(file_mp3)
    os.system("mpg123 " + file_mp3)
    os.system("clear")

if __name__ == '__main__':
    playAudio("hello")