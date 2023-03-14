import uuid
import re
import hashlib as h
from flask import Flask, redirect, request, render_template, session
from flask_sessionstore import Session
from flask_session_captcha import FlaskSessionCaptcha
from pymongo import MongoClient
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads\\'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mongoClient = MongoClient('localhost', 27017)

app.config["SECRET_KEY"] = uuid.uuid4()
app.config['CAPTCHA_ENABLE'] = True

app.config['CAPTCHA_LENGTH'] = 6

app.config['CAPTCHA_WIDTH'] = 160
app.config['CAPTCHA_HEIGHT'] = 60
app.config['SESSION_MONGODB'] = mongoClient
app.config['SESSION_TYPE'] = 'mongodb'
app.config["SESSION_PERMANENT"] = False

Session(app)

captcha = FlaskSessionCaptcha(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
	return render_template("index.html")

@app.route('/login')
def login(check= {
				'valid_Mail': True,
				'valid_Pass': True,
				# 'valid_user': True,
				'valid_Captcha': True
			}, msg= ''):
	return render_template("login.html", check=check, msg= msg)

@app.route('/signup')
def signup(check= {
				'valid_Mail': True,
				'mail_Duplicate': True,
				'valid_Pass': True,
				'match_Pass': True,
				'valid_Captcha': True
			}, msg= ''):
	return render_template("signup.html", check=check, msg= msg)

@app.route('/form', methods=['POST', 'GET'])
def form():

	db= mongoClient['userdata']

	collection= db['data']

	mail_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
	pass_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,20}$'

	if request.method== "POST":
		if request.form.get("page")== "Login":

			check= {
				'valid_Mail': True,
				'valid_Pass': True,
				# 'valid_user': True,
				'valid_Captcha': True
			}

			mail= request.form.get("mail").strip().replace(' ', '')
			password= request.form.get("password").strip().replace(' ', '')

			if not mail or not re.fullmatch(mail_regex, mail):
				check['valid_Mail']= False

			if not password or not re.fullmatch(pass_regex, password):
				check['valid_Pass']= False

			if not captcha.validate():
				check['valid_Captcha']= False

			if all([i for i in check.values()]):

				details= {
					'mail': '%s'%(mail),
					'pass': '%s'%(password)
				}

				if collection.count_documents(details):
					return render_template("file_upload.html", msg= 'Logged in Successfully')
				else:
					return render_template("login.html", check= check, msg= 'User does not exist')

			else:
				return render_template("login.html", check= check, msg= 'Try Again')

		elif request.form.get("page")== "Signup":

			check= {
				'valid_Mail': True,
				'mail_Duplicate': True,
				'valid_Pass': True,
				'match_Pass': True,
				'valid_Captcha': True
			}

			mail= request.form.get("mail").strip().replace(' ', '')
			password= request.form.get("password").strip().replace(' ', '')
			conf_pass= request.form.get("conf_pass").strip().replace(' ', '')

			if not mail or not re.fullmatch(mail_regex, mail):
				check['valid_Mail']= False

			if collection.count_documents({'mail':'%s'%(mail)}):
				check['mail_Duplicate']= False

			if not password or not re.fullmatch(pass_regex, password) or not re.fullmatch(pass_regex, conf_pass):
				check['valid_Pass']= False

			if password!= conf_pass:
				check['match_Pass']= False

			if not captcha.validate():
				check['valid_Captcha']= False

			if all([i for i in check.values()]):

				details= {
					'mail': '%s'%(mail),
					'pass': '%s'%(password),
					'attempts': '%d'%(3)
				}

				if collection.insert_one(details):
					return render_template("file_upload.html", msg= 'User Created Successfully')
				else:
					return render_template("signup.html", check= check, msg= 'Failed to create user. Try Again')

			else:
				return render_template("signup.html", check= check, msg= 'Try Again')

@app.route('/admin')
def admin():
	return render_template("admin.html")

@app.route('/admin_login', methods=['POST', 'GET'])
def admin_panel():
	return "Admin Page"


if __name__ == "__main__":
	app.run(debug=True)
