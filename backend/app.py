from flask import Flask, jsonify, request
from flask import Response
from flask_cors import CORS
from dotenv import load_dotenv
from supabase import create_client
from math import radians, sin, cos, asin, sqrt
import os
import json


# env 가져오기
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")       # ex) "https://xyzcompany.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")       # service_role 키나 anon 키

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)
CORS(app) # CORS 설정 (모든 도메인 허용)

# 거리 계산 함수 (Haversine 공식)
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # km 단위
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    return R * c

# 위치 기반 추천 API - 테스트 완료. 잘 돌아감
@app.route("/api/recommendation/location")
def recommend_location():
    try:
        # 사용자 위치 받기
        user_lat = float(request.args.get("lat"))
        user_lng = float(request.args.get("lng"))

        # Supabase에서 모든 location 정보 불러오기
        response = supabase.table("location").select("id, name, building, lat, lng").execute()
        locations = response.data

        # 거리 계산 및 정렬
        closest = sorted(
            locations,
            key=lambda loc: haversine(user_lat, user_lng, float(loc["lat"]), float(loc["lng"]))
        )[0]  # 가장 가까운 위치 1개

        #JSON 문자열로 변환 후 UTF-8 명시해서 응답. 한국어 깨짐 처리
        return Response(
            json.dumps({"recommended_location": closest}, ensure_ascii=False),
            content_type="application/json; charset=utf-8"
        )

    except Exception as e:
        return Response(
            json.dumps({"error": str(e)}, ensure_ascii=False),
            content_type="application/json; charset=utf-8"), 500

# supabase 연결 테스트용 API (임시적으로 사용)  
@app.route("/test")
def test():
    response = supabase.table("location").select("id,name").execute()
    return Response(
        json.dumps(response.data, ensure_ascii=False),
        content_type="application/json; charset=utf-8" #한국어 지원을 위해 utf-8로 설정
    )

# 서버 체크용 API (임시적으로 사용)
@app.route("/")
def home():
    return "✅ Flask 서버가 잘 작동 중입니다!"

if __name__ == "__main__":
    app.run(debug=True)