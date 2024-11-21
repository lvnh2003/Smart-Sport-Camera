from PyQt5.QtCore import pyqtSignal, QThread
import numpy as np,cv2
from src.preprocessing.classify import get_kits_colors, get_players_boxes, get_kits_classifier, get_left_team_label, \
    get_grass_color, classify_kits
from src.utils.config import box_colors, labels


class ThreadCamera(QThread):
    ImageUpdate = pyqtSignal(np.ndarray)
    def __init__(self,model,camera):
        super().__init__()
        self.model = model
        self.camera = camera

    # run camera
    def run(self):
        Capture = cv2.VideoCapture("./data/"+self.camera)
        Capture.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
        Capture.set(cv2.CAP_PROP_FRAME_WIDTH,640)

        self.ThreadActive = True
        kits_clf = None
        left_team_label = 0
        grass_hsv = None
        while self.ThreadActive:
            ret,frame_cap = Capture.read()
            current_frame_idx = Capture.get(cv2.CAP_PROP_POS_FRAMES)
            if ret:
                result =  self.model(frame_cap, conf=0.5, verbose=False)[0]
                players_imgs, players_boxes = get_players_boxes(result)
                kits_colors = get_kits_colors(players_imgs, grass_hsv, frame_cap)
                # chạy 1 frame đầu tiên thôi
                if current_frame_idx == 1:
                    kits_clf = get_kits_classifier(kits_colors)
                    left_team_label = get_left_team_label(players_boxes, kits_colors, kits_clf)
                    grass_color = get_grass_color(result.orig_img)
                    grass_hsv = cv2.cvtColor(np.uint8([[list(grass_color)]]), cv2.COLOR_BGR2HSV)

                for box in result.boxes:
                    label = int(box.cls.cpu().numpy()[0])
                    x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())

                    #Nếu trong box có chứa cầu thủ thì tìm người đó thuộc team nào

                    if label == 0:
                        kit_color = get_kits_colors([result.orig_img[y1: y2, x1: x2]], grass_hsv)
                        team = classify_kits(kits_clf, kit_color)
                        if team == left_team_label:
                            label = 0
                        else:
                            label = 1

                    # Nếu trong box có chứa thủ môn thì tìm người đó thuộc team nào
                    elif label == 1:
                        if x1 < 0.5 * 300:
                            label = 2
                        else:
                            gk_label = 3

                    # Tăng nhãn lên 2 vì có thêm hai nhãn "Player-L", "GK-L"
                    else:
                        label = label + 2

                    cv2.rectangle(frame_cap, (x1, y1), (x2, y2), box_colors[str(label)], 2)
                    cv2.putText(frame_cap, labels[label], (x1 - 30, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                                box_colors[str(label)], 2)
                self.ImageUpdate.emit(frame_cap)

    def stop(self):
        self.ThreadActive = False
        self.quit()