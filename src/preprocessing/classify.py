import cv2
import numpy as np
from sklearn.cluster import KMeans
from src.utils.config import box_colors, labels
def get_grass_color(img):
    """
        Tìm màu của cỏ trong nền của hình ảnh

    Đối số:
    img: np.array đối tượng có hình dạng (WxHx3) biểu diễn giá trị BGR của
    pixel khung hình.

    Trả về:
    grass_color
    Bộ giá trị BGR của màu cỏ trong hình ảnh
    """
    # Convert image to HSV color space
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Define range of green color in HSV
    lower_green = np.array([30, 40, 40])
    upper_green = np.array([80, 255, 255])

    # Threshold the HSV image to get only green colors
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # Calculate the mean value of the pixels that are not masked
    masked_img = cv2.bitwise_and(img, img, mask=mask)
    grass_color = cv2.mean(img, mask=mask)
    return grass_color[:3]

def get_players_boxes(result):
    """
       Tìm hình ảnh của người chơi trong khung và hộp giới hạn của họ.

    Đối số:
    kết quả: đối tượng ultralytics.engine.results.Results chứa tất cả
    kết quả của việc chạy thuật toán phát hiện đối tượng trên khung

    Trả về:
    players_imgs
    Danh sách các đối tượng np.array chứa các giá trị BGR của các phần đã cắt
    của hình ảnh chứa người chơi.
    players_boxes
    Danh sách các đối tượng ultralytics.engine.results.Boxes chứa nhiều
    thông tin về hộp giới hạn của người chơi được tìm thấy trong hình ảnh.
    """
    players_imgs = []
    players_boxes = []
    if not result.boxes or len(result.boxes) == 0:
        print("No boxes detected.")
        return players_imgs, players_boxes

    for box in result.boxes:
        label = int(box.cls.cpu().numpy()[0])  # Chuyển tensor về CPU
        if label == 0:  # Check if the detected object is a player
            x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())  # Chuyển các tọa độ về CPU
            player_img = result.orig_img[y1: y2, x1: x2]
            players_imgs.append(player_img)
            players_boxes.append(box)
    return players_imgs, players_boxes

def get_kits_colors(players, grass_hsv=None, frame=None):
  """
      Tìm màu bộ dụng cụ của tất cả người chơi trong khung hiện tại

    Đối số:
    players: Danh sách các đối tượng np.array chứa các giá trị BGR của hình ảnh
    các phần chứa người chơi.
    grass_hsv: bộ chứa giá trị màu HSV của màu cỏ của
    nền hình ảnh.

    Trả về:
    kits_colors
    Danh sách các mảng np chứa các giá trị BGR của màu bộ dụng cụ của tất cả
    người chơi trong khung hiện tại
  """
  kits_colors = []
  if grass_hsv is None:
    grass_color = get_grass_color(frame)
    grass_hsv = cv2.cvtColor(np.uint8([[list(grass_color)]]), cv2.COLOR_BGR2HSV)

  for player_img in players:
      # Convert image to HSV color space
      hsv = cv2.cvtColor(player_img, cv2.COLOR_BGR2HSV)

      # Define range of green color in HSV
      lower_green = np.array([grass_hsv[0, 0, 0] - 10, 40, 40])
      upper_green = np.array([grass_hsv[0, 0, 0] + 10, 255, 255])

      # Threshold the HSV image to get only green colors
      mask = cv2.inRange(hsv, lower_green, upper_green)

      # Bitwise-AND mask and original image
      mask = cv2.bitwise_not(mask)
      upper_mask = np.zeros(player_img.shape[:2], np.uint8)
      upper_mask[0:player_img.shape[0]//2, 0:player_img.shape[1]] = 255
      mask = cv2.bitwise_and(mask, upper_mask)

      kit_color = np.array(cv2.mean(player_img, mask=mask)[:3])

      kits_colors.append(kit_color)
  return kits_colors

def get_kits_classifier(kits_colors):
  """
      Tạo một bộ phân loại K-Means có thể phân loại các bộ dụng cụ theo giá trị BGR của chúng
    thành 2 nhóm khác nhau, mỗi nhóm đại diện cho một trong các đội

    Đối số:
    kits_colors: Danh sách các đối tượng np.array chứa các giá trị BGR của
    màu sắc của các bộ dụng cụ của những người chơi được tìm thấy trong khung hình hiện tại.S

    Trả về:
    kits_kmeans
    sklearn.cluster.KMeans đối tượng có thể phân loại các bộ dụng cụ của người chơi thành
    2 đội theo màu sắc của họ..
  """
  kits_kmeans = KMeans(n_clusters=2)
  kits_kmeans.fit(kits_colors)
  return kits_kmeans

def classify_kits(kits_classifer, kits_colors):
  """
     Phân loại người chơi thành một trong hai đội theo bộ đồ của người chơi
    màu

    Đối số:
    kits_classifer: sklearn.cluster.KMeans đối tượng có thể phân loại
    bộ đồ của người chơi thành 2 đội theo màu của họ.
    kits_colors: Danh sách các đối tượng np.array chứa các giá trị BGR của
    màu sắc của bộ đồ của người chơi được tìm thấy trong khung hình hiện tại.

    Trả về:
    team
    đối tượng np.array chứa một số nguyên duy nhất mang số đội của người chơi (0 hoặc 1)
  """
  team = kits_classifer.predict(kits_colors)
  return team

def get_left_team_label(players_boxes, kits_colors, kits_clf):
  """
  Tìm nhãn của đội ở bên trái màn hình

    Đối số:
    players_boxes: Danh sách các đối tượng ultralytics.engine.results.Boxes
    chứa nhiều thông tin khác nhau về các hộp giới hạn của các cầu thủ được tìm thấy
    trong hình ảnh.
    kits_colors: Danh sách các đối tượng np.array chứa các giá trị BGR của
    màu sắc của các bộ dụng cụ của các cầu thủ được tìm thấy trong khung hình hiện tại.
    kits_clf: đối tượng sklearn.cluster.KMeans có thể phân loại các bộ dụng cụ của cầu thủ
    thành 2 đội theo màu sắc của họ.
    Trả về:
    left_team_label
    Int chứa số của đội ở bên trái hình ảnh
    (0 hoặc 1)
  """
  left_team_label = 0
  team_0 = []
  team_1 = []

  for i in range(len(players_boxes)):
    x1, y1, x2, y2 = map(int, players_boxes[i].xyxy[0].cpu().numpy())

    team = classify_kits(kits_clf, [kits_colors[i]]).item()
    if team==0:
      team_0.append(np.array([x1]))
    else:
      team_1.append(np.array([x1]))

  team_0 = np.array(team_0)
  team_1 = np.array(team_1)

  if np.average(team_0) - np.average(team_1) > 0:
    left_team_label = 1

  return left_team_label
