from src.preprocessing.classify import *
def annotate_video(video_path, model):
    """
    Loads the input video and runs the object detection algorithm on its frames, finally it annotates the frame with
    the appropriate labels

    Args:
        video_path: String the holds the path of the input video
        model: Object that represents the trained object detection model
    Returns:
    """
    cap = cv2.VideoCapture(video_path)

    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    kits_clf = None
    left_team_label = 0
    grass_hsv = None

    while cap.isOpened():
        # Read a frame from the video
        success, frame = cap.read()

        current_frame_idx = cap.get(cv2.CAP_PROP_POS_FRAMES)
        if success:

            # Run YOLOv8 inference on the frame
            annotated_frame = cv2.resize(frame, (width, height))
            result = model(annotated_frame, conf=0.5, verbose=False)[0]

            # Get the players boxes and kit colors
            players_imgs, players_boxes = get_players_boxes(result)
            kits_colors = get_kits_colors(players_imgs, grass_hsv, annotated_frame)

            # Run on the first frame only
            if current_frame_idx == 1:
                kits_clf = get_kits_classifier(kits_colors)
                left_team_label = get_left_team_label(players_boxes, kits_colors, kits_clf)
                grass_color = get_grass_color(result.orig_img)
                grass_hsv = cv2.cvtColor(np.uint8([[list(grass_color)]]), cv2.COLOR_BGR2HSV)

            for box in result.boxes:
                label = int(box.cls.numpy()[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0].numpy())

                # If the box contains a player, find to which team he belongs
                if label == 0:
                    kit_color = get_kits_colors([result.orig_img[y1: y2, x1: x2]], grass_hsv)
                    team = classify_kits(kits_clf, kit_color)
                    if team == left_team_label:
                        label = 0
                    else:
                        label = 1

                # If the box contains a Goalkeeper, find to which team he belongs
                elif label == 1:
                    if x1 < 0.5 * width:
                        label = 2
                    else:
                        gk_label = 3

                # Increase the label by 2 because of the two add labels "Player-L", "GK-L"
                else:
                    label = label + 2

                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), box_colors[str(label)], 2)
                cv2.putText(annotated_frame, labels[label], (x1 - 30, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                            box_colors[str(label)], 2)


            cv2.imshow("Result",annotated_frame)
            cv2.waitKey(1)
        else:
            # Break the loop if the end of the video is reached
            break
    cap.release()
    cv2.destroyAllWindows()
    # output_video.release()


if __name__ == "__main__":

    labels = ["T-L", "T-R", "GK-L", "GK-R", "Ball", "Main Ref", "Side Ref", "Staff"]
    box_colors = {
        "0": (150, 50, 50),
        "1": (37, 47, 150),
        "2": (41, 248, 165),
        "3": (166, 196, 10),
        "4": (155, 62, 157),
        "5": (123, 174, 213),
        "6": (217, 89, 204),
        "7": (22, 11, 15)
    }
    model = YOLO("./src/models/best.pt")
    video_path = sys.argv[1]
    annotate_video(video_path, model)