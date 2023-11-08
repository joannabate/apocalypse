import speech_recognition as sr
from google.cloud import texttospeech
from playsound import playsound
import random
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import time
import helpers
import os
from wrapper import RedisWrapper

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="apocalypse-roomservice-6bebad941d3f.json"


class SpeechEngine:
   def __init__(self):
      self.client = texttospeech.TextToSpeechClient()

      self.voice_name = "en-US-Standard-C"

      self.audio_config = texttospeech.AudioConfig(
         audio_encoding=texttospeech.AudioEncoding.MP3
      )
      
   def respond(self, text):
      
      if len(text):
        """Synthesizes speech from the input string of text."""

        print("AI --> [", text, "]")

        input_text = texttospeech.SynthesisInput(text=text)

        # Note: the voice can also be specified by name.
        # Names of voices can be retrieved with client.list_voices().
        voice = texttospeech.VoiceSelectionParams(
            language_code=self.voice_name[:-4] ,
            name=self.voice_name,
            # ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
        )

        response = self.client.synthesize_speech(
            request={"input": input_text, "voice": voice, "audio_config": self.audio_config}
        )

        # The response's audio_content is binary.
        with open("output.mp3", "wb") as out:
            out.write(response.audio_content)

        playsound('output.mp3')
       

class AI:
    def __init__(self, use_redis=False):
        
        self.colors, self.color_list = helpers.build_colors()
        self.faces = helpers.build_faces()
        self.videos = helpers.build_videos()
        self.script = helpers.build_script()
        self.archetypes = helpers.build_archetypes()

        self.ignore_answer = False
        self.num_stages = len(self.script)
        self.speech_engine = SpeechEngine()
        self.repeat_text = "Please try again"
        self.score = 0

        self.use_redis = use_redis
        if use_redis:
            self.r = RedisWrapper()

    def run(self, color_id, face_id, stage_id, question_id, question, answer_id, answered, archetype_id, archetype, pulsing, sensor_flag, show_image, video_id):
        input_text = None
        
        r = sr.Recognizer()
        m = sr.Microphone()
        with m as source:
            r.adjust_for_ambient_noise(source)  # we only need to calibrate once, before we start listening

        while True:
            with m as source:
                print("Say something!")
                audio = r.listen(source, 10, 3)

            if sensor_flag.value:
                # recognize speech using Google Speech Recognition
                try:
                    # for testing purposes, we're just using the default API key
                    # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
                    # instead of `r.recognize_google(audio)`
                    input_text = r.recognize_google(audio)
                    print("me --> [", input_text, "]")
                    self.process_text(input_text, color_id, face_id, stage_id, question_id, question, answer_id, answered, archetype_id, archetype, pulsing, show_image, video_id)
                except sr.UnknownValueError:
                    if question.value == True:
                        self.speech_engine.respond(self.repeat_text)
                    else:
                        print("Google Speech Recognition could not understand audio")
                except sr.RequestError as e:
                    print("Could not request results from Google Speech Recognition service; {0}".format(e))
                except Exception as e:
                    print(e)
                    self.speech_engine.respond("Network error")

            else:
                print("Ignoring audio")

            input_text = None

    def process_text(self, input_text, color_id, face_id, stage_id, question_id, question, answer_id, answered, archetype_id, archetype, pulsing, show_image, video_id):
        if question.value:
            # Pull question
            question_dict = self.stage['questions'][question_id.value]
            input_tokens = word_tokenize(input_text.lower())

            answer_common_words = []
            # Loop through answers and get number of common words
            for answer in question_dict['answers']:
                answer_tokens = word_tokenize(answer['text'].lower())
                common_words = list(set(input_tokens).intersection(answer_tokens))
                answer_common_words.append(len(common_words))

            # If we have no matching words and we're not ignoring the response:
            if (max(answer_common_words) == 0) and (not self.ignore_answer):
                self.speech_engine.respond(self.repeat_text)
                return

            else:
                # Find winner
                answered.value = True
                answer_id.value = answer_common_words.index(max(answer_common_words))
                answer = question_dict['answers'][answer_id.value]

                # Add to tally
                self.score = self.score + answer_id.value

                # Update variables but don't say anything
                self.update_variables(answer, color_id, face_id, pulsing, show_image, text=False, response=False)

                if stage_id.value > 0 and (not self.ignore_answer):
                    # Pause a moment
                    print('sleeping...')
                    time.sleep(2)

            question.value = False
            answered.value = False

            # Update variables and say response
            self.update_variables(answer, color_id, face_id, pulsing, show_image, text=False, response=True)

            # go to next stage, or back to start
            if stage_id.value == self.num_stages-1:
                print("sleeping...")
                time.sleep(30)
                stage_id.value = 0
            else:
                stage_id.value = stage_id.value + 1

            self.speak_dialog(color_id, face_id, stage_id, question_id, question, answer_id, answered, archetype_id, archetype, pulsing, show_image, video_id)

        else:
            self.speak_dialog(color_id, face_id, stage_id, question_id, question, answer_id, answered, archetype_id, archetype, pulsing, show_image, video_id)
    
    def speak_dialog(self, color_id, face_id, stage_id, question_id, question, answer_id, answered, archetype_id, archetype, pulsing, show_image, video_id):
        print("Speaking dialog for stage " + str(stage_id.value))

        #Pull new stage
        self.stage = self.script[stage_id.value]
        if 'ignore_answer' in self.stage:
            self.ignore_answer = False if self.stage['ignore_answer'] == 'False' else True

        if 'voice' in self.stage:
            self.speech_engine.voice_name = self.stage['voice']

        if 'video' in self.stage:
            video_id.value = self.videos.index(self.stage['video'])

        if 'dialog' in self.stage:
            #Loop through dialog
            for line in self.stage['dialog']:
                self.update_variables(line, color_id, face_id, pulsing, show_image)

                if 'generate_image' in line:
                    if self.use_redis:
                        self.r.set('generate_image', True)

                        while self.r.get('generate_image'):
                            time.sleep(0.1)

                    else:
                        print("sleeping...")
                        time.sleep(5)


        # Select an archetype at random
        if 'archetypes' in self.stage:

            # Find archetype ID
            archetype_id.value = min(int(7 * self.score/(3*5)), 6)

            print("Score: " + str(self.score))
            print("Archetype ID: " + str(archetype_id.value))

            archetype_dict = self.stage['archetypes'][archetype_id.value]
            archetype.value = True

            self.speech_engine.respond(archetype_dict['name'])
            self.speech_engine.respond(archetype_dict['text'])
            archetype.value = False
        
        # Select a question at random
        if 'questions' in self.stage:
            question_id.value = random.randint(0, len(self.stage['questions'])-1)
            question_dict = self.stage['questions'][question_id.value]
            self.update_variables(question_dict, color_id, face_id, pulsing, show_image)

            # We are now starting a question
            question.value = True

            for a, answer in enumerate(question_dict['answers']):
                if a == 3:
                    self.speech_engine.respond('or')
                answer_id.value = a
                self.speech_engine.respond(answer['text'])

        else:
            # go to next stage, or back to start
            if stage_id.value == self.num_stages-1:
                print("sleeping...")
                time.sleep(30)
                stage_id.value = 0
            else:
                stage_id.value = stage_id.value + 1
                
            self.speak_dialog(color_id, face_id, stage_id, question_id, question, answer_id, answered, archetype_id, archetype, pulsing, show_image, video_id)


    def update_variables(self, dictionary, color_id, face_id, pulsing, show_image, text=True, response=False):
        if 'color' in dictionary:
            color_id.value = self.color_list.index(dictionary['color'])

        if 'show_image' in dictionary:
            show_image.value = False if dictionary['show_image'] == 'False' else True

        if 'face' in dictionary:
            face_id.value = self.faces.index(dictionary['face'])

        if 'pulsing' in dictionary:
            pulsing.value = False if dictionary['pulsing'] == 'False' else True

        if text and ('text' in dictionary):
            self.speech_engine.respond(dictionary['text'])

        if response and ('response' in dictionary):
            self.speech_engine.respond(dictionary['response'])