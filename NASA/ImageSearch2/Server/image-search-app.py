from flask import Flask
from flask_cors import CORS
#from flask_cors import cross_origin
import json

app = Flask(__name__)
CORS(app)  # Allow all
#CORS(app, resources = {r"/api/*": { "origins": "http://localhost:5000"}})

@app.route("/")
#@cross_origin()
def hello_world():
    return 'Hello World!'

@app.route("/api/search")
#@cross_origin()
def search():
    filePath = 'searchResponseMoon.json'
    try:
        with open(filePath, 'r', encoding = 'utf-8') as file:
            response = json.load(file)
            return response
    except FileNotFoundError:
        print(f'The file {filePath} was not found.')
    except:
        print(f'Something happened trying to read the file {filePath}')

if __name__ == '__main__':
    app.run(debug=True)