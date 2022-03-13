from flask_sqlalchemy import SQLAlchemy
import datetime
from sqlalchemy.inspection import inspect
db = SQLAlchemy()
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
# a model of a user for the database
class User(db.Model):
    __tablename__='user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(25))
    def __init__(self, username,email,password):
        self.username=username
        self.email=email
        self.password=password
class Bill(db.Model):
    __tablename__='bill'
    id = db.Column(db.Integer, primary_key=True)
    billName=db.Column(db.String(30))
    payBy = db.Column(db.String(20))
    payTo = db.Column(db.String(20))
    amount=db.Column(db.Float(2))
    status=db.Column(db.String(20))
    def __init__(self, billName, payBy,payTo,amount,status):
        self.billName=billName
        self.payBy=payBy
        self.payTo=payTo
        self.amount=amount
        self.status=status
class latestAction(db.Model):
    __tablename__='latestAction'
    id = db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(20))
    message=db.Column(db.String(50))
    def __init__(self, username,message):
        self.username=username
        self.message=message
class DBManipulator():
################################################################
    #login related
    def findUserByEmail(self,email):
        print(f"finding the username correspond to email {email}")
        return User.query.filter_by(email=email).first().username
################################################################
    #register related
    def addNewLatestAction(self,username):
        NewLatestAction=latestAction(username,"No action has to be taken")
        db.session.add(NewLatestAction)
        db.session.commit()
        return
    def encrypt(self,password):
        return generate_password_hash(password)
    def addUserToDB(self,username,email,password):
        #db.create_all()
        self.addNewLatestAction(username)
        encryptedPw=self.encrypt(password)
        newUser=User(username,email,encryptedPw)
        db.session.add(newUser)
        db.session.commit()
        print(f"New User: username: {username}, email:{email}, password: {password}, is added to User Table")

    def checkPassword(self,email,password):
        #
        userObj=User.query.filter_by(email=email).first()
        if not userObj is None:
            encryptedPw=userObj.password
            if (check_password_hash(encryptedPw,password)):
                return True
        return False
################################################################
    #Relates to bill(request/pay/view bills)
    def addBillForEveryone(self,payTo,billName,totalAmount):
        def getAllUsernames():
            allUsersNames=[]
            allUsers=User.query.all()
            for user in allUsers:
                if user.username==payTo:
                    continue
                allUsersNames.append(user.username)
            return allUsersNames
        allUsersNames=getAllUsernames()
        totalNumberOfUsers=len(allUsersNames)
        print(f"totalNumberOfUsers={totalNumberOfUsers}")
        amountOfOne=(float(totalAmount)/float(totalNumberOfUsers+1))
        print(f"bill amount of one person is {amountOfOne}")
        billList=[]
        for username in allUsersNames:
            #create new bill object
            if username=="payTo":
                continue
            newBill=Bill(billName,username,payTo,amountOfOne,"pending")
            billList.append(newBill)
        db.session.add_all(billList)
        db.session.commit()
        print("successfully add a bill for everybody ")
        print(f"bill Title {billName}")

        return

    def getBillsToBeMadeByUser(self,username):
        Bills=Bill.query.filter_by(payBy=username, status="pending")
        return Bills
    def getBillsToBePaidToUser(self,username):
        Bills=Bill.query.filter_by(payTo=username).all()
        return Bills
    def updateBillStatus(self,payBy,payTo,billName):
        #search for the corresponding bill object
        bill=Bill.query.filter_by(payBy=payBy,payTo=payTo,billName=billName).first()
        bill.status="completed"
        db.session.commit()
################################################################################
    #latestAction of user
    def getLatestActionOfUser(self,username):
        return latestAction.query.filter_by(username=username)
################################################################################
    #other methods
    def resetDB(self):
        db.drop_all()#remove __tablename__
        db.create_all()

class IPValidator():
    def paymentInputCorrect(self,current_user,billTitle,payTo):
        #search for the item if the item is not None then return True else False
            #if not ListsBelongsToUser is None:#check if there are some list for the user
        #search
        bill=Bill.query.filter_by(payBy=current_user,billName=billTitle,payTo=payTo).first()
        if not bill is None:
            print("payment input correct~!!!!!!")
            return True
        print("payment Input incorrect~!!!!")
        return False
IPV=IPValidator()
DBM=DBManipulator()
# def dbinit():
#     # check if the tables have already been created
#     tables = inspect(db.engine).get_table_names()
#     print(tables)
#     if len(tables) > 0:
#         return
#
#     # if not, then create them
#     db.create_all()
#     user_list = [
#         User("Andrew", "Andrew@gmail.com",security.generate_password_hash("heavy")),
#         User("Felicia","Felicia@gmail.com", security.generate_password_hash("people"))
#         ]
#     db.session.add_all(user_list)
#     db.session.commit()
