from flask import *
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import pickle
import numpy as np
import sklearn
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
 
app = Flask(__name__)
app.secret_key = 'your secret key'
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root54567'
app.config['MYSQL_DB'] = 'login_users'
 
mysql = MySQL(app)

model = pickle.load(open('model.pkl','rb'))

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM loan_users WHERE userid = % s AND userpwd = % s', (username, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['userid'] 
            msg = 'Logged in successfully!'
            return render_template('predict.html', msg = msg)
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg = msg)
 
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('home'))
 
@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM loan_users WHERE userid = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO loan_users VALUES (NULL, % s, % s, % s)', (username, password, email, ))
            mysql.connection.commit()
            msg = 'You have registered successfully!'
            return render_template('login.html', msg = msg)
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg = msg)

@app.route("/predict", methods=['POST'])
def predict():
    if request.method == 'POST':
        Gender=int(request.form['Gender'])
        Married=int(request.form['Married'])
        Dependents=int(request.form['Dependents'])
        Education=int(request.form['Education'])
        Self_Employed=int(request.form['Self_Employed'])
        Income=float(request.form['Income'])
        Loan_Amount=float(request.form['Loan_Amount'])
        Loan_Term=int(request.form['Loan_Term'])
        Credit_History=int(request.form['Credit_History'])
        Property_Area=int(request.form['Property_Area'])
        
        prediction=model.predict([[Gender,Married,Dependents,Education,Self_Employed,Income,Loan_Amount,Loan_Term,Credit_History,Property_Area]])
        if prediction[0] >= 0.50:
            ptext="Congratulations. You are eligible for the Loan."
        else:
            ptext="Sorry. Your are not eligible for the loan."
        
        return render_template('predict.html',prediction_text=ptext) 
    
if __name__=='__main__':
    app.run(debug=True)
        