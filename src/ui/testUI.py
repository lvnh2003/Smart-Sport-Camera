import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer, QTime, Qt
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QGridLayout, QWidget 

class MainWindow(QtWidgets.QMainWindow):
    
    def __init__(self):
        super().__init__()
        # Load UI file
        uic.loadUi('mainwindow.ui', self)
        
        # Setup ScrollArea
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Load cameras from file
        self.load_cameras()
        
        # Setup timer for LCD display
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        
        # Initial time update
        self.update_time()
        
        # Show the window
        self.show()
    
    def load_cameras(self):
        try:
            # Xóa layout cũ nếu có
            self.clear_layout()
            
            # Đọc danh sách camera từ file
            with open('camera.txt', 'r') as f:
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
                camera.setObjectName(f"camera_{i+1}")
                camera.setStyleSheet("QLabel { border: 1px solid grey; background-color: #f0f0f0; }")
                camera.setFixedSize(251, 141)
                
                # Tạo nút Start
                btn = QPushButton("Start")
                btn.setObjectName(f"btn_Start_{i+1}")
                btn.setStyleSheet("background-color: red; border: 1; border-radius: 5")
                btn.setFixedSize(91, 41)
                
                # Thêm vào layout
                row = i // num_columns
                col = i % num_columns
                layout.addWidget(camera, row*2, col)
                layout.addWidget(btn, row*2+1, col, Qt.AlignCenter)
            
            # Thêm nút Add New Camera
            add_camera_btn = QPushButton()
            add_camera_btn.setObjectName("addCameraBtn")
            add_camera_btn.setStyleSheet("""
                QPushButton {
                    border: 2px dashed grey;
                    background-color: transparent;
                    image: url(add.png);  /* Thêm icon cho button add camera */
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                }
            """)
            add_camera_btn.setFixedSize(251, 141)
            add_camera_btn.setCursor(Qt.PointingHandCursor)
            add_camera_btn.clicked.connect(self.open_camera_settings)
            
            # Tính vị trí cho nút Add New Camera
            next_row = (len(camera_urls)) // num_columns
            next_col = (len(camera_urls)) % num_columns
            layout.addWidget(add_camera_btn, next_row*2, next_col)
            
            # Tính toán chiều rộng tối thiểu cho scrollAreaWidgetContents
            total_items = len(camera_urls) + 1  # +1 cho nút Add New Camera
            required_columns = (total_items + num_columns - 1) // num_columns
            min_width = num_columns * (251 + 20)  # 20 là khoảng cách giữa các camera
            self.scrollAreaWidgetContents.setMinimumWidth(min_width)
            
        except FileNotFoundError:
            print("Không tìm thấy file camera.txt")
        except Exception as e:
            print(f"Lỗi khi đọc file camera: {str(e)}")
    
    def update_time(self):
        current_time = QTime.currentTime()
        display_text = current_time.toString('hh:mm:ss')
        self.time_clock.display(display_text)
    
    def open_camera_settings(self):
        # Tạo và hiển thị cửa sổ camera settings
        self.camera_settings = QtWidgets.QMainWindow()
        uic.loadUi('camera_setting.ui', self.camera_settings)
        
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
                with open('camera.txt', 'a') as f:
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())