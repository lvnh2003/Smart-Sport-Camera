from PyQt5.QtCore import pyqtSignal, QThread
import numpy as np,cv2


class ThreadCamera(QThread):
    ImageUpdate = pyqtSignal(np.ndarray)
    def __init__(self,model):
        super().__init__(self)
        self.model = model

    global camIndex
    # run camera
    def run(self):
        Capture = cv2.VideoCapture(0)
        Capture.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
        Capture.set(cv2.CAP_PROP_FRAME_WIDTH,640)
        self.ThreadActive = True
        while self.ThreadActive:
            ret,frame_cap = Capture.read()
            if ret:
                results =  self.model(frame_cap, conf=0.5, verbose=False)
                if len(results[0]) > 0:
                    # get attributes of object
                    box = results[0].boxes.xyxy[0]
                    # if object is falling in polygon

                    print("SOS")

                annotated_frame = results[0].plot()
                self.ImageUpdate.emit(annotated_frame)

    def stop(self):
        self.ThreadActive = False
        self.quit()



