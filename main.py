from src.preprocessing.classify import *
if __name__ == "__main__":
    model = YOLO("./src/models/best.pt")
    video_path = "./data/test.mp4"
    annotate_video(video_path, model)