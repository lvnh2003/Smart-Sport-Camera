from PyQt5.QtGui import QImage, QPixmap
import cv2
from PyQt5.QtWidgets import QPushButton, QLabel
from src.components.thread_camera import ThreadCamera

class CameraHandler:

    def __init__(self, model, camera_urls, find_start_button, find_camera_view, main_camera):
        self.model = model
        self.camera_urls = camera_urls
        self.find_start_button = find_start_button
        self.find_camera_view = find_camera_view
        self.active_camera_threads = [None] * len(camera_urls)
        self.main_camera = main_camera

    def opencv_emit(self, image, camera_index):
        """Phát hình ảnh từ camera và hiển thị trên UI."""
        # Tìm QLabel để hiển thị hình ảnh camera
        camera_view = self.find_camera_view(camera_index)
        original = self.cvt_cv_qt(image)
        camera_view.setPixmap(original)
        camera_view.setScaledContents(True)

    def cvt_cv_qt(self, image):
        """Chuyển đổi ảnh OpenCV (BGR) thành QPixmap để hiển thị trên UI."""
        # Chuyển đổi màu sắc từ BGR (OpenCV) sang RGB (PyQt)
        rgb_img = cv2.cvtColor(src=image, code=cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_img.shape
        bytes_per_line = ch * w
        cvt2QtFormat = QImage(rgb_img.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(cvt2QtFormat)
        return pixmap

    def toggle_camera_stream(self, camera_index):
        """Bật/tắt camera stream dựa trên trạng thái hiện tại."""
        # Sửa lỗi khi add thêm camera mới bị sai index
        if camera_index >= len(self.active_camera_threads):
            self.active_camera_threads.extend([None] * (camera_index - len(self.active_camera_threads) + 1))
        
        btn = self.find_start_button(camera_index)
        if self.active_camera_threads[camera_index] is None:
            btn.setText("Stop")
            self.active_camera_threads[camera_index] = ThreadCamera(self.model, self.camera_urls[camera_index])
            self.active_camera_threads[camera_index].ImageUpdate.connect(lambda image, x=camera_index: self.opencv_emit(image, x))
            self.active_camera_threads[camera_index].ImageDisplayMain.connect(lambda image, x=camera_index: self.opencv_emit_main_camera(image))
            self.active_camera_threads[camera_index].start()
        else:
            self.active_camera_threads[camera_index].stop()
            self.active_camera_threads[camera_index] = None
            btn.setText("Start")

    def opencv_emit_main_camera(self,image):
        """Phát hình ảnh từ camera chính và hiển thị trên UI."""
        original = self.cvt_cv_qt(image)
        self.main_camera.setPixmap(original)
        self.main_camera.setScaledContents(True)

