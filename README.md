
## Cấu trúc dự án
```
    Smart-Sport-Camera/
├── data/            # Dữ liệu
│   ├── cameras.txt
├── src/            # Mã nguồn chính
│   ├── models/            # Các mô hình
│   │   ├── best.pt
│   ├── preprocessing/     # Xử lý dữ liệu đầu vào
│   │   ├── classify.py
│   ├── ui
│   └── utils/             # Các hàm tiện ích      
│       ├── config.py
├── requirements.txt
├── README.md
└── .gitignore
```

### Các trường hợp đáng chú ý
```
1.Có sự xuất hiện của các cầu thủ và bóng trên sân
    Team Left + Team Right >= 2 and Ball > 0
2.Có cầu thủ và trọng tài xuất hiện gần nhau
    Main Ref > 1 and Team Left + Team Right > 0
3.Thủ môn và bóng xuất hiện gần nhau
    Ball > 0 and ( GoalKeeper Left > 0 or GoalKeeper Right >0 )
4. Các tình huống gây tranh cãi (vào bóng mạnh hoặc va chạm)
    Team Left + Team Right > 3 and Ball < 0:
```