import jwt
import datetime
from functools import wraps
from flask_cors import CORS
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import bcrypt

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

    # check if email exists
    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    if cursor.fetchone():
        cursor.close()
        return jsonify({"message": "Email already exists"}), 400

    # hash password
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # insert user
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

            # 🔐 Generate JWT
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

        # get token from headers
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


# 🔒 Protected route (TEST)
@app.route("/protected", methods=["GET"])
@token_required
def protected():
    return jsonify({"message": "You accessed a protected route"})


if __name__ == "__main__":
    app.run(debug=True)