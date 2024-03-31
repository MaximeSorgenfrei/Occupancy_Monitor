import numpy as np

class FPS:
    def __init__(self):
        self.fps = []

    def update(self, value):
        self.fps.append(value)

    def get_min(self):
        return np.min(self.fps)
    
    def get_max(self):
        return np.max(self.fps)
    
    def get_mean(self):
        return np.mean(self.fps)
    
    def get_median(self):
        return np.median(self.fps)
    
    def get_statistics_string(self) -> str:
        return f"FPS Statistics:\t\tmin: {self.get_min():.4f}\tmean: {self.get_mean():.4f}\tmedian: {(self.get_median()):.4f}\tmax: {(self.get_max()):.4f}"