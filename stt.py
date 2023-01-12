from vosk import Model, KaldiRecognizer
import wave
import json


MODEL = r"/home/mdls/vosk-model-small-ru-0.22"
model = Model(MODEL)
voska = KaldiRecognizer(model, 16000)

def speech2text(path):
    wf = wave.open(path, "rb")
    result = ''
    last_n = False
    while True:
        data = wf.readframes(16000)
        if len(data) == 0:
            break
        if voska.AcceptWaveform(data):
            res = json.loads(voska.Result())
            if res['text'] != '':
                result += f" {res['text']}"
                last_n = False
            elif not last_n:
                result += '\n'
                last_n = True
    res = json.loads(voska.FinalResult())
    result += f" {res['text']}"
    return result
