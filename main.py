from PyQt5.QtWidgets import QApplication
from src.components.load_ui import LoadUI
from ultralytics import YOLO
if __name__ == "__main__":
    model = YOLO("./src/models/best.pt")
    app = QApplication([])
    mainwindow = LoadUI(model)
    mainwindow.show()
    app.exec_()
