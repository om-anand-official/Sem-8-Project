# Universally Unique Identifier lib for the creation of session and CAPTCHA
import uuid 

# for managing the image paths
import os

# regex lib for regular expression check of input fields
import re 

# provides necessary hash for the security of input data
import bcrypt

# Framework used : FLASK
from flask import Flask, redirect, request, render_template, session
# Flask 			: Flask class used to create web app
# redirect 			: redirecting to specific url
# request 			: get the input from HTML fields
# render_template 	: load specified HTML page
# session 			: maintain session and session variables

# create unique Sessions
from flask_sessionstore import Session

# create unique CAPTCHA for each session
from flask_session_captcha import FlaskSessionCaptcha

# schedule the update of attempts everyday
from flask_apscheduler import APScheduler

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

# datetime to check whether the updates occur on time everday
# used for logging
from datetime import datetime as dt

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

# scheduler objects to schedule tasks

# scheduler object for updating upload count everyday at midnight
file_upload_attempt_update = APScheduler()

# scheduler object for reporting authorities
authority_report = APScheduler()

# - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - -


# Function to check the validity of filename
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[-1].lower() in ALLOWED_EXTENSIONS


# Machine Learning Model for Pothole Detection
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


# Function to update attempts everyday at
def update_attempts():
	# the database that stores user data
	db = mongoClient['userdata']

	# collection that stores user data
	collection = db['data']

	# the update query that updates the attempts
	# count to 3 everyday
	if collection.update_many({}, {'$set' : {'attempts' : 3}}):

		# count of all the updated documents
		n = collection.count_documents({'attempts' : 3})

		# total documents in the collection
		t = collection.count_documents({})

		# printing the counts to ensure all records are updated
		print(f'==> {dt.now()} :: {n}/{t} Documents Updated')


# Function to decrement attempt after uploading image
def decrement_attempt(mail):
	# the database that stores user data
	db = mongoClient['userdata']

	# collection that stores user data
	collection = db['data']

	# the mail will be used as query for decrementing
	# the upload attempts count
	details = {
		'mail' : '%s'%(mail)
		}
	
	# check if the document with the required mail
	# attempts gets decremented by 1
	# every time a file is successfully uploaded
	if collection.update_many(details, {'$inc' : {'attempts' : -1}}):

		# fetching the document with the mail
		doc= list(collection.find({"mail" : '%s'%(mail)}, {}))

		# print the document to verify 
		# successful decrement of attempt count
		print(f'==> {doc}')


# Function to return remaining attempts
def get_attempts(mail):
	# the database that stores user data
	db = mongoClient['userdata']

	# collection that stores user data
	collection = db['data']

	# the mail will be used as query for fetching
	# the upload attempts count
	details = {
		'mail' : '%s'%(mail)
		}
	
	# list with mail as query 
	# returns only the attempt count in BSON
	attempts = list(collection.find(details, {"attempts" : 1}))

	# getting the attempt count from the BSON
	attempt = attempts[0]['attempts']

	# the attempt count is returned
	return attempt


# Function to create PDF Report and Mail to respective authorities
def report_authority():
	# TODO : Generate graph and mail to required mail ID
	pass

# - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - -


# Default Index Route
@app.route('/')
def index():
	return render_template("index.html")


# - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - -


# Login Page Function
@app.route('/login')
def login(check = {
				'valid_Mail' : True,
				'valid_Pass' : True,
				# 'valid_user' : True,
				'valid_Captcha' : True
			}, 
			msg = '', 
			values = {
				'mail' : ''
			}):
	# the checks are by default all True
	# After validation and db checking, the checks can be False
	# empty msg as the form is not filled
	# empty value for mail as first time the form is not filled
	# (first time access of form)

	# login.html rendered with default values
	return render_template(
		"login.html", 
		check = check, 
		msg = msg, 
		values = values
		)


# - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - -


# Signup Page function
@app.route('/signup')
def signup(check = {
				'valid_Mail' : True,
				'mail_Duplicate' : True,
				'valid_Pass' : True,
				'match_Pass' : True,
				'valid_Captcha' : True
			}, 
			msg = '', 
			values = {
				'mail' : ''
			}):
	# the checks are by default all True
	# After validation and db checking, the checks can be False
	# empty msg as the form is not filled
	# empty value for mail as first time the form is not filled
	# (first time access of form)

	# signup.html rendered with default values
	return render_template(
		"signup.html", 
		check = check, 
		msg = msg, 
		values = values
		)


# - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - -


# I M P O R T A N T
# 					I M P O R T A N T
# 									  I M P O R T A N T

# function to validate and check the login and signup information
@app.route('/form', methods = ['POST', 'GET'])
def form(file_check = {
			'valid_address' : True,
			'valid_area' : True,
			'valid_state' : True,
			'valid_district' : True,
			'valid_zip' : True,
			'valid_file' : True,
			'valid_Captcha' : True
		},
		file_values = {
			'address' : '', 
			'area' : '', 
			'zipcode' : ''
		}):
	# all the file upload form checks are kept True by default 
	# all file_values are kept empty before the form is filled for the first time
	# (first time access of form)

	# database to be used for verifying Login info
	# or add the credentials after Signup
	db = mongoClient['userdata']

	# the collection used for valid user credentials
	collection = db['data']

	mail_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
	# Regular Expression for valid mail id pattern
	# --> does not check the validity(existence) of mail <--

	pass_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,20}$'
	# Regular Expression for valid password
	# must include : 
	# 1 Uppercase
	# 1 Lowercase
	# 1 Number/Digit
	# 1 Special Character
	# length must be between 8 to 20


	# check for session started
	# mail = session.get('mail')
	# print(mail)

	# Login/Signup form redirect
	# All POST requests get validated here ↓
	if request.method == "POST":

		# Condition for Signup Form
		if request.form.get("page") == "Signup":

			check = {
				'valid_Mail' : True,
				'mail_Duplicate' : True,
				'valid_Pass' : True,
				'match_Pass' : True,
				'valid_Captcha' : True
			}
			# checks will be determined after checking all fields against regular expressions and DB


			# field values given by the user for account creation
			mail = request.form.get("mail").strip().replace(' ', '')
			password = request.form.get("password").strip().replace(' ', '')
			conf_pass = request.form.get("conf_pass").strip().replace(' ', '')	# confirm password field
			# the password & confirm password are received in plain-text
			# the leading, trailing & in-between spaces are removed by strip() & replace()


			# will be used as value in case of unsuccessful signup
			values = {
				'mail' : mail
			}


			# check for mail
			# should not be empty
			# match the regular Expression
			if not mail or not re.fullmatch(mail_regex, mail):
				# if any of the condition fails the 
				# valid mail check is marked False
				check['valid_Mail'] = False


			# checking if the mail already exists in the DB
			if collection.count_documents({'mail' : '%s' % (mail)}):
				# if user already exists
				check['mail_Duplicate'] = False
			

			# check for plain-text password & confirm password
			# should not be empty
			# match the regular Expression
			if not password or not conf_pass or not re.fullmatch(pass_regex, password) or not re.fullmatch(pass_regex, conf_pass):
				# if any of the condition fails the 
				# valid password check is marked False
				check['valid_Pass'] = False


			# match password and confirm password fields
			if password != conf_pass:
				# if the passwords do not match
				# match password check is marked False
				check['match_Pass'] = False


			# validation of CAPTCHA
			if not captcha.validate():
				# if incorrect captcha
				check['valid_Captcha'] = False


			# generating random salt that will be used to 
			# add extra security after hashing of plaintext password
			# salt type -> bytes
			salt = bcrypt.gensalt()

			# plain-text password is encoded to bytes and 
			# salted to get hashed password 
			# hashed password type -> bytes
			password = bcrypt.hashpw(password.encode(), salt)


			# if all the checks are True
			if all([i for i in check.values()]):
				
				# dictionary used as query for creating user in DB
				# and return same values to form in case there is an error
				details= {
					'mail' : '%s' % (mail),
					'pass' : '%s' % (password.decode()),
					'attempts' : '%d' % (3)
				}


				# inersting the details in DB 
				# creating the user account
				if collection.insert_one(details):
					
					# mail id will be stored in token session
					# to keep track of file uploads
					session['mail'] = mail

					# initially declaration of remaining attempts
					remaining_attempts = False

					# the actual count of attempts remaining based on mail
					attempts = get_attempts(mail)

					# mark remaining attempts as True if user has got attempts remaining
					if attempts> 0:
						remaining_attempts = True

					# redirected to file upload form after successful user login
					return render_template(
						"file_upload.html", 
						msg = 'User Created Successfully', 
						check = file_check, 
						err= '', 
						attempts= attempts, 
						remaining_attempts= remaining_attempts, 
						values= file_values
						)
				
				# incase there is an error in user creation
				# regarding DB
				else:

					# redirect to signup page if there was error in user creation
					return render_template(
						"signup.html", 
						check= check, 
						msg= 'Failed to create user. Try Again', 
						values= values
						)

			# in case there is an error in input data
			# like mail/password regex error
			else:
				
				# check if the session is active
				if mail:
					# initially declaration of remaining attempts
					remaining_attempts = False

					# the actual count of attempts remaining based on mail
					attempts = get_attempts(mail)

					# mark remaining attempts as True if user has got attempts remaining
					if attempts> 0:
						remaining_attempts = True

					# redirected to file upload form if form is refershed without submitting
					return render_template(
						"file_upload.html", 
						check = file_check, 
						msg = '', 
						err = '', 
						attempts = attempts, 
						remaining_attempts = remaining_attempts, 
						values = file_values
						)
				
				# incase session is not active
				else:

					# the credentials are either empty or do not match the regular expression check
					return render_template(
						"signup.html", 
						check = check, 
						msg = 'Try Again', 
						values = values
						)
	
# - - - - - - - - - - - - - - - - - - - - - - - - - - -

		# Condition for Login Form
		elif request.form.get("page") == "Login":

			check= {
				'valid_Mail' : True,
				'valid_Pass' : True,
				# 'valid_user' : True,
				'valid_Captcha' : True
			}
			# checks will be determined after checking all fields against regular expressions and DB


			# the input credentials for Login
			mail = request.form.get("mail").strip().replace(' ', '')
			password = request.form.get("password").strip().replace(' ', '')
			# the password is received in plain-text
			# the leading, trailing & in-between spaces are removed by strip() & replace()


			# will be used as value in case of unsuccessful signup
			values = {
				'mail' : mail
			}


			# check for mail
			# should not be empty
			# match the regular Expression
			if not mail or not re.fullmatch(mail_regex, mail):
				# if any of the condition fails the 
				# valid mail check is marked False
				check['valid_Mail'] = False


			# check for plain-text password
			# should not be empty
			# match the regular Expression
			if not password or not re.fullmatch(pass_regex, password):
				# if any of the condition fails the 
				# valid password check is marked False
				check['valid_Pass'] = False


			# validation of CAPTCHA
			if not captcha.validate():
				# if incorrect captcha
				check['valid_Captcha'] = False


			# if all the checks are True
			if all([i for i in check.values()]):
				

				# the count of user will be returned (0 or 1)
				# 1 if exists ; 0 if not
				# the DB contains only unique mails 
				user_exist = collection.count_documents({'mail' : '%s'%(mail)})
				

				# user found in DB
				if user_exist:

					# the password field will be returned for the mail id entered
					db_passwords = list(collection.find({"mail" : '%s'%(mail)}, {"pass": 1}))
					db_password = db_passwords[0]['pass']
					

					# password hashed and salted using Bcrypt
					# checkpw function used to check the input password
					# the function takes password(input) & password stored in database
					# both parameters need to be in bytes and thus are encoded
					# boolean value is returned (True for match)
					correct_pass = bcrypt.checkpw(password.encode(), db_password.encode())

					# print(user_exist)
					# print(password)
					# print(db_password)
					# print(correct_pass)


					# if the user is found and password is correct
					if user_exist and correct_pass:
						
						# mail id will be stored in token session
						# to keep track of file uploads
						session['mail'] = mail

						# initially declaration of remaining attempts
						remaining_attempts = False

						# the actual count of attempts remaining based on mail
						attempts = get_attempts(mail)

						# mark remaining attempts as True if user has got attempts remaining
						if attempts > 0:
							remaining_attempts = True

						# redirected to file upload form after successful user login
						return render_template(
							"file_upload.html", 
							msg = 'Logged in Successfully', 
							check = file_check, 
							err = '', 
							attempts = attempts, 
							remaining_attempts = remaining_attempts, 
							values = file_values
							)
					
				else:
					# redirect to login page if the user does not exist in DB
					return render_template(
						"login.html", 
						check = check, 
						msg = 'User does not exist.', 
						values = values
						)

			# in case there is an error in input data
			# like mail/password regex error
			else:
				
				# check if the session is active
				if mail:
					# initially declaration of remaining attempts
					remaining_attempts = False

					# the actual count of attempts remaining based on mail
					attempts = get_attempts(mail)

					# mark remaining attempts as True if user has got attempts remaining
					if attempts > 0:
						remaining_attempts = True

					# redirected to file upload form if form is refershed without submitting
					return render_template(
						"file_upload.html", 
						check = file_check, 
						msg = '', 
						err = '', 
						attempts = attempts, 
						remaining_attempts = remaining_attempts, 
						values = file_values
						)
				
				else:

					# the credentials are either empty or do not match the regular expression check
					return render_template(
						"login.html", 
						check = check, 
						msg = 'Try Again', 
						values = values
						)

# - - - - - - - - - - - - - - - - - - - - - - - - - - -

	# elif mail:

	# 	print('elif', mail)
	# 	remaining_attempts= False

	# 	attempts= get_attempts(mail)

	# 	if attempts> 0:
	# 		remaining_attempts= True

	# 	return render_template("file_upload.html", check= check, msg= '', err= '', attempts= attempts, remaining_attempts= remaining_attempts)

	else:

		# print('redirct')
		# if the page is accesses without logging in or signing up
		# redirected to login page
		return redirect('/login')


# - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - -


# function to validate file upload forms data
@app.route('/file_upload', methods = ['POST', 'GET'])
def file_upload(check = {
			'valid_address' : True,
			'valid_area' : True,
			'valid_state' : True,
			'valid_district' : True,
			'valid_zip' : True,
			'valid_file' : True,
			'valid_Captcha' : True
		}):
	# checks will be determined after verifying every field
	

	# check for session started
	mail = session.get('mail')
	print('-----------------------------------')
	print('Session Mail : ', mail, ':::', session.get('mail'))
	print('-----------------------------------')
	
	
	# after the file upload form submission
	# All POST requests get validated here ↓
	if request.method == 'POST':

		# field values given by the user for image location
		address = request.form.get('address').strip()
		area = request.form.get('area').strip()
		state = request.form.get('state').strip().replace(' ', '')
		district = request.form.get('district').strip().replace(' ', '')
		zipcode = request.form.get('zipcode').strip().replace(' ', '')
		# the leading, trailing & in-between spaces are removed by strip() & replace()

		# the file uploaded by user
		file = request.files['road_img']
		file_name = file.filename


		# result variables initialized with 0 value
		pothole_percent, detect_result = 0, 0
		

		# if the file name matches the allowed extensions
		if allowed_file(file.filename):

			# replaces any extra characters with underscore (_)
			file_name= secure_filename(file.filename)

			# save the file for pothole detection at uploads folder
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
			
			# file path is stored that will be fed to ML model for pothole detection
			path= os.path.join(app.config['UPLOAD_FOLDER'], file_name)

			# pothole detection results after ML model
			pothole_percent, detect_result= model(glob.glob(path))

		else:
			# invalid file type
			check['valid_file']= False


		if not address:
			# empty address field
			check['valid_address']= False


		if not area:
			# empty area field
			check['valid_area']= False
		

		# list of states valid for form submission
		STATES_LIST_INDIA = ['Gujarat', 'Maharashtra', 'Delhi']


		if not state or state not in STATES_LIST_INDIA:
			# state field either empty or not in list
			check['valid_state']= False


		if not district:
			# empty district field
			check['valid_district']= False


		if not zipcode or zipcode.startswith('0'):
			# empty or invalid zipcode
			check['valid_zip']= False


		# validation of CAPTCHA
		if not captcha.validate():
			# if incorrect captcha
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

		values= {
			'address': address,
			'area': area,
			'zipcode': zipcode
		}

		remaining_attempts= False

		attempts= get_attempts(mail)
		print(mail)

		if attempts> 0:
			remaining_attempts= True

		if all([i for i in check.values()]):

			# if pothole_percent< 60:
				# os.remove()

			mail= session.get('mail')

			db= mongoClient['userdata']

			collection= db['pothole_result']

			details= {
				'mail': '%s'%mail,
				'address': '%s'%address,
				'area': '%s'%area,
				'state': '%s'%state,
				'district': '%s'%district,
				'zipcode': '%s'%zipcode,
				'file_name': '%s'%file_name,
				'pothole_percent': '%s'%pothole_percent
			}

			if collection.insert_one(details):

				print('inserted', details)

				print(session.get('mail'))

				print(list(db['data'].find({"mail" : mail})))

				db['data'].update_many({"mail" : mail}, {'$inc': {'attempts': -1}})

				print(list(db['data'].find({"mail" : mail})))

				remaining_attempts= False

				attempts= get_attempts(mail)

				if attempts> 0:
					remaining_attempts= True
				
				return render_template("pothole_result.html", parameters=parameters, results= results, attempts= attempts, remaining_attempts= remaining_attempts)
			else:
				return render_template("file_upload.html", check= check, msg= '', err= 'Some Error Occurred. Try Again.', attempts= attempts, remaining_attempts= remaining_attempts, values= values)
		else:
			return render_template("file_upload.html", check= check, msg= '', err= '', attempts= attempts, remaining_attempts= remaining_attempts, values= values)
		
	elif mail:
		remaining_attempts= False

		attempts= get_attempts(mail)

		if attempts> 0:
			remaining_attempts= True

		return render_template("file_upload.html", check= check, msg= '', err= '', attempts= attempts, remaining_attempts= remaining_attempts, values= values)
	
	return redirect('/login')


# - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - -


# A D M I N
# 			A D M I N
# 					  A D M I N

# Admin Login Form
@app.route('/admin')
def admin():
	return render_template("admin.html")


# - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - -


# Admin Dashboard
@app.route('/admin_login', methods=['POST', 'GET'])
def admin_panel():
	return "Admin Page"


# - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - -
# - - - - - - - - - - - - - - - - - - - - - - - - - - -


# Main Function -->
if __name__ == "__main__":

    app.run(debug=True)
    
	# file_upload_attempt_update.add_job(
	# 	id='Update Attempts', 
	# 	func= update_attempts, 
	# 	trigger= 'cron', 
	# 	hour= 0,
	# 	minute= 0
	# 	)
	
	# file_upload_attempt_update.start()
	
	# authority_report.add_job(
	# 	id='Update Attempts', 
	# 	func= update_attempts, 
	# 	trigger= 'cron', 
	# 	hour= 0,
	# 	minute= 0
	# 	)
	
	# authority_report.start()

    # app.run(debug=True, host='0.0.0.0', use_reloader= False)