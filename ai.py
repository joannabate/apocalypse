import sounddevice as sd
import json
import sys
import numbers
import speech_recognition as sr
from google.cloud import texttospeech
from playsound import playsound
from os import listdir
from os.path import isfile, join
import random
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

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
      
      if len(text):
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
    def __init__(self, faces, videos):
        
        self.faces = faces
        self.videos = videos

        self.speech_engine = SpeechEngine()
        
        with open('script.json') as json_file:
            self.script = {int(k):v for k,v in json.load(json_file).items()}
        
        self.repeat_question_text = "I'm sorry, I didn't understand that. Can you try again?"
        self.number_list = ['one', 'two', 'three', 'four', 'five', 'six']

        self.is_question = False

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
                if input_text == 'reboot':
                    stage_id.value = 0
                    self.speech_engine.respond("Rebooting")
                    face_id.value = self.faces.index('happy.png')
                    
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
        #First run through
        if stage_id.value == 0:
            stage_id.value = 1
        if self.is_question:
            # Pull question
            for q in self.stage['questions']:
                if q["id"] == self.question_id:
                    question = q
                    break

            stop_words = set(stopwords.words('english'))
            input_tokens = word_tokenize(input_text)
            input_filtered = [w for w in input_tokens if not w.lower() in stop_words]

            answer_common_words = []
            # Loop through answers and get number of common words
            for answer in question['answers']:
                answer_tokens = word_tokenize(answer['text'])
                answer_filtered = [w for w in answer_tokens if not w.lower() in stop_words]

                common_words = list(set(input_filtered).intersection(answer_filtered))
                answer_common_words.append(len(common_words))

            # Find winner
            answer_position = answer_common_words.index(max(answer_common_words))
            answer = question['answers'][answer_position]

            # Say response for answer
            color_id.value = answer['color']
            face_id.value = self.faces.index(answer['face'])
            self.speech_engine.respond(answer['response'])

            # go to next stage
            stage_id.value = stage_id.value + 1
            self.is_question = False

            self.speak_dialog(color_id, face_id, stage_id)

        else:
            self.speak_dialog(color_id, face_id, stage_id)
    
    def speak_dialog(self, color_id, face_id, stage_id):
        print("Speaking dialog for stage " + str(stage_id.value))
        #Pull new stage
        self.stage = self.script[stage_id.value]

        #Loop through dialog
        for line in self.stage['dialog']:
            color_id.value = line['color']
            face_id.value = self.faces.index(line['face'])
            self.speech_engine.respond(line['text'])

        # Select a question at random
        question = random.choice(self.stage['questions'])
        self.is_question = True
        self.question_id = question['id']
        color_id.value = question['color']
        face_id.value = self.faces.index(line['face'])
        self.speech_engine.respond(question['text'])

        for answer in question['answers']:
            print(answer)
            self.speech_engine.respond(str(answer['id']))
            self.speech_engine.respond(answer['text'])
