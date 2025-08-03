from flask import Flask, jsonify
from flask import Response
from dotenv import load_dotenv
from supabase import create_client
import os
import json


# env 가져오기
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")       # ex) "https://xyzcompany.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")       # service_role 키나 anon 키

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

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