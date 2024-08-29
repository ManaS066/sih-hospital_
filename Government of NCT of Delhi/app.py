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


@app.route('/user_login', methods=['POST', 'GET'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Find the user by username
        user = users_collection.find_one({'username': username})

        if user:
            # Compare the entered password with the stored hashed password
            if bcrypt.check_password_hash(user['password'], password):
                return redirect('/appointment')
            else:
                return 'Wrong password'
        
        return 'User not found'

    return render_template('user_login.html')



@app.route('/user_register',methods=['GET','POST'])
def user_register():
    if request.method=='POST':
        name=request.form['name']
        number=request.form['phone']
        email= request.form['email']
        user_name = request.form['username']
        # existing_user = users_collection.find_one({'$or': [{'username': user_name}, {'email': email}]})
        # if existing_user:
        #     return 'Username or email already exists'
        pa = request.form['password']
        password=bcrypt.generate_password_hash(pa).decode('utf-8')
        user_data={
            'name':name,
            'username':user_name,
            'email':email,
            'number':number,
            'password':password
        }
        users_collection.insert_one(user_data)
        return redirect('/user_login')
    return render_template('user register.html')


@app.route('/appointment', methods=['POST', 'GET'])
def appointment():
    if request.method == 'POST':
        # Extract form data
        name = request.form['name']
        number = request.form['number']
        email = request.form['email']
        address = request.form['Address']
        appointment_date = request.form['dat']
        time_slot = request.form['timeSlot']
        speciality = request.form['diseaseInput']
        disease_description = request.form['diseaseDescription']
        appointment_data = {
            'name': name,
            'number': number,
            'email': email,
            'address': address,
            'appointment_date': appointment_date,
            'time_slot': time_slot,
            'speciality': speciality,
            'disease_description': disease_description
        }
        appointment_collection.insert_one(appointment_data)

        # After saving or processing, redirect or render a success page
        return "Appointment Sucessfull"
    # If GET request, just render the appointment form
    return render_template('appointment.html')

#Adding Doctor

@app.route('/add_doc',methods=['POST','GET'])
def doctor_register():
    if request.method=='POST':
        name=request.form['doctor_name']
        specialization=request.form['specialization']
        qualification=request.form['qualification']
        email=request.form['email']
        username=request.form['username']
        password=request.form['password']
        hash_password=bcrypt.generate_password_hash(password).decode('utf-8')
        phone=request.form['phone']
        aadhar=request.form['aadhaar']

        doctor_data={
            'name':name,
            'specialization':specialization,
            'qualification':qualification,
            'email':email,
            'username':username,
            'password':hash_password,
            'phone':phone,
            'aadhar':aadhar
        }
        doctors_collection.insert_one(doctor_data)
        return render_template('add doc.html')
    return render_template('add doc.html')















if __name__ == '__main__':
    app.run( port=8000,debug=True)