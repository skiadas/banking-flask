from main import app, db

app.config['TESTING'] = True
client = app.test_client()
r = client.get("/")
assert(r.status_code == 200)
assert("users" in r.json and "link" in r.json["users"])
usersLink = r.json["users"]["link"]
assert("transactions" in r.json and "link" in r.json["transactions"])
transactionsLink = r.json["transactions"]["link"]
r = client.get(usersLink)
assert(r.status_code == 200)
assert("users" in r.json)
assert(len(r.json["users"]) == 0)
r = client.put("/user/sam23", json={ "password": "iamsam" })
assert(r.status_code == 201)
r = client.get(usersLink)
assert(r.status_code == 200)
assert("users" in r.json)
assert(len(r.json["users"]) == 1)
assert("username" in r.json["users"][0] and r.json["users"][0]["username"] == "sam23")
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
r = client.post("/user/sam23?password=iamsam", json={ "password": "ibesam" })
assert(r.status_code == 204)
r = client.get("/user/sam23?password=ibesam")  # the correct password now
assert(r.status_code == 200)
r = client.delete("/user/sam23?password=ibesam")
assert(r.status_code == 204)
client.put("/user/pete", json={ "password": "peteishere" })
# r = client.post("/transaction", json={ "type": "Deposit", "amount": 30 , "username": "pete" })
# assert(r.status_code == 201)
