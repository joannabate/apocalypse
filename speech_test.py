import pyttsx3
def onStart(name):
   print ('starting', name)
def onWord(name, location, length):
   print ('word', name[location:location+length])
def onEnd(name, completed):
   print ('finishing', name, completed)
engine = pyttsx3.init()
engine.connect('started-utterance', onStart)
engine.connect('started-word', onWord)
engine.connect('finished-utterance', onEnd)
text = 'The quick brown fox jumped over the lazy dog.'
engine.say(text, text)
engine.runAndWait()