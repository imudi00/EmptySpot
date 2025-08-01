from flask import Flask, jsonify
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

@app.route("/api/ping")
def ping():
    return jsonify({"message": "pong!"})

if __name__ == "__main__":
    app.run(debug=True)
