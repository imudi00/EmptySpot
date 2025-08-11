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

# 거리 계산 함수 (Haversine 공식) - 위치 기반 추천api
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # km 단위
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    return R * c

# 혼잡도 계산 함수 - 혼잡도 기반 추천api

# 위치 기반 추천 API - 테스트 완료. 잘 돌아감
@app.route("/api/recommendation/location")
def recommend_location():
    try:
        user_lat = float(request.args.get("lat"))
        user_lng = float(request.args.get("lng"))

        response = supabase.table("location").select("id, name, building, lat, lng").execute()
        locations = response.data

        # 거리 계산 후 각 장소에 distance 추가
        for loc in locations:
            distance = haversine(user_lat, user_lng, float(loc["lat"]), float(loc["lng"]))
            loc["distance_km"] = round(distance, 3)  # 보기 좋게 소수점 3자리로

        # 거리순 정렬
        sorted_locations = sorted(locations, key=lambda loc: loc["distance_km"])

        # JSON 응답
        return Response(
            json.dumps({"sorted_locations": sorted_locations}, ensure_ascii=False),
            content_type="application/json; charset=utf-8"
        )

    except Exception as e:
        return Response(
            json.dumps({"error": str(e)}, ensure_ascii=False),
            content_type="application/json; charset=utf-8"
        ), 500
        
# 유형 기반 공간 필터링 API
@app.route("/api/recommendation/type")
def recommend_by_type():
    try:
        # 쿼리 파라미터로 type 받아오기
        type_value = request.args.get("type")
        if not type_value:
            return Response(
                json.dumps({"error": "type parameter is required"}, ensure_ascii=False),
                content_type="application/json; charset=utf-8"
            ), 400

        # Supabase에서 해당 type에 맞는 장소 가져오기
        response = supabase.table("location").select("id, name, lat, lng, type").eq("type", type_value).execute()
        results = response.data

        return Response(
            json.dumps({"matched_locations": results}, ensure_ascii=False),
            content_type="application/json; charset=utf-8"
        )

    except Exception as e:
        return Response(
            json.dumps({"error": str(e)}, ensure_ascii=False),
            content_type="application/json; charset=utf-8"
        ), 500

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
    return "Flask 서버가 잘 작동 중입니다!"

if __name__ == "__main__":
    app.run(debug=True)