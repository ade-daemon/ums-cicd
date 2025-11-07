from flask import Flask, jsonify, request
from flask_cors import CORS  # ✅ Import CORS

app = Flask(__name__)
CORS(app)  # ✅ Enable CORS

users = {
    "demo": {"password": "1234", "name": "Demo User"}
}

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = users.get(username)
    if user and user["password"] == password:
        return jsonify({"message": "Login successful", "name": user["name"]}), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/')
def home():
    return jsonify({"service": "auth-service", "status": "running"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

