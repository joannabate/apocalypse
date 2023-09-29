import multiprocessing as mp
from os import listdir
from os.path import isfile, join
from ctypes import c_bool

from ai import AI
from bulbs import Bulbs
from video import Video

def ai_loop(color_id, face_id, faces, mic_on):
    my_ai = AI(faces)
    my_ai.run(color_id, face_id, mic_on)

def video_loop(face_id, faces, mic_on):
    my_vid = Video(faces)
    my_vid.run(face_id, mic_on)

def bulb_loop(color_id):
    my_bulbs = Bulbs() 
    my_bulbs.run(color_id)

if __name__ == "__main__":
    
    # load faces
    faces = [f for f in listdir('faces') if isfile(join('faces', f))]

    mp.set_start_method('forkserver')
    
    color_id = mp.Value('i', 0)
    face_id = mp.Value('i', 99) #Boot sequence
    mic_on = mp.Value(c_bool, False)
    
    p1 = mp.Process(target=ai_loop, args=(color_id, face_id, faces, mic_on))
    p2 = mp.Process(target=video_loop, args=(face_id, faces, mic_on))
    p3 = mp.Process(target=bulb_loop, args=(color_id, ))
    
    p1.start()
    p2.start()
    p3.start()

    p1.join()
    p2.join()
    p3.join()

