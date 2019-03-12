from flask import Flask,render_template,request, session, url_for, escape, redirect, abort, make_response
import key
import json
import string
import random
from werkzeug.utils import secure_filename
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

@app.route('/request')
def send_loc():
	gmaps = googlemaps.Client(key=api_key)
	loc = gmaps.geolocate()
	pre_lat = loc["location"]["lat"]
	pre_lng = loc["location"]["lng"]
	un_id = id_generator()
	return render_template("request.html", pre_lat=pre_lat, pre_lng=pre_lng, un_id=un_id)

@app.route('/requestsent', methods=["POST"])
def loc_received():
	pre_lat = request.form["getlat"]
	pre_lng = request.form["getlng"]
	file = request.files['file']
	un_id = request.form["unid"]
	user = session["mobile"]
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], un_id+".jpg"))

	sent_data = csvData.write_data(un_id, pre_lat, pre_lng, user)
	otp_gen.new_request(user, un_id)
	return render_template("datasent.html", un_id = un_id)

@app.route('/login')
def log_in():
	if 'userid' in session:
		session['login'] = "signed_in"
		# return redirect(url_for('geoloc'))
	return render_template("login.html")

@app.route('/register')
def register():
	if 'login' in session:
		return redirect(url_for('dashboard'))
	return render_template('register.html')

@app.route('/otpconfirm', methods=["POST"])
def otpconfirm():
	session["userid"] = request.form["userid"]
	session["mobile"] = request.form["mobile"]
	session["password"] = request.form["user_pass"]
	userExist = pyBot.check_id(session["userid"], session["mobile"])
	if userExist == None:
		otp = otp_generator()
		session["otp"] = otp
		try:
			otp_gen.sendsms(session["mobile"], otp)
			return render_template("otpsent.html")
		except:
			return render_template("registration_error.html")
	else:
		return render_template("sameuser.html")

@app.route('/registrationconfirm', methods=["POST"])
def registration():
	if request.form["user_otp"] == session["otp"]:
		session.pop('otp', None)
		userid = session["userid"]
		mobile = session["mobile"]
		password = session["password"]
		try:
			pyBot.register_user(userid, mobile, password)
			session.pop('mobile', None)
			session.pop('userid', None)
			session.pop('password', None)
			return render_template("success.html")
		except:
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
		session['userid'] = uid
		session['login'] = "signed_in"
		return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
	session.pop('mobile', None)
	session.pop('userid', None)
	session.pop('login', None)
	return redirect(url_for('log_in'))
		
@app.route('/dashboard', methods=["GET"])
def dashboard():
	if 'login' in session:
		return render_template('dashboard.html')
	else:
		return redirect(url_for('log_in'))

@app.route('/closedrequests', methods=["GET"])
def closedrequests():
	if session["usertype"] != "admin":
		abort(404)
	else:
		get_locations = csvData.closed_data("csv")
		img_path = []
		for loc in get_locations:
			loc_file = loc[0]+".jpg"
			for files in os.walk(req_image):
				if loc_file in files[2]:
					path = os.path.join(req_image, loc_file)
					img_path.append(path)

		return render_template('closedrequests.html', img_path=img_path, locations=get_locations)
	return make_response("Connected", 200)

@app.route('/closerequest', methods=["POST"])
def closerequest():
	unique_id = request.form["un_id"]
	return render_template("close.html", unique_id=unique_id)

@app.route('/closed', methods=["POST"])
def closed():
	unique_id = request.form["un_id"]
	csvData.change_value(unique_id)
	return redirect("/dashboard")

if __name__=='__main__':
	app.run(debug=True, host="127.0.0.1", port="8080")
