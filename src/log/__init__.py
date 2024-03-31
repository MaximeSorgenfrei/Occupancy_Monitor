from datetime import datetime
import os
import time

class Log():
    def __init__(self,path_to_log_folder):
        self.path_to_log_folder = path_to_log_folder
        self.time_FMT_file = '%Y-%m-%d_%H-%M-%S'
        self.time_FMT_log = '%Y-%m-%d %H:%M:%S (%Z %z)'
        self.time_FMT_event = '%Y-%m-%d %H:%M:%S'
        self.timestamp,self.timestamp_file = self._get_event_time(), time.strftime(self.time_FMT_file)
        self.log_file = f"log_file_{self.timestamp_file}.log"
        
        self.file_handle = open(os.path.join(self.path_to_log_folder,self.log_file),"w")
        self.file_handle.write(f"[{self._get_log_time()}]\tLog file has been created.\n")

    def __exit__(self):
        self.file_handle.write(f"[{self._get_log_time()}]\tLog file has been closed. Service has been running for {self._get_log_runtime()} (hh:mm:ss)")
        self.file_handle.close()

    def _set_path_to_log_folder(self, path):
        if os.path.exists(path) is not True:
            self._create_folder(path)
        self.path_to_log_folder = path

    def _create_folder(self, folder):
        os.mkdir(folder)
        print(f"[{self._get_event_time()}]\tLog folder has been created. ({folder})")

    def _get_event_time(self):
        return time.strftime(self.time_FMT_event)
    
    def _get_log_time(self):
        return time.strftime(self.time_FMT_log)

    def _get_log_runtime(self):
        return datetime.strptime(self._get_event_time(), self.time_FMT_event) - datetime.strptime(self.timestamp, self.time_FMT_event)

    def _write_to_log(self,text : str):
        if type(text) == str:
            self.file_handle.write(f"[{self._get_event_time()}]\t{text}\n")
        else:
            raise TypeError(f"'{text}' must be of type {type(str)} not {type(text)}.")
    
    def log(self, message : str):
        self._write_to_log(message)
    
    def log_event(self, occupation : bool):
        self._write_to_log(f"{self._get_event_text(occupation)}")

    def _get_event_text(self, occupation : bool = False):
        return "Occupation of room has been detected." if occupation else "Non-occupation of room has been detected."
