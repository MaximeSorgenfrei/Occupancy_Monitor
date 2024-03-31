import cv2
import json
import numpy as np
import os
import time

# helper methods
from src.email import EMailService
from src.texttype import TextType
from src.log import Log
from src.fps import FPS

class OccupancyMonitor():

    def __init__(self, show_user_settings=False, diagnostics=False):
        # setting for putting text on image
        text_fontFace, text_fontScale, text_thickness, text_lineType = cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, 2, 1
        infotext_color, alarmtext_color, amber_color = (0,255,0), (0,0,255), (0,140,250)
        self.TEXT_info_text = TextType((50,50), text_fontFace, text_fontScale, infotext_color, text_thickness, text_lineType)
        self.TEXT_fps_text = TextType((400,50), text_fontFace, text_fontScale, infotext_color, text_thickness, text_lineType)
        self.TEXT_occupied_text = TextType((300,440), text_fontFace, text_fontScale, alarmtext_color, text_thickness, text_lineType)
        self.TEXT_not_occupied_text = TextType((300,440), text_fontFace, text_fontScale, infotext_color, text_thickness, text_lineType)
        self.TEXT_status_text = TextType((50,440), text_fontFace, text_fontScale, amber_color, text_thickness, text_lineType)

        # compute vision settings
        self.CV_GaussianBlurKernel = (1,1)
        self.CV_DilationKernel = np.ones((10,10), np.uint8)

        # tracking status
        self.FLAG_room_occupied = None
        self.FLAG_room_status = None
        self.FLAG_message_send = [None,None]
        self.SETTING_FRAMES_TO_ARM = None
        self.SETTING_USER_CONFIG_FILE = "./user_config.json"
        self.SETTING_ARCHIVE_FOLDER = "./archive"
        self.SETTING_LOG_FOLDER = "./logs"
        self.SETTING_TIME_FMT = '%Y-%m-%d %H:%M:%S'
        self.__version__ = 1.0

        # load user settings
        self.load_user_config()
        if self.USER_SETTING_ACTIVATE_LOG:
            self.SERVICE_LogFile = Log(self.SETTING_LOG_FOLDER)
            self.print_message(f"[{time.strftime(self.SETTING_TIME_FMT)}]\tLogging enabled.")
        else:
            print(f"[{time.strftime(self.SETTING_TIME_FMT)}]\tLogging has been disabled. Refer to the config file ({self.SETTING_USER_CONFIG_FILE}) to change this setting. ")
        if self.USER_SETTING_ACTIVATE_EMAIL_NOTIFICATIONS:
            self.SERVICE_Email = EMailService(self.USER_SETTING_EMAIL_fromaddr, self.USER_SETTING_EMAIL_toaddr, self.USER_SETTING_EMAIL_SERVER, self.USER_SETTING_EMAIL_SERVER_PORT, self.USER_SETTING_EMAIL_PASSWORD)
            self.print_message(f"[{time.strftime(self.SETTING_TIME_FMT)}]\tEmail notifications enabled.")
        else:
            self.print_message(f"[{time.strftime(self.SETTING_TIME_FMT)}]\tEmail notifications disabled by user.")

        # check if folder for image saving already exists
        if os.path.exists(self.SETTING_ARCHIVE_FOLDER) is not True:
            os.mkdir(self.SETTING_ARCHIVE_FOLDER)
            if self.USER_SETTING_ACTIVATE_LOG:
                self.print_message(f"[{time.strftime(self.SETTING_TIME_FMT)}]\tArchive folder has been created. ({self.SETTING_ARCHIVE_FOLDER})")

        self.fps = FPS()

        if show_user_settings: self.show_user_settings()
        if diagnostics: self.run_diagnostics()

    def load_user_config(self):
        with open(self.SETTING_USER_CONFIG_FILE, 'r') as f:
            config = json.load(f)
        f.close()

        #save date to self
        self.USER_SETTING_EMAIL_fromaddr = config["SETTING_fromaddr"]
        self.USER_SETTING_EMAIL_toaddr = config["SETTING_toaddr"]
        self.USER_SETTING_EMAIL_PASSWORD = config["SETTING_EMAIL_PASSWORD"]
        self.USER_SETTING_EMAIL_SERVER = config["SETTING_SERVER"]
        self.USER_SETTING_EMAIL_SERVER_PORT = config["SETTING_SERVER_PORT"]
        self.USER_SETTING_SECONDS_TO_ARM = config["SETTING_SECONDS_TO_ARM"]
        self.USER_SETTING_ACTIVATE_EMAIL_NOTIFICATIONS = config["SETTING_ACTIVATE_EMAIL_NOTIFICATIONS"]
        self.USER_SETTING_SAVE_IMAGES = config["SETTING_SAVE_IMAGES"]
        self.USER_SETTING_ACTIVATE_DEBUG = config["SETTING_DEBUG"]
        self.USER_SETTING_ACTIVATE_LOG = config["SETTING_LOG"]
        self.USER_SETTING_SCREEN_RESOLUTION = config["SETTING_SCREEN_RESOLUTION"]
        self.USER_SETTING_FLIP_SCREEN = config["SETTING_FLIP_SCREEN"]
        self.USER_SETTING_REDUCED_COMPUTATIONAL_COMPLEXITY = config["SETTING_REDUCED_COMPUTATIONAL_COMPLEXITY"]
        
        del config

    def show_user_settings(self):
        self.print_message("Following user specified settings are used:\n")
        for item in dir(self):
            if item.startswith("USER_SETTING"): self.print_message(f"{item}:\t\t{self.__getattribute__(item)}")

    def run_diagnostics(self):
        self.print_message("Running diagnostics:\n-----")
        self.print_message(f"Correct cv2 version installed?\t\t{cv2.__version__=='4.1.0'}")
        self.print_message(f"Correct numpy version installed?\t{np.__version__=='1.16.3'}")
        self.print_message(f"-----\nCurrent version of OccupancyMonitor\t{self.__version__}")

    def print_message(self, message):
        if self.USER_SETTING_ACTIVATE_LOG:
            self.SERVICE_LogFile.log(message)
        print(message)

    def send_message(self, image, occupation=False):
        filepath = self.save_image_to_archive(image, occupation)
        if self.USER_SETTING_ACTIVATE_EMAIL_NOTIFICATIONS:
            self.SERVICE_Email.send_email("Room is occupied", filename=filepath)
            timestr = time.strftime('%Y-%m-%d %H:%M:%S\t(%Z %z)')
            self.print_message(f"[{timestr}] Occupancy Status email sent. (Occupancy: {occupation})")
        else:
            timestr = time.strftime('%Y-%m-%d %H:%M:%S')
            self.print_message(f"[{timestr}] Occupancy Status Notification. (Occupancy: {occupation})")
        
        # delete image if saveguarding not allowed.
        if self.USER_SETTING_SAVE_IMAGES == False:
            try:
                os.remove(filepath)
            except Exception as e:
                print(e)
        return ([False,True] if occupation==True else [True,False])
    
    def findBoxfromContours(self, image, contours):
        boxes = None
        if contours is not None and len(contours) > 0:
            # print("{} objects found!".format(len(contours)))
            for contour in contours:
                # conv_hull = cv2.convexHull(contour, clockwise=True, returnPoints=True)
                # cv2.drawContours(image, conv_hull, -1, (255,255,0), 2)
                rect = cv2.minAreaRect(contour)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                if boxes is None:
                    boxes = [box]
                else:
                    boxes.append(box)
                image = cv2.drawContours(image,[box],0,(0,0,255),2)
        return image,boxes

    def convert_image_to_grey(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # if self.USER_SETTING_REDUCED_COMPUTATIONAL_COMPLEXITY:
        #     img = self.normalize_image(img)
        return img

    def print_to_image(self, image,text,font_type):
        assert len(image.shape) == 3, "Image must be three dimensional"
        assert text is not None, "Text must be provided"
        cv2.putText(image,text, font_type.org, font_type.fontFace, font_type.fontScale, font_type.color, font_type.thickness, font_type.lineType)

    def save_image_to_archive(self, image, occupation):
        occ_bool = "occ" if occupation else "nonocc"
        filename = os.path.join(f"{self.SETTING_ARCHIVE_FOLDER}/img_{time.strftime('%Y-%m-%d_%H-%M-%S')}_{occ_bool}.jpg")
        cv2.imwrite(filename, image)
        return filename

    def process(self, cap):
        _, frame = cap.read()
        _, frame2 = cap.read()
        if self.USER_SETTING_FLIP_SCREEN:
            frame, frame2 = cv2.rotate(frame, cv2.ROTATE_180), cv2.rotate(frame2, cv2.ROTATE_180)
        return self.process_frames(frame, frame2)

    def process_frames(self, frame, frame2):
        # convert to grey
        frame_gray = cv2.GaussianBlur(self.convert_image_to_grey(frame), self.CV_GaussianBlurKernel, 0,0,)
        frame2_gray = cv2.GaussianBlur(self.convert_image_to_grey(frame2), self.CV_GaussianBlurKernel, 0,0,)
        # calculate abs difference between frame
        abs_difference_between_frames = cv2.absdiff(frame2_gray, frame_gray)
        # apply treshold on abs difference
        _,treshold_on_abs_diff = cv2.threshold(abs_difference_between_frames, 50, 255, cv2.THRESH_BINARY)
        # dilate tresholded and dilated difference of the two frames
        dilated_frame = cv2.dilate(treshold_on_abs_diff, self.CV_DilationKernel, iterations=5)
        # get contours of dilated frame
        contours, _ = cv2.findContours(dilated_frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        frame,boxes = self.findBoxfromContours(frame, contours)
        # cv2.drawContours(frame, contours, -1, (0,255,0), 2)
        faces = self.detect_faces(frame)
        if boxes is not None and faces is None:
            all_contours = boxes
        elif faces is not None and boxes is None:
            all_contours = faces
        elif faces is not None and boxes is not None:
            all_contours = [faces, boxes]
        else:
            all_contours = []
        # all_contours = boxes if boxes is not None else None
        self.print_to_image(frame, f"{len(all_contours) if all_contours is not None else False} objects found.", self.TEXT_info_text)
        if self.USER_SETTING_ACTIVATE_DEBUG:
            self.print_message(f"faces: {len(faces) if faces is not None else False} {type(faces)})\t\tboxes: {len(boxes) if boxes is not None else False} ({type(boxes)})\t\tall_contours: {len(all_contours) if all_contours is not None else False} ({type(all_contours)})")
        return frame, all_contours

    def detect_faces(self, image):
        face_cascade =  cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        faces = face_cascade.detectMultiScale(image, 1.3, 5)
        if len(faces) > 0:
            for (x,y,w,h) in faces:
                cv2.rectangle(image, (x, y), (x+w, y+h), (255,0,0), 2)
            return list(faces)
        else:
            return None

    def normalize_image(self, image):
        image = image/255.0
        return image

    def startup(self):
        scaling_factor = 2 if self.USER_SETTING_REDUCED_COMPUTATIONAL_COMPLEXITY == True else 1

        # webcam
        cap = cv2.VideoCapture(0)
        cap.set(3,(self.USER_SETTING_SCREEN_RESOLUTION["y"]//scaling_factor))
        cap.set(4,(self.USER_SETTING_SCREEN_RESOLUTION["x"]//scaling_factor))
        self.print_message(f"Starting occupancy observation...\nVideo resolution is {int(cap.get(3))} x {int(cap.get(4))} pixels.")
        return cap

    def run(self, show_video_source=False):
        cap = self.startup()

        start_time = time.time()
        # _,test_frame = cap.read()
        try:
            while cap.isOpened():
                for msg_id in range(len(self.FLAG_message_send)):
                    if self.FLAG_message_send[msg_id] == None: self.FLAG_message_send[msg_id] = False
                if self.SETTING_FRAMES_TO_ARM == None:
                    self.SETTING_FRAMES_TO_ARM = 10
                # elif SETTING_FRAMES_TO_ARM < 0:
                #     # frames = fps / s 
                #     SETTING_FRAMES_TO_ARM = (1/end_time) // USER_SETTING_SECONDS_TO_ARM
                #     print_message(f"Auto adjust setting frames to arm to: {SETTING_FRAMES_TO_ARM}")

                # process frames
                frame, contours = self.process(cap)

                # init and then check room status update...
                if len(contours) > 0:
                    if self.FLAG_room_status == None:
                        self.FLAG_room_status = 0
                    else:
                        self.FLAG_room_status += 1
                        text = "." * self.FLAG_room_status if self.FLAG_room_status > 0 else "."
                        self.print_to_image(frame, f"Checking{text}", self.TEXT_status_text)
                elif len(contours) == 0:
                    if self.FLAG_room_status == None:
                        self.FLAG_room_status = 0
                    else:
                        self.FLAG_room_status -= 1
                else:
                    raise ValueError(f"updating room status is {self.FLAG_room_status}")

                if self.FLAG_room_status > self.USER_SETTING_SECONDS_TO_ARM:
                    self.FLAG_room_occupied = True
                    self.FLAG_room_status = None
                elif self.FLAG_room_status < -self.SETTING_FRAMES_TO_ARM:
                    self.FLAG_room_occupied = False
                    self.FLAG_room_status = None
                else:
                    pass #raise ValueError(f"{len(contours)} is smaller than zero.")

                if self.USER_SETTING_ACTIVATE_DEBUG:
                    self.print_message(f"l_c: {len(contours)}\tr_o: {self.FLAG_room_occupied}\tu_r_s: {self.FLAG_room_status}\tm_s0: {self.FLAG_message_send[0]}\tm_s1: {self.FLAG_message_send[1]}\tS_F_T_A: {self.SETTING_FRAMES_TO_ARM}")
                
                # ... and occupation
                if self.FLAG_room_occupied == None:
                    self.FLAG_room_occupied = False
                elif self.FLAG_room_occupied == True:
                    if self.FLAG_message_send[1] == False:
                        self.FLAG_message_send = self.send_message(frame, occupation=True)
                        if self.USER_SETTING_ACTIVATE_LOG:
                            self.SERVICE_LogFile.log_event(occupation=True)
                    self.print_to_image(frame, "Room occupied!", self.TEXT_occupied_text)
                else:
                    if self.FLAG_message_send[0] == False:
                        self.FLAG_message_send = self.send_message(frame, occupation=False)
                        if self.USER_SETTING_ACTIVATE_LOG:
                            self.SERVICE_LogFile.log_event(occupation=False)
                    self.print_to_image(frame, "Room not occupied!", self.TEXT_not_occupied_text)
                
                end_time = time.time() - start_time
                self.fps.update(1/end_time)
                start_time = time.time()
                self.print_to_image(frame, f"fps: {1/end_time:.2f} ({self.fps.get_mean():.2f})", self.TEXT_fps_text)

                # show results
                if show_video_source:
                    cv2.namedWindow("source", cv2.WINDOW_AUTOSIZE)
                    cv2.imshow("source", frame)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    raise KeyboardInterrupt
        except (KeyboardInterrupt):
                pass
        finally:
            self.shutdown(cap, show_video_source)

    def shutdown(self, cap, show_video_source):
        if show_video_source:
            cv2.destroyAllWindows()
            cap.release()
            self.print_message("All windows have been destroyed and the webcam connection has been terminated.")
        
        # end all services
        self.print_message(self.fps.get_statistics_string())

        if self.USER_SETTING_ACTIVATE_LOG:
            self.SERVICE_LogFile.__exit__()
        if self.USER_SETTING_ACTIVATE_EMAIL_NOTIFICATIONS:
            self.SERVICE_Email.__exit__()

    # end of method