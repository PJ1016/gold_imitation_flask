from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
import os

app = Flask(__name__)

# Get Mongo URI from environment variables
app.config["MONGO_URI"] = os.getenv("MONGO_URI")

# Initialize PyMongo
mongo = PyMongo(app)

# Define a test route
@app.route("/add", methods=["POST"])
def add_user():
    data = request.json
    mongo.db.users.insert_one(data)
    return jsonify({"message": "User added successfully!"}), 201

@app.route("/", methods=["GET"])
def get_users():
    print(app.config)
    users = list(mongo.db.users.find({}, {"_id": 0}))
    return jsonify(users)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
