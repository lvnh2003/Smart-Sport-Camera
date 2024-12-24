import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton


class NotifyMessage(QDialog):
    def __init__(self, message, signal=1):
        super(NotifyMessage, self).__init__()
        self.setWindowTitle("Notification")
        self.signal = signal

        # Remove the help button from the title bar
        # self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout()

        # Example: Add an icon to the center of the dialog
        icon_label = QLabel(self)
        pixmap = QPixmap('./src/ui/images/success.png')
        if self.signal == 0:
            pixmap = QPixmap('./src/ui/images/warning.png')  
        pixmap = pixmap.scaledToWidth(50) 
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        # Add the message label
        message_label = QLabel(message)
        layout.addWidget(message_label)

        # Add the "OK" button
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)

        self.setLayout(layout)
        self.exec_()