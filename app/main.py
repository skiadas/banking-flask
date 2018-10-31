from flask import Flask, request, make_response, json, url_for, abort
from db import Db   # See db.py

app = Flask(__name__)
db = Db()
app.debug = True # Comment out when not testing

@app.errorhandler(500)
def server_error(e):
   return make_json_response({ 'error': 'unexpected server error' }, 500)

@app.errorhandler(404)
def not_found(e):
   return make_json_response({ 'error': e.description }, 404)

@app.errorhandler(403)
def forbidden(e):
   return make_json_response({ 'error': e.description }, 403)

@app.errorhandler(400)
def client_error(e):
   return make_json_response({ 'error': e.description }, 400)


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
   password = getPasswordFromContents()
   checkAlphanum(username, password)
   checkNameAvailable(username)
   db.addUser(username, password)
   db.commit()
   headers = { "Location": url_for('user_profile', username=username) }
   return make_json_response({ 'ok': 'user created' }, 201, headers)

@app.route('/user/<username>', methods = ['GET'])
def user_profile(username):
   password = getPasswordFromQuery()
   user = getUserAndCheckPassword(username, password)
   return make_json_response({
      "username": user.username,
      "balance": user.balance,
      "transactions": {
         "link": url_for('transaction_list', user=user.username)
      }
   })

@app.route('/user', methods = ['GET'])
def user_list():
   users = db.getUsers()
   return make_json_response({
      "users": [
         { "username": user.username,
           "link": url_for('user_profile', username=user.username) }
         for user in users
      ]
   })

@app.route('/user/<username>', methods = ['POST'])
def user_update(username):
   oldpassword = getPasswordFromQuery()
   newpassword = getPasswordFromContents()
   checkAlphanum(username, oldpassword, newpassword)
   user = getUserAndCheckPassword(username, oldpassword)
   user.password = newpassword
   db.commit()
   return make_json_response({}, 204)

@app.route('/user/<username>', methods = ['DELETE'])
def user_delete(username):
   password = getPasswordFromQuery()
   checkAlphanum(username, password)
   user = getUserAndCheckPassword(username, password)
   db.session.delete(user)
   db.commit()
   return make_json_response({}, 204)

@app.route('/transaction', methods = ['GET'])
def transaction_list():
   contents = request.get_json()


@app.route('/transaction', methods = ['POST'])
def transaction_create():
   pass

@app.route('/transaction/<transactionId>', methods = ['GET'])
def transaction_info(transactionId):
   pass


## Helper method for creating JSON responses
def make_json_response(content, response = 200, headers = {}):
   headers['Content-Type'] = 'application/json'
   return make_response(json.dumps(content), response, headers)

def getPasswordFromQuery():
   if "password" not in request.args:
      abort(400, 'must provide a password parameter')
   return request.args["password"]

def getPasswordFromContents():
   contents = request.get_json()
   if "password" not in contents:
      abort(400, 'must provide a password field')
   return contents["password"]

def checkAlphanum(*args):
   for arg in args:
      if not arg.isalnum():
         abort(400, 'username and password must be alphanumeric')

def getUserAndCheckPassword(username, password):
   user = db.getUser(username)
   if user is None:
      abort(404, 'unknown username')
   if user.password != password:
      abort(400, 'incorrect password')
   return user

def checkNameAvailable(username):
   user = db.getUser(username)
   if user is not None:
      abort(403, 'username already exists')

# Starts the application
if __name__ == "__main__":
   app.run()
