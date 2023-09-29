import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="apocalypse-roomservice-6bebad941d3f.json"

from google.cloud import texttospeech
from playsound import playsound
import cv2
import speech_recognition as sr

class Speech:
   def __init__(self):
      self.is_speaking = False
      
   def synthesize_text(self, text):

      self.is_speaking = True

      """Synthesizes speech from the input string of text."""
      client = texttospeech.TextToSpeechClient()

      input_text = texttospeech.SynthesisInput(text=text)

      # Note: the voice can also be specified by name.
      # Names of voices can be retrieved with client.list_voices().
      voice = texttospeech.VoiceSelectionParams(
         language_code="en-US",
         name="en-US-Standard-C",
         ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
      )

      audio_config = texttospeech.AudioConfig(
         audio_encoding=texttospeech.AudioEncoding.MP3
      )

      response = client.synthesize_speech(
         request={"input": input_text, "voice": voice, "audio_config": audio_config}
      )

      # The response's audio_content is binary.
      with open("output.mp3", "wb") as out:
         out.write(response.audio_content)
         print('Audio content written to file "output.mp3"')

      playsound('output.mp3')
   
      self.is_speaking = False

      
   # this is called from the background thread
   def callback(self, recognizer, audio):
      # received audio data, now we'll recognize it using Google Speech Recognition
      try:
         # for testing purposes, we're just using the default API key
         # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
         # instead of `r.recognize_google(audio)`
         text = recognizer.recognize_google(audio)
         print("Google Speech Recognition thinks you said " + text)

         self.synthesize_text(text)

      except sr.UnknownValueError:
         print("Google Speech Recognition could not understand audio")
      except sr.RequestError as e:
         print("Could not request results from Google Speech Recognition service; {0}".format(e))

   def run(self):

      r = sr.Recognizer()

      for index, name in enumerate(sr.Microphone.list_microphone_names()):
         print("Microphone with name \"{1}\" found for `Microphone(device_index={0})`".format(index, name))

      m = sr.Microphone()

      with m as source:
         r.adjust_for_ambient_noise(source)  # we only need to calibrate once, before we start listening

      # start listening in the background (note that we don't have to do this inside a `with` statement)
      stop_listening = r.listen_in_background(m, self.callback)
      # `stop_listening` is now a function that, when called, stops background listening
      
      while True:
         #This is to check whether to break the first loop
         isclosed = False

         if self.is_speaking:
            path = 'speaking.mp4'
            speaking = True
         else:
            path = 'waiting.mp4'
            speaking = False

         cap = cv2.VideoCapture(path)

         while cap.isOpened():

            ret, frame = cap.read()
            # It should only show the frame when the ret is true
            if ret == True:

               cv2.imshow('frame',frame)
               
               if cv2.waitKey(1) == 27:
                  # When esc is pressed isclosed is 1
                  isclosed = True
                  break

               if self.is_speaking != speaking:
                  break
            else:
               print('returning to start of video')
               cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
         # To break the loop if it is closed manually
         if isclosed:
               break

      cap.release()
      cv2.destroyAllWindows()


if __name__ == "__main__":
   my_speech = Speech()
   my_speech.run()