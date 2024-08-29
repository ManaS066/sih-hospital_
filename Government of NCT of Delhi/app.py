from flask import Flask, render_template, request, redirect
import os
from pymongo import MongoClient

app = Flask(__name__)


from flask_bcrypt import Bcrypt 
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://manasranjanpradhan2004:root@hms.m7j9t.mongodb.net/?retryWrites=true&w=majority&appName=HMS"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
db = client['HMS']
patients_collection = db['patients']
doctors_collection = db['doctors']
users_collection = db['users']
admin_collection = db['admin']
appointment_collection = db['appointment']
contact_collection = db['contact']

bcrypt = Bcrypt(app) 




@app.route('/',methods=['GET', 'POST'])
def landing():
    if request.method=='POST':
        name= request.form['name']
        email = request.form['email']
        number = request.form['number']
        comment = request.form['comment']
        contact_data = {
            'name': name,
            'email': email,
            'number': number,
            'comment': comment
        }
        contact_collection.insert_one(contact_data)
    return render_template('index.html')


@app.route('/user_register',methods=['GET','POST'])
def user_register():
    if request.method=='POST':
        name=request.form['name']
        number=request.form['phone']
        email= request.form['email']
        user_name = request.form['username']
        existing_user = users_collection.find_one({'$or': [{'username': user_name}, {'email': email}]})
        if existing_user:
            return 'Username or email already exists'
        pa = request.form['password']
        password=bcrypt.generate_password_hash(pa).decode('utf-8')
        user_data={
            'name':name,
            'username':user_name,
            'number':number,
            'password':password
        }
        users_collection.insert_one(user_data)
        return render_template('user login.html')
    return render_template('user register.html')






















if __name__ == '__main__':
    app.run( port=8000,debug=True)