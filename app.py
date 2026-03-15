from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)
DB_FILE = "users.json"
APP_KEY = "stock_ai_2025"

# 初始化用户数据库（不存在则创建）
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)

def load():
    """加载用户数据"""
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save(data):
    """保存用户数据"""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ====== 登录验证接口（支持 machine 绑定） ======
@app.route("/verify", methods=["POST"])
def verify():
    try:
        j = request.json
        # 1. 验证 AppKey
        if j.get("appkey") != APP_KEY:
            return jsonify({"status": "fail", "msg": "非法应用"})
        
        # 2. 加载用户数据
        users = load()
        username = j.get("user")
        user = users.get(username)
        
        # 3. 验证账号是否存在
        if not user:
            return jsonify({"status": "fail", "msg": "账号不存在"})
        
        # 4. 验证密码
        if user.get("pwd") != j.get("pwd"):
            return jsonify({"status": "fail", "msg": "密码错误"})
        
        # 5. 验证/绑定机器码
        client_machine = j.get("machine")
        bound_machine = user.get("machine", "")
        
        # 5.1 首次登录：绑定当前机器码
        if not bound_machine and client_machine:
            user["machine"] = client_machine
            save(users)
            return jsonify({"status": "ok", "msg": "首次登录，已绑定当前设备"})
        
        # 5.2 非首次登录：验证机器码
        if bound_machine != client_machine:
            return jsonify({"status": "fail", "msg": "账号已绑定其他电脑"})
        
        # 6. 所有验证通过
        return jsonify({"status": "ok", "msg": "验证成功"})
    
    except Exception as e:
        print(f"验证异常：{str(e)}")
        return jsonify({"status": "fail", "msg": f"服务器异常：{str(e)}"})

# ====== 后台添加账号接口 ======
@app.route("/admin/add", methods=["POST"])
def add():
    try:
        j = request.json
        users = load()
        # 添加账号时，machine 字段为空（首次登录绑定）
        users[j["user"]] = {"pwd": j["pwd"], "machine": ""}
        save(users)
        return jsonify({"status": "ok", "msg": "账号添加成功"})
    except Exception as e:
        return jsonify({"status": "fail", "msg": str(e)})

# ====== 后台解绑机器码接口（可选，方便管理） ======
@app.route("/admin/unbind", methods=["POST"])
def unbind():
    try:
        j = request.json
        users = load()
        user = users.get(j["user"])
        if user:
            user["machine"] = ""  # 清空机器码绑定
            save(users)
            return jsonify({"status": "ok", "msg": "机器码解绑成功"})
        else:
            return jsonify({"status": "fail", "msg": "账号不存在"})
    except Exception as e:
        return jsonify({"status": "fail", "msg": str(e)})

if __name__ == "__main__":
    # Render 要求用 0.0.0.0 和指定端口（或默认端口）
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
