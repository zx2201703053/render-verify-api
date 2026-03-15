from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # 允许跨域

# 模拟的账号数据库（这里应改为真实数据库）
# 格式: username: {"pwd": "md5密码", "machine": "绑定码"}
user_db = {
    "admin": {
        "pwd": "123456", # 这里保持明文或使用md5加密，代码逻辑是对比pwd
        "machine": "" # 留空则不限制机器码
    }
}

@app.route('/verify', methods=['POST'])
def verify():
    """
    本地GUI登录验证接口
    接收：appkey, user, pwd, machine
    返回：status: ok 或 error
    """
    data = request.get_json()
    appkey = data.get("appkey")
    username = data.get("user")
    password = data.get("pwd")
    client_machine = data.get("machine")

    # 1. 验证AppKey
    if appkey != "stock_ai_2025":
        return jsonify({"status": "error", "msg": "非法应用"}), 403

    # 2. 检查用户是否存在
    user_info = user_db.get(username)
    if not user_info:
        return jsonify({"status": "error", "msg": "账号不存在"}), 404

    # 3. 验证密码
    if user_info["pwd"] != password:
        return jsonify({"status": "error", "msg": "密码错误"}), 401

    # 4. (可选) 验证机器码绑定。如果不想绑定，直接跳过这一步返回ok
    # bound_machine = user_info.get("machine", "")
    # if bound_machine and bound_machine != client_machine:
    #     return jsonify({"status": "error", "msg": "账号已绑定其他电脑"}), 403

    # 5. 所有验证通过。如果需要绑定机器码，在这里更新machine字段
    # if not bound_machine:
    #     user_db[username]["machine"] = client_machine

    return jsonify({"status": "ok"})

@app.route('/admin/add', methods=['POST'])
def admin_add():
    """
    原有的添加账号接口（用于Postman测试）
    """
    data = request.get_json()
    user = data.get("user")
    pwd = data.get("pwd")
    
    if user and pwd:
        user_db[user] = {"pwd": pwd, "machine": ""}
        return jsonify({"status": "ok", "msg": "账号添加成功"})
    else:
        return jsonify({"status": "error", "msg": "参数错误"}), 400

if __name__ == '__main__':
    # Render使用0.0.0.0和默认端口
    app.run(host='0.0.0.0', port=10080)
