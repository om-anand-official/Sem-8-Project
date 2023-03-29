# Universally Unique Identifier lib for the creation of session and CAPTCHA
import os
import uuid 

# regex lib for regular expression check of input fields
import re 

# provides necessary hash for the security of input data
import bcrypt

# Framework used : FLASK
from flask import Flask, redirect, request, render_template, session

# create unique Sessions
from flask_sessionstore import Session

# create unique CAPTCHA for each session
from flask_session_captcha import FlaskSessionCaptcha

# connect MongoDB with Python
from pymongo import MongoClient

# added security for input files
from werkzeug.utils import secure_filename

# Keras for using the H5 model
from keras.models import Sequential
from keras.models import load_model
from keras.utils import np_utils

# Numpy to reshape and resize the pixel data of image
import numpy as np

# Computer Vision Library for object detection in image
import cv2

# Library for Pattern Matching
import glob

# PIL : Image porocessing library
from  PIL import Image 

# - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - -


# path to uploads folder where necessary files will be stored
UPLOAD_FOLDER = 'uploads\\'

# no other extensions allowed for uploaded file
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Flask Application Initialized
app = Flask(__name__)

# The Uploads Folder where the valid Images will be stored
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# MongoDB Client for connection
mongoClient = MongoClient('localhost', 27017)

# Key required for CAPTCHA
app.config["SECRET_KEY"] = uuid.uuid4()
app.config['CAPTCHA_ENABLE'] = True

# Count of Numbers in the CAPTCHA
app.config['CAPTCHA_LENGTH'] = 6

# CAPTCHA Image Dimensions
app.config['CAPTCHA_WIDTH'] = 160
app.config['CAPTCHA_HEIGHT'] = 60

# MongoDB Session Parameters used for generating CAPTCHA
app.config['SESSION_MONGODB'] = mongoClient
app.config['SESSION_TYPE'] = 'mongodb'
app.config["SESSION_PERMANENT"] = False

# Flask Session for creating CAPTCHA
Session(app)

# CAPTCHA created using Flask Session
captcha = FlaskSessionCaptcha(app)


# - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - -


# Function to check the validity of filename
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[-1].lower() in ALLOWED_EXTENSIONS

def model(image):
	global result, pothole_percent, size

	size = 300
	model = Sequential()
	model = load_model('full_model.h5')

	test = [cv2.imread(img, 0) for img in image]
	print(test)

	for i in range(len(test)):
		test[i] = cv2.resize(test[i], (size, size))

	X_temp = np.asarray(test)

	X_test = []
	X_test.extend(X_temp)
	X_test = np.asarray(X_test)
	X_test = X_test.reshape(X_test.shape[0], size, size, 1)

	Y_temp = np.zeros([X_temp.shape[0]], dtype = int)
	# Y_temp = np.ones([X_temp.shape[0]], dtype = int)

	Y_test = []
	Y_test.extend(Y_temp)
	Y_test = np.asarray(Y_test)
	Y_test = np_utils.to_categorical(Y_test)

	X_test =X_test/ 255

	tests = model.predict(X_test)

	for i in range(len(X_test)):
		print(">>> Predicted %d = %s" % (i, tests[i]))

	result = tests[i]
	pothole_percent = float("{0:.2f}".format(result[1] * 100))

	detect_result= 'Pothole Detected'

	print(result)
	if result[1] < 0.6: detect_result= 'No ' + detect_result

	return pothole_percent, detect_result


# - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - -


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
def form(file_check= {
			'valid_address': True,
			'valid_area': True,
			'valid_state': True,
			'valid_district': True,
			'valid_zip': True,
			'valid_file': True,
			'valid_Captcha': True
		}):

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
					'mail': '%s'%(mail)
				}

				user_exist= collection.count_documents(details)
				
				if user_exist:
					db_passwords= list(collection.find({"mail" : '%s'%(mail)}, {"pass": 1}))
					db_password= db_passwords[0]['pass']

					correct_pass= bcrypt.checkpw(password.encode(), db_password.encode())

					print(user_exist)
					print(password)
					print(db_password)
					print(correct_pass)

					if user_exist and correct_pass:
						return render_template("file_upload.html", msg= 'Logged in Successfully', check= file_check)
				else:
					return render_template("login.html", check= check, msg= 'User does not exist.')

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

			salt = bcrypt.gensalt()
			password= bcrypt.hashpw(password.encode(), salt)

			# password = hashlib.sha256(str.encode(password)).hexdigest()

			if not captcha.validate():
				check['valid_Captcha']= False

			if all([i for i in check.values()]):

				details= {
					'mail': '%s'%(mail),
					'pass': '%s'%(password.decode()),
					'attempts': '%d'%(3)
				}

				if collection.insert_one(details):
					return render_template("file_upload.html", msg= 'User Created Successfully', check= file_check)
				else:
					return render_template("signup.html", check= check, msg= 'Failed to create user. Try Again')

			else:
				return render_template("signup.html", check= check, msg= 'Try Again')
		
	else:
		return redirect('/login')

@app.route('/admin')
def admin():
	return render_template("admin.html")

@app.route('/admin_login', methods=['POST', 'GET'])
def admin_panel():
	return "Admin Page"

@app.route('/file_upload', methods=['POST', 'GET'])
def file_upload():
	if request.method == 'POST':

		check= {
			'valid_address': True,
			'valid_area': True,
			'valid_state': True,
			'valid_district': True,
			'valid_zip': True,
			'valid_file': True,
			'valid_Captcha': True
		}

		address= request.form.get('address').strip()
		area= request.form.get('area').strip()
		state= request.form.get('state').strip().replace(' ', '')
		district= request.form.get('district').strip().replace(' ', '')
		zipcode= request.form.get('zipcode').strip().replace(' ', '')

		file = request.files['road_img']
		file_name= file.filename

		pothole_percent, detect_result= 0, 0
		
		if allowed_file(file.filename):
			file_name= secure_filename(file.filename)

			file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
			
			path= os.path.join(app.config['UPLOAD_FOLDER'], file_name)
			pothole_percent, detect_result= model(glob.glob(path))
		else:
			check['valid_file']= False

		if not address: 
			check['valid_address']= False

		if not area:
			check['valid_area']= False
		
		STATES_LIST_INDIA = ['Gujarat', 'Maharashtra', 'Delhi']

		if not state or state not in STATES_LIST_INDIA:
			check['valid_state']= False

		if not district:
			check['valid_district']= False

		if not zipcode or zipcode.startswith('0'):
			check['valid_zip']= False

		if not captcha.validate():
			check['valid_Captcha']= False

		parameters= {
			'address': address,
			'area': area,
			'state': state,
			'district': district,
			'zipcode': zipcode,
			'file_name': file_name
		}

		results= {
			'pothole_percent': pothole_percent,
			'detect_result': detect_result
		}

		if all([i for i in check.values()]):
			return render_template("pothole_result.html", parameters=parameters, results= results)
		else:
			return render_template("file_upload.html", check= check, msg= '')
	return redirect('/login')


# - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - -


if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0')
