import boto3
import jwt
import datetime
from functools import wraps
from flask_cors import CORS
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import bcrypt
import os
from werkzeug.utils import secure_filename
import uuid
from botocore.client import Config
from dotenv import load_dotenv
import urllib.parse

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# 🔐 Secret key
app.config["SECRET_KEY"] = "your_secret_key"

# 🗄️ MySQL config
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "1234"
app.config["MYSQL_DB"] = "drive_app"

mysql = MySQL(app)

# ☁️ S3 CONFIG
S3_BUCKET = os.getenv("AWS_BUCKET")

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
    region_name=os.getenv("AWS_REGION"),
    config=Config(
        signature_version="s3v4",
        s3={"addressing_style": "virtual"}
    )
)


@app.route("/")
def home():
    return "Backend running 🚀"


# 🔐 Register
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


# 🔑 Login
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
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"message": "Token is missing"}), 401

        try:
            jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        except:
            return jsonify({"message": "Token is invalid"}), 401

        return f(*args, **kwargs)

    return decorated


# 🔒 Protected route
@app.route("/protected", methods=["GET"])
@token_required
def protected():
    return jsonify({"message": "Protected route accessed"})


# ☁️ Upload file
@app.route("/upload", methods=["POST"])
@token_required
def upload_file():
    if "file" not in request.files:
        return jsonify({"message": "No file provided"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"message": "No selected file"}), 400

    filename = str(uuid.uuid4()) + "_" + secure_filename(file.filename)

    s3.upload_fileobj(file, S3_BUCKET, filename)

    token = request.headers.get("Authorization")
    data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
    user_id = data["user_id"]

    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO files (user_id, filename) VALUES (%s, %s)",
        (user_id, filename)
    )
    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": "File uploaded", "filename": filename})


# 🔐 Secure download
@app.route("/download/<filename>", methods=["GET"])
@token_required
def download_file(filename):
    safe_filename = urllib.parse.unquote(filename)

    url = s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": S3_BUCKET,
            "Key": safe_filename
        },
        ExpiresIn=300
    )

    return jsonify({"url": url})


# 📂 Get files
@app.route("/files", methods=["GET"])
@token_required
def get_files():
    token = request.headers.get("Authorization")
    data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
    user_id = data["user_id"]

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM files WHERE user_id=%s", (user_id,))
    files = cursor.fetchall()
    cursor.close()

    return jsonify([
        {
            "id": f[0],
            "filename": f[2],
            "uploaded_at": str(f[3])
        } for f in files
    ])


# ❌ Delete file
@app.route("/delete/<int:file_id>", methods=["DELETE"])
@token_required
def delete_file(file_id):
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT filename FROM files WHERE id=%s", (file_id,))
    file = cursor.fetchone()

    if not file:
        return jsonify({"message": "File not found"}), 404

    filename = file[0]

    s3.delete_object(Bucket=S3_BUCKET, Key=filename)

    cursor.execute("DELETE FROM files WHERE id=%s", (file_id,))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": "File deleted"})


if __name__ == "__main__":
    app.run(debug=True)