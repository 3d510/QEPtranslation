from gtts import gTTS
from pygame import mixer
import time

def playAudio(text):
    print("called")
    tts = gTTS(text=text, lang='en')
    file_mp3 = "sound.mp3"
    time.sleep(0.1)
    tts.save(file_mp3)
    mixer.init()
    mixer.music.load(file_mp3)
    mixer.music.play()

if __name__ == '__main__':
    playAudio("hello")