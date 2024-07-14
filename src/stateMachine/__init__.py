from enum import Enum

class Detection(Enum):
    noDetection = 0
    detecting = 1
    ObjectDetected = 2

class State(Enum):
    noOccupancy = 0
    Occupancy = 1

class Debouncer():
    def __init__(self, default = 10):
        self.__default = default
        self.__value = default
        self.__step = 1

    def _reset(self):
        self.__value = self.__default
    
    def _decrement(self):
        if not self.is_debounced():
         self.__value -= self.__step

    def is_debounced(self):
        return (self.__value <= 0)
    
    def update(self, trigger):
        if trigger:
            self._decrement()
        else:
            self._reset()

    def _get_value(self):
        return self.__value

class Signal():
    def __init__(self, default = False):
        self.__current = default
        self.__last = default

    def get_current(self):
        return self.__current
    
    def get_last(self):
        return self.__last

    def update(self, value):
        self.__last = self.__current
        self.__current = value

    def turned_active(self):
        return ((not self.get_last()) and self.get_current())
    
    def turned_inactive(self):
        return (self.get_last() and (not self.get_current()))

class Monitor():
    def __init__(self, frames_to_arm):
        self.__state = State(State.noOccupancy)
        self.__detection = Detection(Detection.noDetection)
        self._debouncer = Debouncer(frames_to_arm)
        self._fallback_debouncer = Debouncer(frames_to_arm)
        self._objects_detected = Signal()

    def _update_detected_objects(self, trigger):
        self._objects_detected.update(trigger)
    
    def _update_debouncer(self, trigger):
        self._debouncer.update(trigger)
        self._fallback_debouncer.update(not trigger)

    def _object_detection_debounced(self):
        return (self.is_detection_set_to(Detection.detecting) and self._debouncer.is_debounced())
    
    def _object_detection_debounced_inactive(self):
        return (self.is_detection_set_to(Detection.noDetection) and self._fallback_debouncer.is_debounced())

    def _obj_detection_turned_active(self):
        return self._objects_detected.turned_active()
        
    def _obj_detection_turned_inactive(self):
        return self._objects_detected.turned_inactive()
        
    def update(self, trigger = False):
        self._update_detected_objects(trigger)
        self._update_debouncer(trigger)

        if self._obj_detection_turned_inactive():
            self._set_detection(Detection.noDetection)

        elif self._obj_detection_turned_active():
            self._set_detection(Detection.detecting)

        elif self._object_detection_debounced():
            self._set_detection(Detection.ObjectDetected)
            self._set_state(State.Occupancy)
        
        elif self._object_detection_debounced_inactive():
            self._set_state(State.noOccupancy)
        
        else:
            # do not set state(s)
            pass
        
        # print(f"trigger: {trigger}\tDebounced: {self._debouncer.is_debounced()}\tobj_det: {self.get_detection()}\tstate: {self.get_state()}")
        return self.get_state()
    
    def get_state(self):
        return self.__state

    def _set_state(self, state : State):
        self.__state = state

    def get_detection(self):
        return self.__detection
    
    def is_detection_set_to(self, value : Detection):
        return (value == self.get_detection())
    
    def _set_detection(self, detection : Detection):
        self.__detection = detection