# Resources

Here we discuss the specific resources that we will support, and their respective format. We will start with a high level overview:

- **Users**. Our first resource would be the list of all users.
    - Its URI scheme is simply `/user`.
    - A GET request would return the list of all the bank's users.
    - No other operations are allowed.
- **Single User**. Our second resource is an individual user.
    - Its URI scheme is `/user/{username}`. For example my username URI would be `/user/skiadas`.
    - A GET request would return an account summary for the user. It can only succeed if the correct password is provided as a parameter.
    - A PUT request can be used to create a new account. A password would need to be provided, and an error would be thrown if the account already exists.
    - A DELETE request can be used to delete a user from the system. It can only succeed if the correct password is provided as a parameter.
    - A POST request can be used to change the user's password. Both the old and the new password must be provided.
- **Transactions**. The list of all transactions in the system.
    - Its URI scheme is simply `/transaction`.
    - A GET request provides a list of transactions. A number of filter parameters and sorting parameters may be provided.
    - A POST request can be used to create a new transaction. The type of the transaction, along with corresponding amounts and possible password if needed, must be provided.
    - No other operations are allowed.
- **A specific transaction**.
    - Its URI scheme is simply `/transaction/{transactionId}` where the transactionId is a randomly generated unique ID string identifying this transaction.
    - A GET request provides details about the transaction, namely its type, the sender and/or receiver, amount and date/time.
    - No other operations are allowed.

So in summary here are all the methods we'll need to implement:

- `GET /user`
- `POST /user`
- `GET /user/{username}`
- `PUT /user/{username}`
- `POST /user/{username}`
- `DELETE /user/{username}`
- `GET /transaction`
- `POST /transaction`
- `GET /transaction/{transactionId}`

## Details

We need to now discuss details for each transaction, describing expected inputs, format of outputs etc.

### `GET /user`

Returns the list of users in alphabetical order, in JSON format. More specifically, the output will look like this:
```json
{
    "users": [
        { "username": "skiadas", "link": "/user/skiadas" },
        ...
    ]
}
```
It will always return a 200 OK unless there were problems accessing the database.

### `GET /user/{username}`

Returns information for a particular user. It expects a `password` query parameter to be provided, and it must match the password stored for that user.

- If the username is not a valid username, return 404 Not Found.
- If the password is not provided or does not match the user info, return 403 Forbidden (If we were using a more standard HTTP authentication scheme, a 401 response might be more appropriate).
- Otherwise, the user's balance information is provided, along with a link to the query to the user's transactions. The format would be as follows:

    ```json
    {
        "username": "skiadas",
        "balance": 453,
        "transactions": {
            "link": "/transaction?user=skiadas" }
        }
    }
    ```

### `PUT /user/{username}`

Used to create a new user. The server response is similar to that for `POST /user`.

Expected payload:
```json
{
    "password": "somethingcool"
}
```

 - If the username already exists, return 403 Forbidden.
 - If the payload does not contain a password, return 400 Bad Request.
 - If the username is not consisting of only alphanumeric symbols, return 400 Bad Request.
 - A successful user creation will return a response code 201 Created.

### `POST /user/{username}`

Used to change a user's password. The expected payload must have the form:
```json
{
    "password": "somethingcool",
    "new_password": "somethingEvenCooler"
}
```

- If the username does not exist, return 404 Not Found.
- If the password is not provided or does not match the user info, return 403 Forbidden.
- If no new_password entry is present, return 400 Bad Request.
- Otherwise, change the users password and return 204 No Content.

### `DELETE /user/{username}`

Used to delete a user account. This does not delete any transactions that are stored for that user. The expected payload must include a password entry:
```json
{
    "password": "somethingcool"
}
```

- If the username does not exist, return 404 Not Found.
- If the password is not provided or does not match the user info, return 403 Forbidden.
- Otherwise, "delete" the user account and return 204 No Content.

### `GET /transaction`

Returns a list of all transactions in the system. Allows for filtering and shorting options:

- Can provide a `user=...` parameter to restrict the transactions to those involving a particular user as either the "sender" or the "recipient".
- Can provide `from=...` or `to=...` parameters that specify start and end dates to consider.
- Can provide an `order=...` parameter that specifies the order in which transactions are to appear. Possible values are `amount`, `type`, or `date`, with `date` being the default.

The return format looks as follows:
```json
{
    transactions: [
        {
            "transactionId": "Grfe42greTY6",
            "link": "/transaction/Grfe42greTY6",
            "type": "Deposit",
            "user": "skiadas",
            "amount": 34,
            "datetime": "2018-10-04 04:23am"
        },
        {
            "transactionId": "TgEEF3ER2I6Q",
            "link": "/transaction/TgEEF3ER2I6Q",
            "type": "Transfer",
            "user": "pete",
            "recipient": "skiadas",
            "amount": 23,
            "datetime": "2018-10-03 03:12pm"
        },
        ...
    ]
}
```

### `POST /transaction`

Used to create a new transaction. Payload is as follows:
```json
{
    "type": "Deposit or Transfer or Withdrawal",
    "user": "skiadas",
    "recipient": "only needed for transfers",
    "amount": 23,
    "password": "must match the user's password"
}
```

- If the `type`, `user`, `amount` or `password` fields are not present, return a 400 Bad Request.
- If the `type` field is not one of the three possible words, return a 400 Bad Response.
- If the `type` is `Transfer` but there is no `recipient` field, return a 400 Bad Response.
- If the `user` is not a valid account, or the recipient is not a valid account, or the amount is not a non-negative number, return 400 Bad Response.
- If the `password` does not match the user's password, return 403 Forbidden.
- If the user's account does not have enough funds for a Transfer or Withdrawal, return 400 Bad Request.
- Otherwise, create a new transaction entry, and return 201 Created, along with a suitable `Location` header.

### `GET /transaction/{transactionId}`

Retrieves information for a specific transaction.

- If the `transactionId` is not that of a valid transaction, return 404 Not Found.
- Otherwise, return 200 OK with the contents of the transaction as in the example that follows. The response should include an `Expires` header set to one year into the future.

```json
{
    "transactionId": "TgEEF3ER2I6Q",
    "link": "/transaction/TgEEF3ER2I6Q",
    "type": "Transfer",
    "user": "pete",
    "recipient": "skiadas",
    "amount": 23,
    "datetime": "2018-10-03 03:12pm"
}
```
