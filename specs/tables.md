# Database Tables

This page describes the database tables that are needed and how they should be set up. We mainly need two tables: `users` and `transactions`.

One important fact to consider is that we need our transactions to persist after one of their users has been deleted. The main consideration here is a transaction from a user account that has been deleted towards another user's account. We want to preverse these transactions unless both accounts are deleted.

We could take two approaches to this:

- Have a field that marks a user as "deleted", and never trully delete users, or transactions. We must take great care in this case when we generate queries to only show transactions where at least one of the users involved is active. We must also ensure that we are in fact legally allowed to maintain our user information after they have asked for it to be deleted, a delicate issue.
- We delete a user, and set NULL as the value for the user in the relevant transactions. We must then take extra care to delete those transactions that involve NULL users (i.e. a Transfer transaction with only one of the involved users still present must remain in the system).

We will opt for this second option.

Let's start with the `users` table:

- `username` should be a variable length character field. It should be not null, and be the primary key.
- `password` should be a variable length character field. It should be not null.
- `balance` should be an integer indicating the current account balance. It should be not null and default to 0.

Now the `transactions` table:

- `txId` will be a unique identifier for each transaction, that we will build by hashing the information in the transaction via an "MD5 Hash". It is not considered a very "safe" hashing mechanism, but it will do for our purposes. The corresponding hashes consist of 36 hexadecimal characters. Even though we could represent them in a more condensed form, we will simply store them as type CHAR(36) or TEXT depending on how the database handles the SQLAlchemy `String` type.
- `txType` is the transaction type, and it is going to be simply a string type where we will make sure to store one of the strings `"Deposit"`, `"Withdrawal"` or `"Transfer"`. We will rely on our Python code to enforce this constraint.
- `username` is the username that pertains to the transaction. In the case of the transfers it is the account that is the source of the funds. It will have to be allowed to be nullable in order to allow for our deletion of user entries. It will be set to be a foreign key referencing the username in the `user` table.
- `recipientname` is the username of the receiver/target of a transfer. It should be nullable as non-transfer transactions don't have a recipient. It should be a foreign key pointing to the username in the `user` table.
- `amount` is an integer representing the amount of the transaction. It should be not nullable.
- `datetime` should be a datetime object representing the time of creation of the transaction. We will be setting it manually as we want to use it to generate the `txId` hash.
