# nao_say.py
from nao_conf import *
from naoqi import ALProxy
tts = ALProxy("ALTextToSpeech", IP, 9559)


def say(text):
    tts.say(text)