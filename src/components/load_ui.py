from PyQt5.QtGui import QImage, QPixmap
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QPushButton, QMainWindow
from PyQt5.QtCore import Qt, pyqtSlot
import numpy as np
import cv2
from src.components.thread_camera import ThreadCamera


class LoadUI(QMainWindow):
    def __init__(self, model):
        super().__init__()
        self.model = model
        # Load UI file
        uic.loadUi('./src/ui/mainwindow.ui', self)

        # Setup ScrollArea
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        # Load cameras from file
        self.load_cameras()
        self.btn_Start.clicked.connect(self.StartWebCam)
        self.btn_Start.setStyleSheet("background-color: red; color: white;")
        # self.btn_stop.clicked.connect(self.StopWebcam)
    def load_cameras(self):
        try:
            # Xóa layout cũ nếu có
            self.clear_layout()

            # Đọc danh sách camera từ file
            with open('./data/camera.txt', 'r') as f:
                camera_urls = f.readlines()

            # Tạo grid layout mới cho scrollAreaWidgetContents
            layout = QGridLayout()
            self.scrollAreaWidgetContents.setLayout(layout)

            # Tính toán số cột dựa trên chiều rộng
            num_columns = 3

            # Tạo camera widgets
            for i, url in enumerate(camera_urls):
                url = url.strip()

                # Tạo camera label
                camera = QLabel()
                camera.setObjectName(f"camera_{i + 1}")
                camera.setStyleSheet("QLabel { border: 1px solid grey; background-color: #f0f0f0; }")
                camera.setFixedSize(300, 181)

                # Tạo nút Start
                btn = QPushButton("Start")
                btn.setObjectName(f"btn_Start_{i + 1}")
                btn.setStyleSheet("background-color: red; border: 1; border-radius: 5")
                btn.setFixedSize(91, 41)

                # Thêm vào layout
                row = i // num_columns
                col = i % num_columns
                layout.addWidget(camera, row * 2, col)
                layout.addWidget(btn, row * 2 + 1, col, Qt.AlignCenter)

            # Thêm nút Add New Camera
            add_camera_btn = QPushButton()
            add_camera_btn.setObjectName("addCameraBtn")
            add_camera_btn.setStyleSheet("""
                   QPushButton {
                       border: 2px dashed grey;
                       background-color: transparent;
                       image: url(src/ui/images/add.png);  /* Thêm icon cho button add camera */
                   }
                   QPushButton:hover {
                       background-color: #f0f0f0;
                   }
               """)
            add_camera_btn.setFixedSize(300, 181)
            add_camera_btn.setCursor(Qt.PointingHandCursor)
            add_camera_btn.clicked.connect(self.open_camera_settings)

            # Tính vị trí cho nút Add New Camera
            next_row = (len(camera_urls)) // num_columns
            next_col = (len(camera_urls)) % num_columns
            layout.addWidget(add_camera_btn, next_row * 2, next_col)

            # Tính toán chiều rộng tối thiểu cho scrollAreaWidgetContents
            total_items = len(camera_urls) + 1  # +1 cho nút Add New Camera
            required_columns = (total_items + num_columns - 1) // num_columns
            min_width = num_columns * (251 + 20)  # 20 là khoảng cách giữa các camera
            self.scrollAreaWidgetContents.setMinimumWidth(min_width)

        except FileNotFoundError:
            print("Không tìm thấy file camera.txt")
        except Exception as e:
            print(f"Lỗi khi đọc file camera: {str(e)}")

    def open_camera_settings(self):
        # Tạo và hiển thị cửa sổ camera settings
        self.camera_settings = QMainWindow()
        uic.loadUi('./src/ui/camera_setting.ui', self.camera_settings)

        # Kết nối nút Close với hàm đóng cửa sổ
        self.camera_settings.close_btn.clicked.connect(self.camera_settings.close)

        # Kết nối nút Update với hàm cập nhật camera
        self.camera_settings.updateBtn.clicked.connect(self.update_camera_list)

        self.camera_settings.show()

    def update_camera_list(self):
        # Lấy IP address từ textEdit
        new_camera_url = self.camera_settings.ipAddress.toPlainText().strip()
        if new_camera_url:
            try:
                # Thêm camera mới vào file
                with open('./data/camera.txt', 'a') as f:
                    f.write(f'\n{new_camera_url}')

                # Cập nhật lại giao diện
                self.clear_layout()
                self.load_cameras()

                # Đóng cửa sổ settings
                self.camera_settings.close()

            except Exception as e:
                print(f"Lỗi khi cập nhật camera: {str(e)}")

    def clear_layout(self):
        if self.scrollAreaWidgetContents.layout() is not None:
            # Xóa tất cả widgets trong layout
            while self.scrollAreaWidgetContents.layout().count():
                item = self.scrollAreaWidgetContents.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            # Xóa layout cũ
            QWidget().setLayout(self.scrollAreaWidgetContents.layout())

    @pyqtSlot(np.ndarray)
    def opencv_emit(self, Image):

        # QPixmap format
        original = self.cvt_cv_qt(Image)

        self.disp_main.setPixmap(original)
        self.disp_main.setScaledContents(True)

    def cvt_cv_qt(self, Image):
        rgb_img = cv2.cvtColor(src=Image, code=cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_img.shape
        bytes_per_line = ch * w
        cvt2QtFormat = QImage(rgb_img.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(cvt2QtFormat)

        return pixmap  # QPixmap.fromImage(cvt2QtFormat)11

    def StartWebCam(self, pin):
        try:
            # self.textEdit.append(
            #     f"{self.DateTime.toString('d MMMM yy hh:mm:ss')}: Start Webcam ({self.camlist.currentText()})")
            # self.btn_stop.setEnabled(True)
            # self.btn_stop.setStyleSheet("background-color: red; color: white;")
            # self.btn_start.setEnabled(False)
            # self.btn_start.setStyleSheet("color: grey; background-color: white")
            #
            # global camIndex
            # camIndex = self.camlist.currentIndex()
            # Opencv QThread
            self.camera_worker = ThreadCamera(self.model)
            self.camera_worker.ImageUpdate.connect(self.opencv_emit)
            self.camera_worker.start()
            print("open")
        except Exception as error:
            print(error)

    def StopWebcam(self):
        self.camera_worker.stop()