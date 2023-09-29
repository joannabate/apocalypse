import cv2
from boot_sequence import BootSequence

class Video:
    def __init__(self, faces):
        self.width = 800
        self.height = 600
        self.window_name = 'face'
        self.faces = faces
        return
        
    def show_face(self, f_id, face_id):
        self.img = cv2.imread('faces/' + self.faces[face_id.value])
        self.img = cv2.copyMakeBorder(self.img, 0, 0, 100, 100, cv2.BORDER_CONSTANT)
        f_id = face_id.value
        cv2.imshow('face', self.img)

    def run(self, face_id, mic_on):
        cv2.namedWindow("face", cv2.WINDOW_NORMAL)
        #cv2.setWindowProperty("face",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN) #Disable when on large monitor
        cv2.resizeWindow("face", self.width, self.height) #Enable when on large monitor
        
        f_id = 100
        while True:
            if face_id.value == 99:
                boot_seq = BootSequence(self.width, self.height, self.window_name)
                boot_seq.run(mic_on)
                face_id.value = self.faces.index('happy.png') #switch to happy once finished
                f_id = self.show_face(f_id, face_id)
                
            elif face_id.value != f_id: # emotion has changed
                f_id = self.show_face(f_id, face_id)

            k = cv2.waitKey(10)
            if k==27:    # Esc key to stop
                break