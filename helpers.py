from os import listdir
from os.path import isfile, join
import json

def build_colors():

    colors = {}
    colors['blue'] = {'x':0.1, 'y':0.25}
    colors['red'] = {'x':0.7539, 'y':0.2746}
    colors['green'] = {'x':0.0771, 'y':0.8268}
    colors['white'] = {'x':0.3127, 'y':0.329}
    colors['orange'] = {'x':0.55, 'y':0.43}
    colors['yellow'] = {'x':0.44, 'y':0.54}
    colors['pink'] = {'x':0.4, 'y':0.12}
    colors['black'] = None

    color_list = [c for c in colors.keys()]

    return colors, color_list

def build_faces():
    return [f for f in listdir('faces') if isfile(join('faces', f))]

def build_archetypes():
    return [a for a in listdir('archetypes') if isfile(join('archetypes', a))]

def build_videos():
    return [v for v in listdir('videos') if (isfile(join('videos', v)) and v[-4:] == ".mp4")]

def build_script():
    with open('script.json') as json_file:
        return {k:v for k,v in json.load(json_file).items()}['script']