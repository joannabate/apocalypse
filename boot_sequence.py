import cv2
import numpy as np
import time

class BootSequence:
    def __init__(self, width=800, height=600, window_name='face'):
        self.width = width
        self.height = height
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 1
        self.thickness = 1
        self.background_color = (0,0,0)
        
        self.booting_script = [{'text':'Booting FUCKBOT', 'loops':1, 'dots':1, 'end_word':None},
                               {'text':'Loading friendliness', 'loops':4, 'dots':4, 'end_word':'DONE'},
                               {'text':'Loading kindness', 'loops':4, 'dots':4, 'end_word':'DONE'},
                               {'text':'Loading sexual experience', 'loops':4, 'dots':4, 'end_word':'FAILED'}]

    def create_blank(self):
        # Create black blank image
        image = np.zeros((self.height, self.width, 3), np.uint8)

        # Since OpenCV uses BGR, convert the colors before using
        rgb_color = tuple(reversed(self.background_color))

        # Fill image with color
        image[:] = rgb_color

        return image

    def flashing_text(self, image, text, bottom_left=(50,100), font_color=(0,0,255), flashes=4):
        for _ in range(flashes):
            img = image.copy() #Copy image to temporary variable
            cv2.putText(img, text, bottom_left, self.font, self.font_scale, font_color, self.thickness)
            cv2.imshow('face', img)
            if self.esc_key(200): return img
            cv2.imshow('face', image)
            if self.esc_key(200): return img
        return img


    def looping_text(self, image, text, bottom_left=(50,100), font_color=(0,255,0), loops=4, dots=4, end_word=None):
        for _ in range(loops):
            txt = text[:] #Copy text to temporary variable
            img = image.copy() #Copy image to temporary variable
            for __ in range(dots):
                cv2.putText(img, txt, bottom_left, self.font, self.font_scale, font_color, self.thickness)
                cv2.imshow('face', img)
                txt = txt + '.'
                if self.esc_key(200): return img, txt
        if end_word:
            txt = txt + end_word
            cv2.putText(img, txt, bottom_left, self.font, self.font_scale, font_color, self.thickness)
            cv2.imshow('face', img)
            if self.esc_key(200): return img, txt

        return img, txt

    def calc_bottom_left(self, line_id=0):
        return (50,50*(line_id+2))

    def esc_key(self, ms):
        k = cv2.waitKey(ms)
        if k==27:    # Esc key to stop
            return True
        return False

    def run(self, mic_on):
        mic_on.value = False
        images = []
        image = self.create_blank()
        images.append(image)
        cv2.imshow('face',image)
        i = 0

        for line in self.booting_script:
            image, text = self.looping_text(image,
                                 line['text'],
                                 bottom_left=self.calc_bottom_left(i),
                                 loops=line['loops'],
                                 dots=line['dots'],
                                 end_word=line['end_word'])
            images.append(image)
            i = i+1
            if self.esc_key(200): break

        #Send the last text with the last but one image to be flashed onscreen
        image = self.flashing_text(images[-2], text, bottom_left=self.calc_bottom_left(i-1))

        #Last image before ending
        image, text = self.looping_text(image,
                             'Starting up...',
                             bottom_left=self.calc_bottom_left(i),
                             loops=1,
                             dots=1)
        mic_on.value = True

if __name__ == "__main__":
    cv2.namedWindow("face", cv2.WINDOW_NORMAL)
    #cv2.setWindowProperty("face",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN) #Enable when on large monitor
    cv2.resizeWindow("face", 800, 600) #Enable when on large monitor

    boot_seq = BootSequence()
    boot_seq.run()

    cv2.destroyAllWindows()