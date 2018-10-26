from flask import Flask, request, make_response, json, url_for
from db import Db   # See db.py

app = Flask(__name__)
db = Db()

@app.route('/', methods = ['GET'])
def index():
   return make_json_response({
      "users": { "link": url_for("user_list") },
      "transactions": { "link": url_for("transaction_list") }
   })


## Creates a new user. Request body contains the password to be used
## If user exists, must ensure it is same or else throw error
@app.route('/user/<username>', methods = ['PUT'])
def user_create(username):
   contents = request.get_json()
   if "password" not in contents:
      return make_json_response({ 'error': 'must provide a password field' }, 400)
   password = contents["password"]
   if not username.isalnum() or not password.isalnum():
      return make_json_response({ 'error': 'username and password must be alphanumeric' }, 400)
   try:
      user = db.getUser(username)
      if user is not None:
         return make_json_response({ 'error': 'username already exists' }, 403)
      db.addUser(username, password)
      db.commit()
      headers = { "Location": url_for('user_profile', username=username) }
      return make_json_response({ 'ok': 'user created' }, 201, headers)
   except:
      return make_json_response({ 'error': 'unexpected server error' }, 500)

@app.route('/user/<username>', methods = ['GET'])
def user_profile(username):
   query = request.args
   if "password" not in query:
      return make_json_response({ 'error': 'must provide a password parameter' }, 400)
   password = query["password"]
   try:
      user = db.getUser(username)
      if user is None:
         return make_json_response({ 'error': 'unknown username' }, 404)
      if user.password != password:
         return make_json_response({ 'error': 'incorrect password' }, 400)
      return make_json_response({
         "username": user.username,
         "balance": user.balance,
         "transactions": {
            "link": url_for('transaction_list', user=user.username)
         }
      })
   except:
      return make_json_response({ 'error': 'unexpected server error' }, 500)

@app.route('/user', methods = ['GET'])
def user_list():
   pass

@app.route('/user/<username>', methods = ['POST']):
def user_update(username):
   pass

@app.route('/user/<username>', methods = ['DELETE']):
def user_delete(username):
   pass

@app.route('/transaction', methods = ['GET']):
def transaction_list():
   pass

@app.route('/transaction', methods = ['POST']):
def transaction_create():
   pass

@app.route('/transaction/<transactionId>', methods = ['GET']):
def transaction_info(transactionId):
   pass


## Helper method for creating JSON responses
def make_json_response(content, response = 200, headers = {}):
   headers['Content-Type'] = 'application/json'
   return make_response(json.dumps(content), response, headers)

# Starts the application
if __name__ == "__main__":
   app.run()
