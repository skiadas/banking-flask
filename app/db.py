# Sets up database
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime, timedelta
from json import dumps
from hashlib import md5
from utils import getName

date_format = "%Y-%m-%d %H:%M:%S"

class InsufficientFunds(Exception):
    pass

Base = declarative_base()

class Transaction(Base):
   __tablename__ = 'transactions'

   txId = Column(String(36), primary_key=True)
   txType = Column(String)
   username = Column(String, ForeignKey('users.username', ondelete="SET NULL"), nullable=True)
   recipientname = Column(String, ForeignKey('users.username', ondelete="SET NULL"), nullable=True)
   amount = Column(Integer, nullable=False)
   date = Column(DateTime, nullable=False)

   user = relationship('User', back_populates='transactions', foreign_keys=[username])
   recipient = relationship('User', foreign_keys=[recipientname])

   def __init__(self, txType, amount, user, recipient=None):
      self.txType = txType
      self.amount = amount
      self.user = user
      self.recipient = recipient
      self.date = datetime.now()
      self.txId = self.generateHash()

   def isPossible(self):
      if self.txType == "Withdrawal" or self.txType == "Transfer":
         return self.user.balance >= self.amount
      return True

   def performTransaction(self):
      if self.txType == "Deposit":
         self.user.balance += self.amount
      elif self.txType == "Withdrawal":
         self.user.balance -= self.amount
      else:
         self.user.balance -= self.amount
         self.recipient.balance += self.amount

   def toJSON(self):
      return {
         "txId": self.txId,
         "txType": self.txType,
         "amount": self.amount,
         "username": getName(self.user),
         "recipientname": getName(self.recipient),
         "date": self.date.strftime(date_format)
      }

   def generateHash(self):
      jsonString = dumps(self.toJSON())
      return md5(jsonString.encode('utf-8')).hexdigest()

   def __repr__(self):
      if self.txType == "Deposit":
         return "<Tx %s: Deposit $%d to %s>" %\
           (self.txId or "", self.amount, getName(self.user, default="<deleted>"))
      elif self.txType == "Withdrawal":
         return "<Tx %s: Withdraw $%d from %s>" %\
            (self.txId or "", self.amount, getName(self.user, default="<deleted>"))
      else:
         return "<Tx %s: Transfer $%d from %s to %s>" %\
            (self.txId or "", self.amount,
               getName(self.user, default="<deleted>"),
               getName(self.recipient, default="<deleted>"))

class User(Base):
   __tablename__ = 'users'

   username = Column(String, primary_key=True)
   password = Column(String, nullable=False)
   balance = Column(Integer, nullable=False, default=0)

   transactions = relationship('Transaction', back_populates='user', foreign_keys=[Transaction.username])

   def __repr__(self):
      return "<User: %s ($%d)>" % (self.username, self.balance)

# Represents the database and our interaction with it
class Db:
   def __init__(self):
      engineName = 'sqlite:///test.db'   # Uses in-memory database
      self.engine = create_engine(engineName)
      self.metadata = Base.metadata
      self.metadata.bind = self.engine
      self.metadata.drop_all(bind=self.engine)
      self.metadata.create_all(bind=self.engine)
      Session = sessionmaker(bind=self.engine)
      self.session = Session()

   def commit(self):
      self.session.commit()

   def rollback(self):
      self.session.rollback()

   def addUser(self, username, password):
      user = User(username=username, password=password, balance=0)
      self.session.add(user)
      return user

   def getUser(self, username):
      return self.session.query(User)\
                 .filter_by(username=username)\
                 .one_or_none()

   def deleteUser(self, user):
      self.session.delete(user)
      self.deleteNullTransactions()

   def addTransaction(self, txType, amount, user, recipient=None):
      tx = Transaction(txType = txType, amount = amount,
                       user = user, recipient = recipient)
      if not tx.isPossible():
         raise InsufficientFunds()
      self.session.add(tx)
      tx.performTransaction()
      return tx

   def getTransaction(self, txId):
      return self.session.query(Transaction)\
                 .filter_by(txId=txId).one_or_none()

   def deleteNullTransactions(self):
      self.session.query(Transaction).filter_by(
         user=None,
         recipient=None
      ).delete()

   def getTransactions(self, params = None):
      query = self.session.query(Transaction)
      query = enrichQuery(query, params)
      return query.all()

# Helpers
def enrichQuery(query, params):
   if params is None:
      return query
   if "user" in params:
      username = params["user"]
      query = query.filter(
         or_(Transaction.username==username,
            Transaction.recipientname==username))
   if "from" in params:
      date = datetime.strptime(params["from"], date_format)
      query = query.filter(Transaction.date >= date)
   if "to" in params:
      date = datetime.strptime(params["to"], date_format)
      query = query.filter(Transaction.date <= date)
   order = params["order"] if "order" in params else "date"
   if order == "date":
      # Won't work properly in SQLite but will in other DBs
      query = query.order_by(Transaction.date.desc())
   elif order == "amount":
      query = query.order_by(Transaction.amount.desc())
   elif order == "type":
      query = query.order_by(Transaction.txType)
   return query

# Testing
if __name__ == "__main__":
   # Example usage
   db = Db()
   session = db.session
   john1 = db.addUser(username="John65", password="Doe")
   john2 = db.getUser(username="John65")
   john3 = db.getUser(username="John63")
   assert(john1 is not None)
   assert(john1 is john2)
   assert(john3 is None)
   tx1 = db.addTransaction("Deposit", 25, john1)
   assert(tx1 is not None)
   try:
      tx2 = db.addTransaction("Withdrawal", 30, john1)
      assert(False)
   except InsufficientFunds as e:
      assert(True)
   db.commit()
   db.deleteUser(john1)
   assert(tx1.user is None)
   txs = db.getTransactions()
   assert(len(txs) == 0)
   db.commit()
   users = [ db.addUser(username="Peter%d" % i, password="Duh%d" %  i) for i in range(0,10)]
   transactions = [db.addTransaction("Deposit", 30, user) for user in users]
   txTransfer = db.addTransaction("Transfer", 10, users[0], users[1])
   tx0 = transactions[0].date = datetime.now() - timedelta(hours=5)
   anHourAgo = datetime.now() - timedelta(hours=1)
   txs = db.getTransactions()
   assert(len(txs) == 11)
   txs = db.getTransactions({ "from": anHourAgo.strftime(date_format) })
   assert(len(txs) == 10)
   txs = db.getTransactions({ "to": anHourAgo.strftime(date_format) })
   assert(len(txs) == 1)
   txs = db.getTransactions({ "user": users[0].username })
   assert(len(txs) == 2)
   txs = db.getTransactions({ "from": anHourAgo.strftime(date_format),
                               "user": users[0].username })
   assert(len(txs) == 1)
   txBig = db.addTransaction("Deposit", 50, users[5])
   txs = db.getTransactions({ "order": "amount" })
   assert(txs[0] == txBig)
