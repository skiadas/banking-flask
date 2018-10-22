from flask import Flask, make_response, json, url_for
from db import Db   # See db.py

app = Flask(__name__)
db = Db()






## Helper method for creating JSON responses
def make_json_response(content, response = 200, headers = {}):
   headers['Content-Type'] = 'application/json'
   return make_response(json.dumps(content), response, headers)

# Starts the application
if __name__ == "__main__":
   app.run()
