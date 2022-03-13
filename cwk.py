from flask import Flask,redirect, url_for, render_template,request,session
app = Flask(__name__)
from db_schema import db, User,Bill,latestAction,DBM,IPV
db.init_app(app)
def dbConfiguration():
        # prep the database file
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
    # required for the 'session' to work
    app.secret_key = 'any string you want'

# try setting up some data (within the app context)
with app.app_context():
    dbConfiguration()

    #dbinit()
    print("initialized DB by dbinit()")
@app.route("/user", methods=["POST","GET"])#default is get
def user():
    if request.method == 'POST':
            if request.form['submit_button'] == "1":
                print("Going to requestBill")
                return redirect(url_for("requestBill"))
            if request.form['submit_button'] == "2":
                return redirect(url_for("pay"))
            if request.form['submit_button'] == "3":
                return redirect(url_for("viewTrans"))

    else:#load register.html
        return render_template("user.html",current_user=session["username"])
@app.route("/requestBill", methods=["POST","GET"])#default is get
def requestBill():
    if request.method == 'POST':
        billTitle=request.form["billTitle"]
        amount=request.form["amount"]
        print("received bill Title :"+billTitle)
        print("total amount: "+amount)
        DBM.addBillForEveryone(session["username"],billTitle,amount)
        return redirect(url_for("user"))
    else:#load register.html
        return render_template("requestBill.html")
@app.route("/pay", methods=["POST","GET"])#default is get
def pay():
    if request.method == 'POST':
        billTitle=request.form["billTitle"]
        payTo=request.form["payTo"]
        current_user=session["username"]
        print(f"user: {current_user} paid for {billTitle} toward {payTo}")
        if (IPV.paymentInputCorrect(current_user,billTitle,payTo)):
            DBM.updateBillStatus(current_user,payTo,billTitle)
            #TODO: the message flash notify you have paid somebody with title
            print("bill status updated as completed")
        #DBM.addBillForEveryone(session["username"],billTitle,amount)
        return redirect(url_for("pay"))
    else:#load register.html

        return render_template("pay.html",user=session["username"],Bills=DBM.getBillsToBeMadeByUser(session["username"]))
@app.route("/viewTrans")
def viewTrans():

        return render_template("viewTransaction.html",Bills=DBM.getBillsToBePaidToUser(session["username"]))

@app.route("/register", methods=["POST","GET"])#default is get
def register():
    if request.method=="POST":#sending data from web to BE
        username=request.form["username"]
        email=request.form["email"]
        password=request.form["password"]
        DBM.addUserToDB(username,email,password)
        session["UsernameFromRegister"]=username
        return redirect(url_for("login"))

    else:#load register.html
        return render_template("register.html")

@app.route("/login", methods=["POST","GET"])#default is get
def login():
    session["username"]=""
    session["logged_in"]=False
    if request.method=="POST":
        email=request.form["email"]
        password=request.form["password"]
        correctPassword=DBM.checkPassword(email,password)
        if(correctPassword):
            session["logged_in"]=True
            #print("login successful")
            session["username"]=DBM.findUserByEmail(email)
            current_user=session["username"]
            print(f"current_user: {current_user}")
            #items=getUserListItem(username)#[item1.name,item2.name.....]
            return redirect(url_for("user"))
        else:
            print("email or password incorrect")
            return redirect(url_for("login"))

    else:
        return render_template("login.html")


@app.route("/resetDB")
def resetDB():
    DBM.resetDB()
    return redirect(url_for("viewDB"))
@app.route("/viewDB", methods=["POST","GET"])
def viewDB():
    return render_template("db.html",Users=User.query.all(),Bills=Bill.query.all(),latestAction=latestAction.query.all())
#route to the index
@app.route('/')
def index():

    return redirect(url_for("login"))
