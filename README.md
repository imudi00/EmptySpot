<yolo모델 설치>  
git clone https://github.com/ultralytics/yolov5  
cd yolov5  
pip install -r requirements.txt  

파일 구조
main.py: 실제 서비스 시 작동하는 코드(실시간 영상)  
extract_roi.py: 환경에맞게 ROI 좌표를 추출하는 코드  
evaluation.py: 녹화된 영상으로 테스트/평가해보는 코드(실험용 영상 첨부)  
json_to_DB_daemon.py: main.py로 바뀌는 json파일을 실시간으로 DB로 전송하는 코드  
yolo_snapshot.json: 좌석 정보를 담은 JSON 파일
`best.pt`, `4th.pt`: YOLO 가중치/ 4th.pt가 기본, best.pt는 특정 위치에 파인튜닝한 버전  


## Acknowledgments  
- Inspired by: https://github.com/Artecrowd/yolov5  
- Inspired by: https://github.com/Artecrowd/Artecrowd_Android  



