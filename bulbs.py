import time
from platypush.context import get_plugin
import helpers
import math

N_BULBS = 6

class Bulbs:
    def __init__(self):
        self.colors, self.color_list = helpers.build_colors()
        self.script = helpers.build_script()

    def update_bulbs(self, color_xy=None, brightness=None):
        # Update bulbs
        for s in range(N_BULBS):
            bulb_name = 'Bulb ' + str(s+1)
            try:
                if color_xy:
                    get_plugin('zigbee.mqtt').device_set(device=bulb_name, property='color', value=color_xy)
                if brightness is not None:
                    get_plugin('zigbee.mqtt').device_set(device=bulb_name, property='brightness', value=brightness)
            except:
                print(bulb_name + ' failed to update')
                continue

    def run(self, color_id, pulsing, sensor_flag):
        c_id = -1
        s_flag = sensor_flag.value
        t_secs = int(time.time())

        while True:
            # If someone is sitting down, do normal light logic
            if sensor_flag.value:
                if color_id.value != c_id or sensor_flag.value != s_flag:
                    color_name = self.color_list[color_id.value]

                    if color_name == "black":
                        self.update_bulbs(brightness=0)
                    else:
                        self.update_bulbs(brightness=254)

                        color_xy = self.colors[color_name]
                        self.update_bulbs(color_xy=color_xy)

                    c_id = color_id.value 
                    s_flag = sensor_flag.value 

                if pulsing.value:
                    # If the time in seconds has changed
                    if t_secs != int(time.time()):
                        # brightness = int(254 * (1 + math.sin(2 * math.pi * (time.time() % 5)/5))/2)
                        if int(time.time()) % 2 == 0:
                            brightness = 254
                        else:
                            brightness = 0
                        t_secs = int(time.time())
                    self.update_bulbs(brightness=brightness)

            # If no-one is sitting down, ignore light logic and set white light
            else:
                if sensor_flag.value != s_flag:
                    self.update_bulbs(brightness=254)
                    color_xy = self.colors['white']
                    self.update_bulbs(color_xy=color_xy)
                    s_flag = sensor_flag.value

            time.sleep(0.2)

if __name__ == '__main__':
    my_bulbs = Bulbs()