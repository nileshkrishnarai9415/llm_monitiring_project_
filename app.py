from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import requests
import os

app = Flask(__name__)
CORS(app)

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

# ==============================
# 🔹 LLM Function
# ==============================
def ask_ollama(prompt):
    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            }
        )

        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            return f"LLM Error: {response.text}"

    except Exception as e:
        return f"LLM Connection Error: {str(e)}"


# ==============================
# 🔹 Home Route
# ==============================
@app.route("/")
def home():
    return "LLM System Monitoring Backend Running 🚀"


# ==============================
# 🔹 Analyze Route
# ==============================
@app.route("/analyze", methods=["POST"])
def analyze_file():

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"})

    file = request.files["file"]

    try:
        df = pd.read_excel(file)

        # Required columns
        required_columns = ["timestamp", "cpu_usage", "memory_usage", "disk_usage"]

        if not all(col in df.columns for col in required_columns):
            return jsonify({"error": "Invalid file format. Required columns missing."})

        alerts = []

        # ==============================
        # 🔹 Alert Logic
        # ==============================
        if df["cpu_usage"].max() > 80:
            alerts.append("High CPU Usage Detected (>80%)")

        if df["memory_usage"].max() > 80:
            alerts.append("High Memory Usage Detected (>80%)")

        if df["disk_usage"].max() > 90:
            alerts.append("High Disk Usage Detected (>90%)")

        if not alerts:
            alerts.append("System is Stable ✅")

        # ==============================
        # 🔹 LLM Analysis
        # ==============================
        summary = f"""
        System Monitoring Report:

        Max CPU Usage: {df['cpu_usage'].max()}%
        Max Memory Usage: {df['memory_usage'].max()}%
        Max Disk Usage: {df['disk_usage'].max()}%

        Alerts:
        {", ".join(alerts)}

        Give a professional analysis and improvement suggestions.
        """

        llm_response = ask_ollama(summary)

        return jsonify({
            "alerts": alerts,
            "analysis": llm_response
        })

    except Exception as e:
        return jsonify({"error": str(e)})


# ==============================
# 🔹 Run App
# ==============================
if __name__ == "__main__":
    app.run(debug=True)