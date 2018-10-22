# Overview

The banking-flask app offers a very simple banking system:

- Users can create accounts by providing a username and password.
- Users can "deposit" funds into their accounts, or can "withdraw" funds from their accounts, provided they have enough.
- Users can "transfer" funds from their account to someone else's.
- Records of all transactions are being kept by the "bank" and can be provided upon requests.
- Users can at any point inspect their balance as well as their past transactions.

We should make sure that users cannot have funds taken out of their account, or their account details being viewed, unless their password is provided.

For simplicity, all fund amounts are considered to be integers.
