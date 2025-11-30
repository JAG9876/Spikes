from flask import Flask, request
from flask_cors import CORS
import requests
#import json

app = Flask(__name__)
CORS(app)  # Allow all

@app.route("/api/search")
def search():
    queryString = request.args.get('q')

    baseUrl = 'https://images-api.nasa.gov/search'
    payload = { 'q': queryString, 'media_type': 'image' }
    
    try:
        response = requests.get(url = baseUrl, params= payload)
        if response.ok:
            return {
                "errorMessage": "",
                "searchResponse": response.json()
            }
        return {
            "errorMessage": f"An error occured. Status code = {response.status_code}",
            "searchResponse": {}
        }
    except Exception as e:
        return {
            "errorMessage": f"An exception of type {type(e)} occured:\r\n{e}",
            "searchResponse": {}
        }



'''
def getFileResponse(filePath):
    response = errorMessage = ''

    try:
        with open(filePath, 'r', encoding = 'utf-8') as file:
            response = json.load(file)
    except FileNotFoundError:
        errorMessage = f'The file {filePath} was not found.'
    except:
        errorMessage = f'Something happened trying to read the file {filePath}'
    
    return response, errorMessage
'''

if __name__ == '__main__':
    app.run(debug=True)