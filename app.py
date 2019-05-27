import cloudinary
from cloudinary import uploader
from flask import Flask, url_for, render_template, request, jsonify
from flask_pymongo import MongoClient
from dotenv import load_dotenv
import datetime
import config
from bson import objectid

# flask initialization
app = Flask(__name__)

# cloudinary configuration
cloudinary.config(
    cloud_name=config.CLOUD_NAME,
    api_key=config.API_KEY,
    api_secret=config.API_SECRET
)

# Mongo initialization
try:
    client = MongoClient(config.MONGO_URI)
    db = client.todos
    print("connected to database successfully")

except Exception as err:
    print("could not connect to database due to ", err)

# function to upload to cloudinary


def uploader(file):
    result = cloudinary.uploader.upload(file)
    return result["secure_url"]

# home page route


@app.route('/')
def home():
    return "<h3>Welcome to todo-cloud app. </h3>"


# api routes
@app.route("/api/addTodo", methods=["POST"])
def index():
    # connect to the database
    try:
        todo = db.todos
        print("connected to the collection")
    except Exception as err:
        print("could not connect to collection due to ", err)

    # Todo :
    file = request.json["image"]

    # todo item from json
    todo_item = {
        "Name": request.json["name"],
        "Completed": False,
        "Created": datetime.datetime.now(),
        "Image": uploader(file)
    }

    try:
        todo.insert_one(todo_item)

        return jsonify({"Message": "todo item posted to the database"})
    except Exception as err:
        print("could not post the item to the database due to ", err)


# gettiing todos
@app.route("/api/getTodo", methods=["GET"])
def getTodo():
    # connect to db
    try:
        todo = db.todos
        todos = []
        for to in todo.find():
            todos.append({
                "image": to["Image"],
                "name": to["Name"],
                "completed": to["Completed"],
                "created": to["Created"]
            })

            todo_length = len(todos)

        print("connected to the db")

    except Exception as err:
        print("connection failed")

    return render_template('index.html', todos=todos, numTodos=todo_length)


if __name__ == "__main__":
    app.run(debug=True, port=5500)
