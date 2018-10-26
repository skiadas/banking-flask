import requests
from main import app, db

app.config['TESTING'] = True
client = app.test_client()
r = client.put("/user/sam23", json={ "password": "iamsam" })
assert(r.status_code == 201)
r = client.put("/user/sam23", json={ "password": "ibesam" })
assert(r.status_code == 403)
r = client.put("/user/sam2", json={})
assert(r.status_code == 400)
r = client.put("/user/sam2@@", json={ "password": "iamsam" })
assert(r.status_code == 400)

r = client.get("/user/sam23")   # No password
assert(r.status_code == 400)
r = client.get("/user/sam2?password=iamsam")  # Nonexistent user
assert(r.status_code == 404)
r = client.get("/user/sam23?password=ibesam")  # wrong password
assert(r.status_code == 400)
r = client.get("/user/sam23?password=iamsam")
assert(r.status_code == 200)
assert("balance" in r.json)
assert("username" in r.json)
assert("transactions" in r.json)
assert("link" in r.json["transactions"])
