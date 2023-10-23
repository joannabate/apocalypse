import multiprocessing as mp
from os import listdir
from os.path import isfile, join
from ctypes import c_bool

from ai import AI
from bulbs import Bulbs
from video import Video

def ai_loop(color_id, face_id, stage_id, faces, videos):
    my_ai = AI(faces, videos)
    my_ai.run(color_id, face_id, stage_id)

def video_loop(face_id, stage_id, faces, videos):
    my_vid = Video(faces, videos)
    my_vid.run(face_id, stage_id)

def bulb_loop(color_id):
    my_bulbs = Bulbs() 
    my_bulbs.run(color_id)

if __name__ == "__main__":

    mp.set_start_method('forkserver')

    faces = [f for f in listdir('faces') if isfile(join('faces', f))]
    videos = [v for v in listdir('videos') if (isfile(join('videos', v)) and v[-4:] == ".mp4")]
    
    color_id = mp.Value('i', 3) #starts off white
    face_id = mp.Value('i', faces.index('happy.png')) # starts off happy
    stage_id = mp.Value('i', 0)
    
    p1 = mp.Process(target=ai_loop, args=(color_id, face_id, stage_id, faces, videos))
    p2 = mp.Process(target=video_loop, args=(face_id, stage_id, faces, videos))
    p3 = mp.Process(target=bulb_loop, args=(color_id, ))
    
    p1.start()
    p2.start()
    p3.start()

    p1.join()
    p2.join()
    p3.join()
