import cv2
import random
import helpers

class Video:
    def __init__(self):
        self.width = 800
        self.height = 600
        self.window_name = 'face'

        self.colors, self.color_list = helpers.build_colors()
        self.faces = helpers.build_faces()
        self.videos = helpers.build_videos()
        self.script = helpers.build_script()
        self.archetypes = helpers.build_archetypes()

        return

    def put_text(self, frame, text, color, a):
        line1 = ""
        line2 = ""
        line1_length = 0
        two_lines = False
        for word in text.split():
            if ((line1_length + len(word) + 1) <= 30) and (not two_lines):
                line1 = line1 + str(word) + " "
                line1_length = line1_length + len(word) + 1
            else:
                two_lines = True
                line2 = line2 + str(word) + " "

        if line2 == "":
            cv2.putText(img=frame,
                text=line1,
                org=(50, a*150+70),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=1.5,
                color=color,
                thickness=3)
        else:
            cv2.putText(img=frame,
                text=line1,
                org=(50, a*150+70),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=1.5,
                color=color,
                thickness=3)
            
            cv2.putText(img=frame,
                text=line2,
                org=(50, a*150+120),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=1.5,
                color=color,
                thickness=3)
            
        return frame


    def run(self, face_id, stage_id, question_id, question, answer_id, answered, archetype_id, archetype, sensor_flag, show_image, video_id):

        f_id = -1
        s_id = -1
        a_id = -1
        arch_id = -1
        show_image_flag = False
        break_stage = False
        break_esc = False

        while True: # First loop resets every stage
            cap = cv2.VideoCapture('videos/' + self.videos[video_id.value])

            while True: # Second loop resets every time the face changes or answer changes

                while(cap.isOpened()):

                    ret, frame = cap.read() 

                    if ret:

                        # Resize frame
                        frame = cv2.resize(frame, (self.width, self.height))

                        # If no-one is sitting and we're not at the end of the test
                        if (not sensor_flag.value) and (stage_id.value != 11):

                            text = "Please be seated"
                            color = (255,255,255)

                            cv2.putText(img=frame,
                                text=text,
                                org=(125, 300),
                                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                fontScale=2,
                                color=color,
                                thickness=3)
                            
                        # If we are asking a multiple choice question
                        elif question.value and len(self.script[stage_id.value]['questions'][question_id.value]['answers']) > 1:

                            if answered.value:
                                # Add text for all options
                                # color answered option in red
                                for a, answer in enumerate(self.script[stage_id.value]['questions'][question_id.value]['answers']):
                                    text = answer['text']
                                    if a == answer_id.value:
                                        color = (0,0,255)
                                    else:
                                        color = (255,255,255)

                                    frame = self.put_text(frame, text, color, a)

                            else:
                                # Add text up to and including the question the AI is speaking
                                for a in range(answer_id.value+1):
                                    text = self.script[stage_id.value]['questions'][question_id.value]['answers'][a]['text']
                                    color = (255, 255, 255)

                                    frame = self.put_text(frame, text, color, a)
                                    
                        
                        # Load archetype image or face image
                        else:
                            if show_image.value:
                                if archetype.value:
                                    img = cv2.imread('archetypes/' + self.script[stage_id.value]['archetypes'][archetype_id.value]['image'])
                                    size = 600
                                        
                                else:
                                    img = cv2.imread('faces/' + self.faces[face_id.value])
                                    size = 400
                            
                                img = cv2.resize(img, (size, size))
                                img_height, img_width, img_channels = img.shape
                                        
                                # img = cv2.copyMakeBorder(img, 0, 0, 100, 100, cv2.BORDER_CONSTANT)

                                frame_height, frame_width, frame_channels = frame.shape

                                x_offset = int((frame_width - img_width)/2)
                                y_offset = int((frame_height - img_height)/2)

                                y1, y2 = y_offset, y_offset + img_height
                                x1, x2 = x_offset, x_offset + img_width

                                # For archetypes, put image across center of screen
                                if archetype.value:
                                    frame[y1:y2, x1:x2] = img

                                # For faces, make sure image is transparent
                                else:
                                    alpha_s = img[:, :, 2] / 255.0
                                    alpha_l = 1.0 - alpha_s

                                    for c in range(0, 3):
                                        frame[y1:y2, x1:x2, c] = (alpha_s * img[:, :, c] +
                                                                alpha_l * frame[y1:y2, x1:x2, c]) 


                        cv2.imshow('face', frame)
                        cv2.namedWindow("face", cv2.WINDOW_NORMAL)
                        #cv2.setWindowProperty("face",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN) #Disable when on large monitor
                        cv2.resizeWindow("face", self.width, self.height) #Enable when on large monitor

                    else:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        continue

                    # If face has changed, restart video loop
                    if f_id != face_id.value:
                        f_id = face_id.value
                        break

                    # If answer has changed, restart video loop
                    if a_id != answer_id.value:
                        a_id = answer_id.value
                        break

                    # If archetype has changed, restart video loop
                    if arch_id != archetype_id.value:
                        arch_id = archetype_id.value
                        break

                    # If show image flag has changed, restart video loop
                    if show_image_flag != show_image.value:
                        show_image_flag = show_image.value
                        break

                    # If stage has changed, restart stage loop
                    if stage_id.value != s_id:
                        s_id = stage_id.value
                        break_stage = True
                        print("stage changed")
                        break

                    # If esc has been pressed, exit both loops
                    k = cv2.waitKey(10)
                    if k==27:
                        break_esc = True
                        print("shutting down...")
                        break
                
                if break_esc or break_stage:
                    break_stage = False
                    break

            if break_esc:
                break




if __name__ == "__main__":
    my_vid = Video()
    print(my_vid.videos)