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
        
# 장소 상세 정보 불러오기 - 버튼의 장소 id와 연결.
@app.route("/api/places/<int:place_id>", methods=["GET"])
def get_place_details(place_id: int):
    try:
        # location.id == place_id 인 행에서 필요한 필드 모두 조회
        res = (
            supabase
            .table("location")
            .select("id, name, building, max_group, details")
            .eq("id", place_id)
            .limit(1)
            .execute()
        )

        if not res.data:
            payload = {"error": f"Place id {place_id} not found"}
            return Response(
                json.dumps(payload, ensure_ascii=False),
                status=404,
                content_type="application/json; charset=utf-8"
            )

        row = res.data[0]

        # max_group 정수 변환(없거나 형식이 이상하면 None)
        try:
            max_group = int(row["max_group"]) if row.get("max_group") is not None else None
        except (ValueError, TypeError):
            max_group = None

        payload = {
            "place": {
                "id": row.get("id"),
                "name": row.get("name", ""),        # 텍스트(한글) OK
                "building": row.get("building", ""),# 텍스트(한글) OK
                "max_group": max_group,             # 정수
                "details": row.get("details", ""),  # 텍스트(한글) OK
            }
        }

        return Response(
            json.dumps(payload, ensure_ascii=False),
            content_type="application/json; charset=utf-8"
        )

    except Exception as e:
        payload = {"error": str(e)}
        return Response(
            json.dumps(payload, ensure_ascii=False),
            status=500,
            content_type="application/json; charset=utf-8"
        )

#혼잡도 기반 추천 API - 혼잡도 낮은 순으로 장소 추천
@app.route("/api/recommendation/congestion")
def get_congestion():
    try:
        location_id = request.args.get("location_id", type=int)
        limit = request.args.get("limit", default=20, type=int)  # 상위 N개만 보고 싶을 때

        query = supabase.table("v_location_congestion").select(
            "location_id,name,building,capacity,"
            "current_people,congestion"
        )

        if location_id:
            query = query.eq("location_id", location_id)

        # 혼잡도 낮은 순으로 추천 (NULL은 맨 뒤로)
        data = (query
                .order("congestion", desc=False, nullsfirst=False)
                .limit(limit)
                .execute()
               ).data

        return Response(
            json.dumps({"items": data}, ensure_ascii=False),
            content_type="application/json; charset=utf-8"
        )

    except Exception as e:
        return Response(
            json.dumps({"error": str(e)}, ensure_ascii=False),
            content_type="application/json; charset=utf-8"
        ), 500

#시간대별 혼잡도 - 장소 id, 시간대별로 가능.
@app.route("/api/congestion/avg")
def avg_congestion_by_hour():
    try:
        loc = request.args.get("location_id", type=int)
        hr = request.args.get("hour", type=int)

        if loc is None or hr is None:
            return jsonify({"error": "location_id and hour are required"}), 400

        # v_hourly_avg_28d에서 해당 장소 + 시간대 평균 데이터 조회
        rows = (supabase.table("v_hourly_avg_28d")
                .select("location_id,hour,avg_congestion,avg_people")
                .eq("location_id", loc)
                .eq("hour", hr)
                .limit(1)
                .execute()).data

        if not rows:
            return jsonify({"message": "No data found"}), 404

        return jsonify(rows[0])

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#인원수별 혼잡도 GET
@app.route("/api/congestion_people")
def get_congestion_people():
    try:
        group = request.args.get("group", type=int)
        limit = request.args.get("limit", default=50, type=int)

        if group is None or group <= 0:
            return Response(
                json.dumps({"error": "group must be a positive integer"}, ensure_ascii=False),
                status=400,
                content_type="application/json; charset=utf-8"
            )

        limit = max(1, min(limit, 200))  # 과도한 요청 방지

        cols = ("location_id,name,building,campus,capacity,max_group,"
                "current_people,congestion")

        data = (supabase.table("v_location_congestion")
                .select(cols)
                .gte("max_group", group)                     # ✅ group 이상 수용 가능한 장소만
                .order("congestion", desc=False, nullsfirst=False)  # ✅ 혼잡도 낮은 순, NULL은 뒤로
                .limit(limit)
                .execute()
               ).data

        return Response(
            json.dumps({"group": group, "count": len(data), "items": data}, ensure_ascii=False),
            content_type="application/json; charset=utf-8"
        )

    except Exception as e:
        return Response(
            json.dumps({"error": str(e)}, ensure_ascii=False),
            status=500,
            content_type="application/json; charset=utf-8"
        )
        
        
#-----------------------------test api-------------------------------------#

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

#---------------------------------------------------------------------------#

if __name__ == "__main__":
    app.run(debug=True)