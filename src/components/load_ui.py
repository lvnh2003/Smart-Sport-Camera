from PyQt5.QtGui import QImage, QPixmap
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QPushButton, QMainWindow, QMessageBox
from PyQt5.QtCore import Qt
from src.preprocessing.camera_handle import CameraHandler

class LoadUI(QMainWindow):

    def __init__(self, model):
        super().__init__()
        self.model = model
        uic.loadUi('./src/ui/mainwindow.ui', self)
        self.camera_handler = CameraHandler(self.model, self.load_camera_urls(),self.find_start_button, self.find_camera_view, self.main_camera)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.load_cameras()

    def load_camera_urls(self):
        """Load các đường link của các cameras được lưu trong file"""
        try:
            with open('./data/camera.txt', 'r') as f:
                return [url.strip() for url in f.readlines()]
        except FileNotFoundError:
            print("Không tìm thấy file camera.txt")
            return []

    def load_cameras(self):
        """Load UI và cài đặt cài đặt các hàm cho các element"""
        try:
            # Xóa layout cũ nếu có
            self.clear_layout()

            # Tạo grid layout mới cho scrollAreaWidgetContents
            layout = QGridLayout()
            self.scrollAreaWidgetContents.setLayout(layout)

            # Tính toán số cột dựa trên chiều rộng
            num_columns = 3
            # Tạo camera widgets
            for i, url in enumerate(self.camera_handler.camera_urls):
                # Tạo widget container cho mỗi camera
                container = QWidget()
                container_layout = QGridLayout()
                container.setLayout(container_layout)
                container_layout.setContentsMargins(0, 0, 0, 0)  # Loại bỏ margin

                # Camera container với position relative
                camera_container = QWidget()
                camera_container.setStyleSheet("QWidget { position: relative; }")
                camera_container_layout = QGridLayout()
                camera_container.setLayout(camera_container_layout)
                camera_container_layout.setContentsMargins(0, 0, 0, 0)

                # Camera label
                camera = QLabel()
                camera.setObjectName(f"camera_{i + 1}")
                camera.setStyleSheet("QLabel { border: 1px solid grey; background-color: #f0f0f0; }")
                camera.setFixedSize(300, 181)
                camera_container_layout.addWidget(camera, 0, 0)

                # Close button (dấu x)
                close_btn = QPushButton("×")
                close_btn.setObjectName(f"btn_Close_{i + 1}")
                close_btn.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(255, 255, 255, 0.8);
                        border: none;
                        border-radius: 10px;
                        color: #666;
                        font-size: 16px;
                        font-weight: bold;
                        width: 20px;
                        height: 20px;
                    }
                    QPushButton:hover {
                        background-color: #ff4444;
                        color: white;
                    }
                """)
                close_btn.setFixedSize(20, 20)
                close_btn.setCursor(Qt.PointingHandCursor)
                close_btn.clicked.connect(lambda _, url_camera=url: self.delete_camera(url_camera))
                
                # Thêm close button vào góc trên phải
                camera_container_layout.addWidget(close_btn, 0, 0, Qt.AlignTop | Qt.AlignRight)
                container_layout.addWidget(camera_container, 0, 0)

                # Start button
                btn = QPushButton("Start")
                btn.setObjectName(f"btn_Start_{i + 1}")
                btn.setStyleSheet("background-color: red; border: 1; border-radius: 5")
                btn.setFixedSize(91, 41)
                btn.clicked.connect(lambda _, idx=i: self.camera_handler.toggle_camera_stream(idx))
                container_layout.addWidget(btn, 1, 0, Qt.AlignCenter)

                # Thêm container vào layout chính
                row = i // num_columns
                col = i % num_columns
                layout.addWidget(container, row * 2, col)

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
            next_row = (len(self.camera_handler.camera_urls)) // num_columns
            next_col = (len(self.camera_handler.camera_urls)) % num_columns
            layout.addWidget(add_camera_btn, next_row * 2, next_col)

            # Tính toán chiều rộng tối thiểu cho scrollAreaWidgetContents
            total_items = len(self.camera_handler.camera_urls) + 1  # +1 cho nút Add New Camera
            required_columns = (total_items + num_columns - 1) // num_columns
            min_width = num_columns * (251 + 20)  # 20 là khoảng cách giữa các camera
            self.scrollAreaWidgetContents.setMinimumWidth(min_width)

        except FileNotFoundError:
            print("Không tìm thấy file camera.txt")
        except Exception as e:

            print(f"Lỗi khi đọc file camera: {e}")

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
                # Đọc tất cả các URL hiện tại
                with open('./data/camera.txt', 'r') as f:
                    urls = [line.strip() for line in f.readlines() if line.strip()]  # Bỏ qua dòng trống
                
                # Thêm URL mới
                urls.append(new_camera_url)
                
                # Ghi lại file
                with open('./data/camera.txt', 'w') as f:
                    f.write('\n'.join(urls))

                # Cập nhật lại danh sách camera
                self.camera_handler.camera_urls = self.load_camera_urls()
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

    def find_start_button(self, camera_index):
        """Tìm nút Start/Stop cho camera dựa trên chỉ số."""
        return self.findChild(QPushButton, f"btn_Start_{camera_index + 1}")

    def find_camera_view(self, camera_index):
        """Tìm view camera cho camera dựa trên chỉ số."""
        return self.findChild(QLabel, f"camera_{camera_index + 1}")

    def delete_camera(self, url):
        try:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Question)
            msg.setText("DO YOU WANT TO DELETE THIS CAMERA?")
            msg.setWindowTitle("CONFIRM DELETE")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)
            
            if msg.exec_() == QMessageBox.Yes:
                # Tìm button được click
                sender = self.sender()
                if sender:
                    # Lấy index từ tên của button close
                    button_name = sender.objectName()
                    camera_index = int(button_name.split('_')[-1]) - 1
                    
                    # Đọc nội dung file và loại bỏ dòng trống
                    with open('./data/camera.txt', 'r') as f:
                        urls = [line.strip() for line in f.readlines() if line.strip()]
                    
                    # Xóa URL tại vị trí camera cần xóa
                    urls.pop(camera_index)
                    
                    # Ghi lại file
                    with open('./data/camera.txt', 'w') as f:
                        f.write('\n'.join(urls))
                    
                    # Cập nhật lại danh sách camera
                    self.camera_handler.camera_urls = self.load_camera_urls()
                    self.clear_layout()
                    self.load_cameras()
                    
        except Exception as e:
            print(f"Error deleting camera: {str(e)}")