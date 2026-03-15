from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)
DB_FILE = "users.json"
APP_KEY = "stock_ai_2025"

if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)

def load():
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ====== 되쩌駱聯쌈왯 ======
@app.route("/verify", methods=["POST"])
def verify():
    j = request.json
    if j.get("appkey") != APP_KEY:
        return jsonify({"status":"fail"})
    users = load()
    user = users.get(j.get("user"))
    if not user or user.get("pwd") != j.get("pwd"):
        return jsonify({"status":"fail"})
    mc = j.get("machine")
    if not user.get("machine"):
        user["machine"] = mc
        save(users)
    if user.get("machine") != mc:
        return jsonify({"status":"fail"})
    return jsonify({"status":"ok"})

# ====== 빈憩警속瑯뵀 ======
@app.route("/admin/add", methods=["POST"])
def add():
    j = request.json
    users = load()
    users[j["user"]] = {"pwd": j["pwd"], "machine": ""}
    save(users)
    return jsonify({"status":"ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
