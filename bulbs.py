import time
from platypush.context import get_plugin

N_BULBS = 6

class Bulbs:
    def __init__(self):
        self.colors = self.build_colors()
        
    def build_colors(self):
        colors = {}
        colors[0] = {'x':0.1, 'y':0.25} #blue
        colors[1] = {'x':0.7539, 'y':0.2746} #red
        colors[2] = {'x':0.0771, 'y':0.8268} #green
        return colors

    def update_bulbs(self, color=None, brightness=None):
        # Update bulbs
        for s in range(N_BULBS):
            bulb_name = 'Bulb ' + str(s+1)
            try:
                if color:
                    get_plugin('zigbee.mqtt').device_set(device=bulb_name, property='color', value=color)
                if brightness:
                    get_plugin('zigbee.mqtt').device_set(device=bulb_name, property='brightness', value=brightness)
            except:
                print(bulb_name + ' failed to update')
                continue
            

    def run(self, color_id):
        c_id = -1
        self.update_bulbs(self, brightness=127)

        while True:
            if color_id.value != c_id: # emotion has changed
                color = self.colors[color_id.value]
                self.update_bulbs(color=color)
                c_id = color_id.value 
            time.sleep(0.1)

if __name__ == '__main__':
    my_bulbs = Bulbs()
    # get_plugin('zigbee.mqtt').device_set(device='Bulb 1', property='color', value={'x':0.7539, 'y':0.2746})
    for color_id in range(3):
        color = my_bulbs.colors[color_id]
        my_bulbs.update_bulbs(color=color)
        time.sleep(1)