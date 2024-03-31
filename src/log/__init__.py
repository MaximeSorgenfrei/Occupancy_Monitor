from datetime import datetime
import os
import time

class Log():
    def __init__(self,path_to_log_folder):
        self.path_to_log_folder = path_to_log_folder
        self.time_FMT_file = '%Y-%m-%d_%H-%M-%S'
        self.time_FMT_log = '%Y-%m-%d %H:%M:%S (%Z %z)'
        self.time_FMT_event = '%Y-%m-%d %H:%M:%S'
        self.timestamp,self.timestamp_file = time.strftime(self.time_FMT_event), time.strftime(self.time_FMT_file)
        self.log_file = f"log_file_{self.timestamp_file}.log"
        if os.path.exists(self.path_to_log_folder) is not True:
            os.mkdir(self.path_to_log_folder)
            print(f"[{time.strftime(self.time_FMT_event)}]\tLog folder has been created. ({self.path_to_log_folder})")
        
        self.file_handle = open(os.path.join(self.path_to_log_folder,self.log_file),"w")
        self.file_handle.write(f"[{time.strftime(self.time_FMT_log)}]\tLog file has been created.\n")

    def write_to_log(self,text):
        if type(text) == str:
            self.file_handle.write(f"{text}\n")
        else:
            raise TypeError(f"'{text}' must be of type {type(str)} not {type(text)}.")

    def log_event(self,occupation):
        if occupation:
            self.write_to_log(f"[{time.strftime(self.time_FMT_event)}]\tOccupation of room has been detected.")
        else:
            self.write_to_log(f"[{time.strftime(self.time_FMT_event)}]\tNon-occupation of room has been detected.")

    def __exit__(self):
        tdelta = datetime.strptime(time.strftime(self.time_FMT_event), self.time_FMT_event) - datetime.strptime(self.timestamp, self.time_FMT_event)
        self.write_to_log(f"[{time.strftime(self.time_FMT_log)}]\tLog file has been closed. Service has been running for {tdelta} (hh:mm:ss)")
        self.file_handle.close()
