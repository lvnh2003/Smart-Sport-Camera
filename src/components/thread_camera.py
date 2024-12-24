from PyQt5.QtCore import pyqtSignal, QThread
import numpy as np, cv2

from src.preprocessing.classify import get_players_boxes, get_player_classifier, get_left_team_label, \
    get_grass_color, classify_players, get_player_colors
from src.utils.config import box_colors, labels
from src.components.notify import NotifyMessage


class ThreadCamera(QThread):
    ImageUpdate = pyqtSignal(np.ndarray)
    ImageDisplayMain = pyqtSignal(np.ndarray)
    def __init__(self, model, camera, index, change_state):
        super().__init__()
        self.model = model
        self.camera = camera
        self.index = index
        self.change_state = change_state

    # run camera
    def run(self):
        Capture = cv2.VideoCapture("./data/" + self.camera)
        Capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        Capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)

        self.ThreadActive = True
        players_clf = None
        left_team_label = 0
        grass_hsv = None
        eligible = False
        while self.ThreadActive:
            ret, frame_cap = Capture.read()

            if ret:
                result = self.model(frame_cap, conf=0.5, verbose=False)[0]
                players_imgs, players_boxes = get_players_boxes(result)
                players_colors = get_player_colors(players_imgs, grass_hsv, frame_cap)
                # kiểm tra frame đó có đủ điều kiện không ( classify các cầu thủ )
                if not eligible:
                    if players_boxes and len(players_colors)>=2 :
                        players_clf = get_player_classifier(players_colors)
                        left_team_label = get_left_team_label(players_boxes, players_colors, players_clf)
                        grass_color = get_grass_color(result.orig_img)
                        grass_hsv = cv2.cvtColor(np.uint8([[list(grass_color)]]), cv2.COLOR_BGR2HSV)
                        eligible = True
                    continue

                counts = {
                    "team_left": 0, "team_right": 0,
                    "gk_left": 0, "gk_right": 0,
                    "ball": 0, "main_ref": 0
                }
                positions = {"ball": None, "ref": None, "players": [], "goalkeepers": []}
                for box in result.boxes:
                    label = int(box.cls.cpu().numpy()[0])
                    x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                    center_position = ((x1 + x2) // 2, (y1 + y2) // 2)
                    #Nếu trong box có chứa cầu thủ thì tìm người đó thuộc team nào

                    if label == 0:
                        player_color = get_player_colors([result.orig_img[y1: y2, x1: x2]], grass_hsv)
                        team = classify_players(players_clf, player_color)
                        if team == left_team_label:
                            counts["team_left"] += 1
                            label = 0
                        else:
                            counts["team_right"] += 1
                            label = 1
                        positions["players"].append(center_position)
                    # Nếu trong box có chứa thủ môn thì tìm người đó thuộc team nào
                    elif label == 1:
                        if x1 < 0.5 * 300:
                            label = 2
                            counts["gk_left"] += 1
                        else:
                            label = 3
                            counts["gk_right"] += 1
                        positions["goalkeepers"].append(center_position)
                    elif label == 2:
                        counts["ball"] += 1
                        positions["ball"] = center_position
                        label = 4
                    elif label == 3:
                        counts["main_ref"] += 1
                        positions["ref"] = center_position
                        label = 5
                    # Tăng nhãn lên 2 vì có thêm hai nhãn "Player-L", "GK-L", các classes còn lại không sử dụng
                    else:
                        label = label + 2

                    cv2.rectangle(frame_cap, (x1, y1), (x2, y2), box_colors[str(label)], 2)
                    cv2.putText(frame_cap, labels[label], (x1 - 30, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                                box_colors[str(label)], 2)
                # Nếu đạt các điều kiện thì hiện thị trên camera chính
                point = 0
                # Thủ môn và bóng xuất hiện gần nhau
                if counts["ball"] > 0 and (counts["gk_left"] > 0 or counts["gk_right"] > 0):
                    point += 4

                # Cầu thủ và trọng tài gần nhau!
                if counts["main_ref"] > 0 and positions["ref"] is not None:
                    for player_pos in positions["players"]:
                        if np.linalg.norm(np.array(positions["ref"]) - np.array(player_pos)) < 50:
                            point += 3

                # Tình huống tranh chấp xảy ra
                if counts["team_left"] + counts["team_right"] > 3 and counts["ball"] == 0:
                    point += 2

                # Có cầu thủ và bóng trên sân!
                if counts["team_left"] + counts["team_right"] >= 2 and counts["ball"] > 0:
                    point += 1

                # kiểm tra có phải là thread camera  hiện tại có phải có point cao nhất không
                array_cameras = self.change_state(self.index, point)
                is_max_point = max(array_cameras, key=array_cameras.get) == self.index
                if is_max_point:
                    self.ImageDisplayMain.emit(frame_cap)
                self.ImageUpdate.emit(frame_cap)

    def stop(self):
        self.ThreadActive = False
        self.quit()

class ThreadCameraAdd(QThread):
    ImageUpdate = pyqtSignal(np.ndarray)
    NotifySignal = pyqtSignal(str)

    def __init__(self, camera):
        super().__init__()
        self.ThreadActive = False
        self.camera = camera
        self.NotifySignal.connect(self.notify_error)

    def run(self):
        Capture = cv2.VideoCapture("./data/" + self.camera)
        if not Capture.isOpened():
            self.NotifySignal.emit("Invalid Camera IP Address \nPlease check again")
            print("Error: Camera could not be opened.")
            self.stop()
            return

        Capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        Capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.ThreadActive = True
        while self.ThreadActive:
            ret, frame_cap = Capture.read()
            if ret:
                self.ImageUpdate.emit(frame_cap)
        Capture.release()

    def stop(self):
        self.ThreadActive = False
        self.quit()
        
    def notify_error(self, message):
        NotifyMessage(message, 0)
