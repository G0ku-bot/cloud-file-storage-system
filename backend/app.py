import jwt
import datetime
from functools import wraps
from flask_cors import CORS
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import bcrypt
import os
from werkzeug.utils import secure_filename
from flask import send_from_directory

app = Flask(__name__)
CORS(app)

# 🔐 Secret key
app.config["SECRET_KEY"] = "your_secret_key"

# 🗄️ MySQL config
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "1234"
app.config["MYSQL_DB"] = "drive_app"

# 📁 Upload config
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# create uploads folder if not exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

mysql = MySQL(app)


@app.route("/")
def home():
    return "Backend running 🚀"


# 🔐 Register API
@app.route("/register", methods=["POST"])
def register():
    data = request.json

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    cursor = mysql.connection.cursor()

    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    if cursor.fetchone():
        cursor.close()
        return jsonify({"message": "Email already exists"}), 400

    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    cursor.execute(
        "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
        (name, email, hashed_pw)
    )

    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": "User registered successfully"})


# 🔑 Login API
@app.route("/login", methods=["POST"])
def login():
    data = request.json

    email = data.get("email")
    password = data.get("password")

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()
    cursor.close()

    if user:
        stored_password = user[3]

        if bcrypt.checkpw(password.encode("utf-8"), stored_password.encode("utf-8")):

            token = jwt.encode({
                "user_id": user[0],
                "email": user[2],
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
            }, app.config["SECRET_KEY"], algorithm="HS256")

            return jsonify({
                "message": "Login successful",
                "token": token,
                "user": {
                    "id": user[0],
                    "name": user[1],
                    "email": user[2]
                }
            })

    return jsonify({"message": "Invalid credentials"}), 401


# 🔐 JWT Middleware
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "Authorization" in request.headers:
            token = request.headers["Authorization"]

        if not token:
            return jsonify({"message": "Token is missing"}), 401

        try:
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        except:
            return jsonify({"message": "Token is invalid"}), 401

        return f(*args, **kwargs)

    return decorated


# 🔒 Protected route
@app.route("/protected", methods=["GET"])
@token_required
def protected():
    return jsonify({"message": "You accessed a protected route"})


# 📤 FILE UPLOAD ROUTE
@app.route("/upload", methods=["POST"])
@token_required
def upload_file():
    if "file" not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"message": "No selected file"}), 400

    filename = secure_filename(file.filename)

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    # 🔐 Get user from token
    token = request.headers["Authorization"]
    data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
    user_id = data["user_id"]

    # 💾 Save to DB
    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO files (user_id, filename) VALUES (%s, %s)",
        (user_id, filename)
    )
    mysql.connection.commit()
    cursor.close()

    return jsonify({
        "message": "File uploaded and saved",
        "filename": filename
    })

@app.route("/uploads/<filename>")
def get_uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/files", methods=["GET"])
@token_required
def get_files():
    token = request.headers["Authorization"]
    data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
    user_id = data["user_id"]

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM files WHERE user_id=%s", (user_id,))
    files = cursor.fetchall()
    cursor.close()

    file_list = []
    for f in files:
        file_list.append({
            "id": f[0],
            "filename": f[2],
            "uploaded_at": str(f[3])
        })

    return jsonify(file_list)

@app.route("/delete/<int:file_id>", methods=["DELETE"])
@token_required
def delete_file(file_id):
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT filename FROM files WHERE id=%s", (file_id,))
    file = cursor.fetchone()

    if not file:
        return jsonify({"message": "File not found"}), 404

    filename = file[0]

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if os.path.exists(filepath):
        os.remove(filepath)

    cursor.execute("DELETE FROM files WHERE id=%s", (file_id,))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": "File deleted successfully"})

if __name__ == "__main__":
    app.run(debug=True)