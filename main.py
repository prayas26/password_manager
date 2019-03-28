from flask import Flask,render_template,request, session, url_for, escape, redirect, abort, make_response
import key
import json
import string
import random
from werkzeug.utils import secure_filename
import os
import db
import genpass
import otp_gen

pyBot = db.Database()

api_key = key.key

app=Flask(__name__)
app.secret_key = "smartBuddy"

def otp_generator(size=4, chars=string.digits):
    otp = ''.join(random.choice(chars) for _ in range(size))
    return otp

@app.route('/')
def index():
	return render_template("index.html")

@app.route('/login')
def log_in():
	if 'mobile' in session:
		session['login'] = "signed_in"
		return redirect(url_for('dashboard'))
	return render_template("login.html")

@app.route('/register')
def register():
	if 'login' in session:
		return redirect(url_for('index'))
	return render_template('register.html')


@app.route('/otpconfirm', methods=["POST"])
def otpconfirm():
	session["username"] = request.form["username"]
	session["mobile"] = request.form["userid"]
	session["password"] = request.form["user_pass"]
	checkUser = pyBot.checkUser(session["mobile"])
	if checkUser == None:
		otp = otp_generator()
		session["otp"] = otp
		try:
			otp_gen.sendsms(session["mobile"], otp)
			return render_template("otpsent.html")
		except:
			session.pop("mobile", None)
			session.pop("password", None)
			return render_template("registration_error.html")
	else:
		session.pop("mobile", None)
		session.pop("password", None)
		return render_template("userExists.html")

@app.route('/registrationconfirm', methods=["POST"])
def registration():
	if request.form["user_otp"] == session["otp"]:
		session.pop('otp', None)
		mobile = session["mobile"]
		password = session["password"]
		try:
			pyBot.register_user(mobile, password, session["username"])
			session.pop("username", None)
			session.pop('password', None)
			session.pop('mobile', None)
			session.pop('login', None)
			session.pop('otp', None)
			return render_template("success.html")
		except:
			session.pop('password', None)
			session.pop('mobile', None)
			session.pop('login', None)
			session.pop('otp', None)
			return render_template("registration_error.html")
	else:
		render_template("registration_error.html")

@app.route('/validate', methods=["POST"])
def validate():
	uid = request.form["userid"]
	upass = request.form["user_pass"]
	check_user = pyBot.con_auth(uid, upass)
	if check_user == None:
		return render_template("nouser.html")
	else:
		session['mobile'] = uid
		session['login'] = "signed_in"
		session['usertype'] = check_user['usertype']
		return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
	session.pop('mobile', None)
	session.pop('login', None)
	session.pop('usertype', None)
	return redirect(url_for('log_in'))
		
@app.route('/dashboard', methods=["GET"])
def dashboard():
	if 'login' in session:
		return render_template('dashboard.html')
	else:
		return redirect(url_for('log_in'))

if __name__=='__main__':
	app.run(debug=True, host="127.0.0.1")
