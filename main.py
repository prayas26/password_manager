from flask import Flask,render_template,request, session, url_for, escape, redirect, abort, make_response
import json
import string
import random
from werkzeug.utils import secure_filename
import os
import db
import genpass
import otp_gen
import encrypt

pyBot = db.Database()
getEncrypt = encrypt.Cipher()

app=Flask(__name__)
app.secret_key = "smartBuddy"

def otp_generator(size=4, chars=string.digits):
    otp = ''.join(random.choice(chars) for _ in range(size))
    return otp

@app.route('/')
def index():
	if 'login' in session:
		return redirect(url_for('dashboard'))
	else:
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
		return redirect(url_for('dashboard'))
	return render_template('register.html')


@app.route('/otpconfirm', methods=["POST"])
def otpconfirm():
	session["username"] = request.form["username"]
	session["mobile"] = request.form["mobile"]
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
			pyBot.createUserDB(mobile)
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

@app.route('/addpassword', methods=["GET"])
def addpassword():
	if 'login' in session:
		return render_template('addpassword.html')
	else:
		abort(404)

@app.route('/add', methods=["POST"])
def add():
	if 'login' in session:
		link = request.form["website"]
		userid = request.form["addUserID"]
		password = request.form["addUserPass"]
		newPassword = getEncrypt.encryptPassword(password)
		try:
			pyBot.addUserPassword(link, userid, newPassword, session["mobile"])
			return redirect(url_for('dashboard'))
		except:
			return render_template("error.html")

@app.route('/logout')
def logout():
	session.pop('mobile', None)
	session.pop('login', None)
	session.pop('usertype', None)
	return redirect(url_for('index'))
		
@app.route('/dashboard', methods=["GET"])
def dashboard():
	if 'login' in session:
		getPasswords = pyBot.getUserPassword(session["mobile"])
		return render_template('dashboard.html', getPasswords=getPasswords)
	else:
		return redirect(url_for('log_in'))

@app.route('/teams', methods=["GET"])
def teams():
	if 'login' in session:
		userTeams = pyBot.checkUserTeams(session["mobile"])
		return render_template('teams.html', userTeams=userTeams)
	else:
		return redirect(url_for('log_in'))

@app.route('/createTeam', methods=["POST"])
def createTeam():
	if 'login' in session:
		return render_template('createTeam.html')
	else:
		return redirect(url_for('log_in'))

@app.route('/create', methods=["POST"])
def create():
	if 'login' in session:
		team = request.form["teamName"]
		user1 = request.form["addUserID1"]
		user2 = request.form["addUserID2"]
		user3 = request.form["addUserID3"]
		checkUser1 = pyBot.checkUser(user1)
		checkUser2 = pyBot.checkUser(user2)
		checkUser3 = pyBot.checkUser(user3)
		if pyBot.checkTeam(team) == None:
			if checkUser1 == None:
				return render_template('notRegistered.html')
			elif checkUser2 == None and user2 != "":
				return render_template('notRegistered.html')
			elif checkUser3 == None and user3 != "":
				return render_template('notRegistered.html')
			elif user2 == "" and user3 == "":
				pyBot.addToTeam(team, session["mobile"], "admin")
				pyBot.addToTeam(team, user1, "user")
				pyBot.createTeamDB(team)
				return render_template('teamCreated.html')
			elif user2 == "":
				pyBot.addToTeam(team, session["mobile"], "admin")
				pyBot.addToTeam(team, user1, "user")
				pyBot.addToTeam(team, user3, "user")
				pyBot.createTeamDB(team)
				return render_template('teamCreated.html')
			elif user3 == "":
				pyBot.addToTeam(team, session["mobile"], "admin")
				pyBot.addToTeam(team, user1, "user")
				pyBot.addToTeam(team, user2, "user")
				pyBot.createTeamDB(team)
				return render_template('teamCreated.html')
		else:
			return render_template('teamExists.html', team=team)

@app.route('/teams/<teamName>', methods=["GET"])
def getTeam(teamName):
	if 'login' in session:
		check = pyBot.checkTeamAccess(session["mobile"], teamName)
		if check != None:
			checkTeam = pyBot.getTeamPassword(teamName)
			return render_template('showTeam.html', checkTeam=checkTeam, teamName=teamName, admin=check)
		else:
			return render_template('noTeamAccess.html')
	else:
		return redirect(url_for('log_in'))

@app.route('/delete/<teamName>', methods=["GET"])
def deleteTeam(teamName):
	if 'login' in session:
		check = pyBot.checkTeamAccess(session["mobile"], teamName)
		if check != None:
			isAdmin = check["userType"]
			if isAdmin == "admin":
				pyBot.deleteTeam(teamName)
				return render_template('delete.html')
			else:
				abort(404)
		else:
			abort(404)
	else:
		abort(404)

@app.route('/showPassword', methods=["POST"])
def showPassword():
	website = request.form["website"]
	username = request.form["username"]
	mobile = session["mobile"]
	getPass = pyBot.retrievePassword(mobile, website, username)
	getPass = getPass["userpass"]
	decryptPass = getEncrypt.decryptPassword(getPass)
	return render_template('showPassword.html', getPass=decryptPass)

@app.route('/addTeamPassword/<teamname>', methods=["POST"])
def addTeamPassword():
	if 'login' in session:
		return render_template('addteampassword.html')
	else:
		abort(404)


if __name__=='__main__':
	app.run(debug=True, host="127.0.0.1")
