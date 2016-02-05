# -*- coding: utf-8 -*-
__author__ = 'Antonio'
from flask import app, request
from flask import Flask
import database_helper
import json
import random
import re

app = Flask(__name__)
app.debug = True

list_token={}
min_size_password=4


"""
	Definition:	
		connecte to the database before any request
    Keyword arguments:
	Return:
"""
@app.before_request
def before_request():
    database_helper.connect_db()

"""
	Definition:	
		disconnecte to the database in case of problem
    Keyword arguments:
	Return:
"""
@app.teardown_request
def teardown_request(exception):
    database_helper.close_db()


"""
	Definition:	​Authenticates the username by the provided password.
    Keyword arguments: -
	Return: the token or a message error
		
"""
@app.route('/signin', methods=['POST'])
def sign_in():
	email = request.form['email']
	password = request.form['password']
	if  validate_signin(email,password):
		result = database_helper.sign_in(email,password)
		if result == 'user not found':
			return return_json(404,False,result)
		else:
			return return_json(200,True,'Successfully signed in',create_token(result))
	else:
		return return_json(400,False,'wrong inputs')
"""
	Definition:	​Registers a user in the database.
    Keyword arguments: -
	Return: Message about the succes or the fail
"""
@app.route('/signup', methods=['POST'])
def sign_up():
	firstname = request.form['firstname']
	familyname = request.form['familyname']
	email = request.form['email']
	password =request.form['password']
	gender =request.form['gender']
	city =request.form['city']
	country =request.form['country']
	if  validate_singup(email,password,firstname,familyname,gender,city,country):
		result = database_helper.sign_up(email,password,firstname,familyname,gender,city,country)
		if result == True:
			return return_json(200,True,'User added')
		else:	
			return return_json(400,False,'sign up fail')
	else:
		return return_json(400,False,'wrong inputs')

"""
	Definition:	Retrieves the stored data for the user whom the passed token is issued for. The currently
signed in user can use this method to retrieve all its own information from the server.
    Keyword arguments: -
	Return: information about the user or error message
"""
@app.route('/getuserdatabytoken/<token>', methods=['GET'])
def get_user_data_by_token(token = None):  
	if token != None and list_token.has_key(token):
		result = database_helper.get_user_data(list_token.get(token))
		if result == 'user not found':
			return return_json(404,False,result)
		else:
			return return_json(200,True,'User data retrieved',result)
	else:
		return return_json(403,False,'user not connected')

"""
	Definition:	​Signs out a user from the system
    Keyword arguments: -
	Return: message to know if it's a success or a fail
"""
@app.route('/signout/<token>', methods=['GET'])
def sign_out(token = None):
	if token != None:
		if list_token.has_key(token):
			list_token.pop(token)
			return return_json(200,True,'user disconnected')
		else:
			return return_json(404,False,'user not found')
	else:
		return return_json(400,False,'wrong inputs')

"""
	Definition:	​Changes the password of the current user to a new one.
    Keyword arguments: -
	Return: message to know if it's a success or a fail
"""
@app.route('/changepassword', methods=['POST'])
def change_password():
	  
	token = request.form['token']
	if list_token.has_key(token):
		password = request.form['password']
		new_password = request.form['new_password']
		result = database_helper.change_password(list_token.get(token),password,new_password)
		if result == True:
			return return_json(200,True,'password change')
		else:
			return return_json(401,False,'password incorrect')
	else:
		return return_json(403,False,'user not connected')

"""
	Definition:	Retrieves the stored data for the user whom the passed token is issued for. The currently
signed in user can use this method to retrieve all its own information from the server
    Keyword arguments: -
	Return: information about the user or error message
"""
@app.route('/getuserdatabyemail/<token>/<email>', methods=['GET'])
def get_user_data_by_email(token = None, email=None):
	if token != None and email!=None and list_token.has_key(token):
		result = database_helper.get_user_data_by_email(email)
		if result == 'user not found':
			return return_json(404,False,result)
		else:
			return return_json(200,True,'User data retrieved',result)
	else:
		return return_json(403,False,'user not connected')

"""
	Definition:	Retrieves the stored messages for the user whom the passed token is issued for. The
currently signed in user can use this method to retrieve all its own messages from the server.
    Keyword arguments: -
	Return: the message sent to the user or an error message
"""
@app.route('/getmessagesbytoken/<token>', methods=['GET'])
def get_messages_by_token(token = None):
	if token != None and list_token.has_key(token):
		result = database_helper.get_messages_by_token(list_token.get(token))
		if result == 'wrong email':
			return return_json(404,False,result)
		else:
			return return_json(200,True,'User message retrieved',result)
	else:
		return return_json(403,False,'user not connected')

"""
	Definition:	​Retrieves the stored messages for the user specified by the passed email address.
    Keyword arguments: -
	Return: the message sent to the user or an error message
"""
@app.route('/getmessagesbyemail/<token>/<email>', methods=['GET'])
def get_messages_by_email(token = None,email=None):  
	if token != None and email!=None and list_token.has_key(token):
		result = database_helper.get_messages_by_email(email)
		if result == 'wrong email':
			return return_json(404,False,result)
		else:
			return return_json(200,True,'User message retrieved',result)
	else:
		return return_json(403,False,'user not connected')

"""
	Definition:	​Tries to post a message to the wall of the user specified by the email address.
    Keyword arguments: -
	Return: message to know if it's a success or a fail
"""
@app.route('/postmessage', methods=['POST'])
def post_message():  
	token = request.form['token']
	if list_token.has_key(token):
		message = request.form['message']
		email = request.form['email']
		result = database_helper.post_message(list_token.get(token),message,email)
		if result == False:
			return return_json(404,False,'unknown receiver')
		else:
			return return_json(200,True,'message sent')
	else:
		return return_json(403,False,'user not connect')
	
	
	

######################################################
"""
	Definition:	return a json object with code http,success (bool),message (string), data (json object)
    Keyword arguments: 
		code http,success (bool),message (string), data (json object)
	Return: the json object
"""
def return_json(code,success,message,data=None):
	output = {}  
	output['success']=success
	output['message']=message
	output['data']=data
	return json.dumps(output), code

"""
	Definition:	Create a token for the user with the id given in parameter
    Keyword arguments: id of the user
	Return: the token generated for the user
"""
def create_token(id_user):
	letters = 'abcdefghiklmnopqrstuvwwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
	token = "";
	for i in range(0,36):
		token += letters[random.randint(0, len(letters)-1)];
	global list_token
	list_token[token]=id_user
	return token

def validateEmail(email):	
	if len(email) >= 5:
		if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{1,3}|[0-9]{1,3})(\\]?)$", email) != None:
		    return True
	return False

def validate_signin(email,password):
	result=validateEmail(email)
	if len(password)<min_size_password:
		result=False
	return result

def validate_singup(email,password,firstname,familyname,gender,city,country):
	result=validate_signin(email,password)
	if len(firstname)<=0 or len(familyname)<=0 or len(city)<=0 or len(country)<=0:
		result=False
	if gender!="Female" and gender!="Male":
		result=False
	return result

	


if __name__ == '__main__':
    app.run()
