import sounddevice as sd
import json
import sys
import numbers
import speech_recognition as sr
from google.cloud import texttospeech
from playsound import playsound
from os import listdir
from os.path import isfile, join

import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="apocalypse-roomservice-6bebad941d3f.json"


class SpeechEngine:
   def __init__(self):
      self.is_speaking = False
      self.client = texttospeech.TextToSpeechClient()

      # Note: the voice can also be specified by name.
      # Names of voices can be retrieved with client.list_voices().
      self.voice = texttospeech.VoiceSelectionParams(
         language_code="en-US",
         name="en-US-Standard-C",
         ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
      )

      self.audio_config = texttospeech.AudioConfig(
         audio_encoding=texttospeech.AudioEncoding.MP3
      )
      
   def respond(self, text):

      self.speaking_text = text
      self.is_speaking = True

      """Synthesizes speech from the input string of text."""

      print("AI --> [", text, "]")

      input_text = texttospeech.SynthesisInput(text=text)

      response = self.client.synthesize_speech(
         request={"input": input_text, "voice": self.voice, "audio_config": self.audio_config}
      )

      # The response's audio_content is binary.
      with open("output.mp3", "wb") as out:
         out.write(response.audio_content)

      playsound('output.mp3')
       

class AI:
    def __init__(self):
        
        self.faces = [f for f in listdir('faces') if isfile(join('faces', f))]

        self.speech_engine = SpeechEngine()
        
        with open('script.json') as json_file:
            self.script = {int(k):v for k,v in json.load(json_file).items()}
        
        self.direct_control = False
        
        self.repeat_question_text = "I'm sorry, I didn't understand that. Can you give me a clear yes or no?"
        self.yes_words = ['yes', 'yep', 'ya', 'yeah', 'yea', 'sure', 'okay', 'i am', 'i shall',
                          'positive', 'totally', 'totes', 'you bet', 'okie dokie',
                          'alright', 'good', 'certainly', 'definitely', 'of course', 'probably',
                          'gladly', 'indubitably', 'absolutely', 'indeed', 'undoubtedly',
                          'fine', 'affirmative', 'very well', 'obviously', 'aye']
        self.no_words = ['no', 'now', 'nah', 'nope', 'no way', 'not', 'negative', 'sorry',
                         'not', 'pass', 'another time', 'if only', 'bow out', "can't",
                         "don't", 'wish', 'wont', 'sorry', 'apologies']
        self.number_list = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven']

    def callback(self, indata, frames, time, status):
        # This is called (from a separate thread) for each audio block
        if status:
            print(status, file=sys.stderr)
        self.q.put(bytes(indata))

    def run(self, color_id, face_id, stage_id):
        input_text = None
        
        r = sr.Recognizer()

        while True:

            with sr.Microphone() as source:
                print("Say something!")
                audio = r.listen(source)

            # recognize speech using Google Speech Recognition
            try:
                # for testing purposes, we're just using the default API key
                # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
                # instead of `r.recognize_google(audio)`
                input_text = r.recognize_google(audio)
                print("me --> [", input_text, "]")
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))

            if input_text:
                if input_text in('reboot', 'exit'):
                    stage_id.value = 0
                    if self.direct_control:
                        self.direct_control = False
                    self.speech_engine.respond("Rebooting")
                    face_id.value = 99
                    
                elif input_text == 'direct control':
                    self.speech_engine.respond("Entering direct control mode")
                    self.direct_control = True
                    
                elif 'go to stage' in input_text:
                    for number in self.number_list:
                        if number in input_text:
                            n = self.number_list.index(number) + 1
                            stage_id.value = n
                            print('going to stage ' + str(n))
                            self.speak_dialog(color_id, face_id, stage_id)
                            break
                            
                else: #We have any other sort of text
                    self.process_text(input_text, color_id, face_id, stage_id)

            input_text = None

    def process_text(self, input_text, color_id, face_id, stage_id):
        if self.direct_control:
            self.speech_engine.respond(input_text)
            return
        #First run through
        elif stage_id.value == 0:
            stage_id.value = 1
        #We don't care what the text is
        elif isinstance(self.stage['goto'], numbers.Number):
            stage_id.value = self.stage['goto']
        elif self.is_no(input_text):
            #Find the next stage based on the last stage's goto logic
            stage_id.value = self.stage['goto']['no']
        elif self.is_yes(input_text):
            #Find the next stage based on the last stage's goto logic
            stage_id.value = self.stage['goto']['yes']
        else:
            #We don't know what this text is, ask to repeat
            self.speech_engine.respond(self.repeat_question_text)
            return
        self.speak_dialog(color_id, face_id, stage_id)
    
    def speak_dialog(self, color_id, face_id, stage_id):
        #Pull new stage
        self.stage = self.script[stage_id.value]

        #Loop through dialog
        for line in self.stage['dialog']:
            color_id.value = line['color']
            face_id.value = self.faces.index(line['face'])
            self.speech_engine.respond(line['text'])
        
        if 'goto' not in self.stage:
            stage_id.value = 0
            face_id.value = 99
            
    def is_yes(self, input_text):
        if len(input_text) == 0:
            return False

        for word in self.yes_words:
            if word in input_text:
                return True
            elif input_text[-1] == 's':
                return True
        return False
            
    def is_no(self, input_text):
        if len(input_text) == 0:
            return False

        for word in self.no_words:
            if word in input_text:
                return True
        return False
