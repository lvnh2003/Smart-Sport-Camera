import cv2
import numpy as np
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer

from src.components.thread_camera import ThreadCameraAdd
from src.components.notify import NotifyMessage


class AddCamera(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(AddCamera, self).__init__(parent)
        # load ui from ui folder
        uic.loadUi("./src/ui/camera_setting.ui", self)
        self.setWindowTitle("Add Camera")
        self.ipAddress.setStyleSheet("background-color:white;color: black")
        self.setStyleSheet("background-color: #DDDDDD;color: black")
        # show video button
        self.parent = parent
        self.checkBtn.clicked.connect(self.checkCameraIsAvailable)
        self.updateBtn.setText("Add")
        self.updateBtn.clicked.connect(self.addCamera)
        self.close_btn.clicked.connect(self.closeWindow)
        self.linkIsTrue = False
        self.link = None
        # tạo ra thread để check được method isRunning()
        self.active_camera_threads = ThreadCameraAdd(0)
        
        # Create timer for 60 FPS
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1000//60)  
        
        self.show()

    # Kiểm tra IP của camera có chuẩn ( tòn tại hay không )
    def checkCameraIsAvailable(self):
        self.link = self.ipAddress.toPlainText()
        if len(self.link) > 255:
            NotifyMessage("Camera IP Address too long", 0)
            print("Camera IP Address of character is too long")
            return
        # change value video_capture
        if self.active_camera_threads.isRunning():
            self.active_camera_threads.stop()
        # Tạo thread mới ở camera mới
        self.active_camera_threads = ThreadCameraAdd(self.link)
        self.active_camera_threads.ImageUpdate.connect(self.opencv_emit)
        self.active_camera_threads.start()

    def update_frame(self):
        # This method will be called every 16.67ms (60 FPS)
        if hasattr(self, 'current_frame'):
            self.camera_preview.setPixmap(self.current_frame)
            self.camera_preview.setScaledContents(True)

    def opencv_emit(self, image):
        self.current_frame = self.cvt_cv_qt(image)

    def cvt_cv_qt(self, image):
        rgb_img = cv2.cvtColor(src=image, code=cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_img.shape
        bytes_per_line = ch * w
        cvt2QtFormat = QImage(rgb_img.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(cvt2QtFormat)
        return pixmap

    def addCamera(self):
        # thêm link mới vào file cameras.txt
        self.link = self.ipAddress.toPlainText()
        if len(self.link) > 255:
            NotifyMessage("Camera IP Address too long",0)
            print("Camera IP Address of character is too long")
            return
        NotifyMessage("Add new camera successfully")
        with open('./data/camera.txt', 'a') as file:
            file.write(self.link + "\n")
        self.parent.camera_handler.camera_urls = self.parent.load_camera_urls()
        self.parent.clear_layout()
        self.parent.load_cameras()
        self.close()

    def closeWindow(self):
        if self.active_camera_threads is not None:
            self.active_camera_threads.stop()
        self.timer.stop()
        self.close()

    def closeEvent(self, event):
        if self.active_camera_threads is not None:
            self.active_camera_threads.stop()
        self.timer.stop()
        event.accept()