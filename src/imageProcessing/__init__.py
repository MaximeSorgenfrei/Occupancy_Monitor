import cv2
import numpy as np

def _normalize_image(image):
        return image/255.0

def _convert_image_to_grey(img, reduce_complexity = False):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if reduce_complexity:
        img = _normalize_image(img)
    return img

class ImageProcessing():
    def __init__(self):
        # compute vision settings
        self.CV_GaussianBlurKernel = (1,1)
        self.CV_DilationKernel = np.ones((10,10), np.uint8)
        self.CV_DilationIterations = 5
        self.face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        
        # colors
        self._color_blue = (255,0,0)
        self._color_red = (0,0,255)

        self._line_thickness = 2
    
    def _findBoxFromContour(self, contour):
        # conv_hull = cv2.convexHull(contour, clockwise=True, returnPoints=True)
        # cv2.drawContours(image, conv_hull, -1, (255,255,0), 2)
        rect = cv2.minAreaRect(contour)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        return box
    
    def _findBoxesfromContours(self, image, contours = []):
        boxes = []
        for contour in contours:
            box = self._findBoxFromContour(contour)
            boxes.append(box)
        return image,boxes
    
    def _process_frame(self, frame):
        return cv2.GaussianBlur(_convert_image_to_grey(frame), self.CV_GaussianBlurKernel, 0,0)
    
    def _process_frames_for_movement_detection(self, frame, frame2):
        # calculate abs difference between frame
        processed_frame = cv2.absdiff(self._process_frame(frame2), self._process_frame(frame))
        # apply treshold on abs difference
        _,processed_frame = cv2.threshold(processed_frame, 50, 255, cv2.THRESH_BINARY)
        # dilate tresholded and dilated difference of the two frames
        return cv2.dilate(processed_frame, self.CV_DilationKernel, iterations=self.CV_DilationIterations)
    
    def _detect_movement(self, frame, frame2):
        processed_frame = self._process_frames_for_movement_detection(frame, frame2)
        contours, _ = cv2.findContours(processed_frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        frame,boxes = self._findBoxesfromContours(frame, contours)        

        return boxes

    def _print_boxes_to_frame(self, frame, boxes):
        for box in boxes:
            frame = cv2.drawContours(frame, [box], 0, self._color_red, self._line_thickness)
        return frame

    def _detect_faces(self, image):
        faces = self.face_cascade.detectMultiScale(image, 1.3, 5)
        if len(faces) > 0:
            return list(faces)
        else:
            return []
    
    def _print_detected_faces_to_frame(self, frame, faces):
        if len(faces) == 0: return frame
        
        for face in faces:
            self._print_rectangle_to_frame(frame, face)
        return frame
    
    def _print_rectangle_to_frame(self, frame, rectangle = (0,0,0,0)):
        (pos_x, pos_y, width, height) = rectangle
        cv2.rectangle(frame, (pos_x, pos_y), (pos_x+width, pos_y+height), self._color_blue, self._line_thickness)
        return frame

    def _calculate_detected_objects(self, boxes, faces):
        return boxes + faces

    def process(self, frame, frame2):
        boxes = self._detect_movement(frame, frame2)
        frame = self._print_boxes_to_frame(frame, boxes)

        faces = self._detect_faces(frame)
        frame = self._print_detected_faces_to_frame(frame, faces)
        
        detected_objects = self._calculate_detected_objects(boxes, faces)
        
        # print(f"Objects found: {len(detected_objects)}\tObjects: {detected_objects}")
        return frame, detected_objects