from PyQt5.QtWidgets import QApplication

from src.preprocessing.classify import *
from src.components.load_ui import LoadUI
if __name__ == "__main__":
    model = YOLO("./src/models/best.pt")
    video_path = "./data/test.mp4"
    # annotate_video(video_path, model)
    app = QApplication([])
    mainwindow = LoadUI(model)
    mainwindow.show()
    app.exec_()
