import multiprocessing as mp
from ctypes import c_bool
import json
from sensors import Sensors
from ai import AI
from bulbs import Bulbs
from video import Video

def ai_loop(color_id,
            face_id,
            stage_id,
            question_id,
            question,
            answer_id,
            answered,
            archetype_id,
            archetype,
            pulsing,
            sensor_flag,
            show_image,
            video_id):
    
    my_ai = AI()

    my_ai.run(color_id,
              face_id,
              stage_id,
              question_id,
              question,
              answer_id,
              answered,
              archetype_id,
              archetype,
              pulsing,
              sensor_flag,
              show_image,
              video_id)


def video_loop(face_id,
               stage_id,
               question_id,
               question,
               answer_id,
               answered,
               archetype_id,
               archetype,
               sensor_flag,
               show_image,
               video_id):
    
    my_vid = Video()
    
    my_vid.run(face_id,
               stage_id,
               question_id,
               question,
               answer_id,
               answered,
               archetype_id,
               archetype,
               sensor_flag,
               show_image,
               video_id)

def bulb_loop(color_id,
              pulsing,
              sensor_flag):
    
    my_bulbs = Bulbs() 
    my_bulbs.run(color_id,
                 pulsing,
                 sensor_flag)
    
def sensors_loop(sensor_flag):
    my_sensors = Sensors()
    my_sensors.run(sensor_flag)

if __name__ == "__main__":

    mp.set_start_method('forkserver')
    
    color_id = mp.Value('i', 0)
    face_id = mp.Value('i', 0)
    stage_id = mp.Value('i', 7)
    question_id  = mp.Value('i', 99)
    question = mp.Value(c_bool, False)
    answer_id  = mp.Value('i', 99)
    answered = mp.Value(c_bool, False)
    archetype_id  = mp.Value('i', 99)
    archetype = mp.Value(c_bool, False)
    pulsing = mp.Value(c_bool, False)
    sensor_flag = mp.Value('b', True)
    show_image = mp.Value('b', True)
    video_id  = mp.Value('i', 0)
    
    p1 = mp.Process(target=ai_loop, args=(color_id,
                                          face_id,
                                          stage_id,
                                          question_id,
                                          question,
                                          answer_id,
                                          answered,
                                          archetype_id,
                                          archetype,
                                          pulsing,
                                          sensor_flag,
                                          show_image,
                                          video_id))
    
    p2 = mp.Process(target=video_loop, args=(face_id,
                                             stage_id,
                                             question_id,
                                             question,
                                             answer_id,
                                             answered,
                                             archetype_id,
                                             archetype,
                                             sensor_flag,
                                             show_image,
                                             video_id))
    
    p3 = mp.Process(target=bulb_loop, args=(color_id,
                                            pulsing,
                                            sensor_flag))
    
    p4 = mp.Process(target=sensors_loop, args=(sensor_flag,))
    
    p1.start()
    p2.start()
    p3.start()
    p4.start()

    p1.join()
    p2.join()
    p3.join()
    p4.join()
