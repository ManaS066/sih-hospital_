from flask import Flask, flash, redirect, render_template, request, url_for

# from flask_pymongo import PyMongo,MongoClient
import pymongo
from pymongo import MongoClient


from jinja2 import Environment, FileSystemLoader

Doctor_Logedin = None

template_loader = FileSystemLoader(searchpath="D:/dev/HMS/templates")
jinja_env = Environment(loader=template_loader)
app = Flask(__name__)
client = MongoClient('mongodb+srv://manasranjanpradhan2004:root@hms.m7j9t.mongodb.net/?retryWrites=true&w=majority&appName=HMS')
db = client['HMS']  # Replace 'hospital' with your MongoDB database name
patients_collection = db['patients']  # Collection for patients
doctors_collection = db['doctors'] 
users_collection = db['users'] 
admin_collection = db['admin']
appointment_collection = db['appointment'] 
contact_collection = db['contact']



@app.route('/login' ,methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        login_user = users_collection.find_one({'username': username})
        if login_user:
            if login_user['password'] == password:
                
                return render_template('index.html')
            else:
                return 'Wrong password'
        else:
            return 'Username not found'
    else:
        return render_template('user_login.html')



@app.route('/registration',methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        existing_user = users_collection.find_one({'$or': [{'username': username}, {'email': email}]})
        if existing_user:
            return render_template('regisration.html')
        # Insert user data into MongoDB
        user_data = {
            'username': username,
            'email': email,
            'password': password
        }
        result = users_collection.insert_one(user_data)
        print(f"User added with ID: {result.inserted_id}")
        return render_template('user_login.html')
    return render_template('regisration.html')



@app.route("/",methods=["get","post"])
def home():
    if request.method == "POST":
        name = request.form['name']
        email =request.form['email']
        number = request.form['number']
        comment = request.form['comment']
        contact_data = {
            'name':name,
            'email':email,
            'number':number,
            'comment':comment
        }
        contact_collection.insert_one(contact_data)
    return render_template("index.html")



@app.get('/user')
def user():
    return render_template('user_app.html')



@app.route('/doctor', methods=['GET', 'POST'])
def doctor_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        doctor = doctors_collection.find_one({'username': username, 'password': password})
        Doctor_Logedin=doctor['name']
        if doctor:
            name = doctor['name']
            email = doctor['email']
            spec = doctor['specialization']
            phone = doctor['phone']
            data = (name, email, spec, phone)
            print(data)
            # Corrected query with projection {'doc_appoint': 1}
            appointments_data = list(appointment_collection.find({'disease': spec},))
            template = jinja_env.get_template('doctor_app.html')
            
            # Filter appointments with missing email field
            appointment_emails = [appointment['email'] for appointment in appointments_data if 'email' in appointment]

            return template.render(data=data, appointments_data=appointments_data, appointment_emails=appointment_emails)
        else:
            return render_template('doctor_login.html')
        
    return render_template('doctor_login.html')




@app.route('/admin/appointments')
def admin_appointments():
    # Retrieve all appointment data from the database
    appointments = list(appointment_collection.find())
    return render_template('admin_appointments.html', appointments=appointments)



@app.route('/admin', methods=['GET', 'POST'])
def admin():
     if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        login_admin = admin_collection.find_one({'username': username})
        if login_admin:
            if login_admin['password'] == password:
                total_app = appointment_collection.count_documents({})
                total_doc = doctors_collection.count_documents({})
                total_patient = patients_collection.count_documents({})
                total_contact = contact_collection.count_documents({})
                return render_template('admin_dashboard.html',appointment = total_app,doc=total_doc,patient=total_patient,contact  = total_contact)
            else:
                return 'Wrong password'
        else:
            return 'Username not found Contact Data Admin To Add Your Account.'
     else:
        return render_template('admin_pass.html')
     


    
@app.route("/admin/contact-us")
def admin_contact_us():
    contacts = contact_collection.find()
    return render_template("admin_contact_us.html", contacts=contacts)



@app.route('/add_patient',methods=['GET', 'POST'])
def add_patient():
    if request.method=="POST":
        name = request.form['patient_name']
        gender = request.form['gender']
        dob = request.form['dob']
        address = request.form['address']
        phone=request.form['phone']
        patients_data ={
            'name':name,
            'gender':gender,
            'dob':dob,
            'address':address,
            'phone':phone
        }
        patients_collection.insert_one(patients_data)
    return render_template('add_patient.html')

@app.route('/add_doc', methods=['GET', 'POST'])
def add_doc():
    if request.method=="POST":
        doc_name = request.form['doctor_name']
        specialization = request.form['specialization']
        qualification = request.form['qualification']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        phone = request.form['phone']
        doctor_data = {
            'name': doc_name,
            'specialization': specialization,
            'qualification': qualification,
            'email':email,
            'phone':phone,
            'username':username,
            'password':password,
            'view_count':0
        }
        doctors_collection.insert_one(doctor_data)
    return render_template('add_doc.html')



@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    if request.method == 'POST':
        name = request.form['name']
        number = request.form['number']
        email = request.form['email']
        address = request.form['Address']
        date = request.form['dat']
        disease = request.form['diseaseInput']
        description = request.form['diseaseDescription']
        data = {
            'name': name,
            'email': email,
            'number': number,
            'address': address,
            'date': date,
            'disease': disease,
            'description': description,
            'doc_appoint':None
        }
        appointment_collection.insert_one(data)
        
        return redirect('/')
        print("Data inserted into MongoDB")

    return render_template('appointment.html')

@app.post("/approve")
def approve():
    name = request.form['docName']
    patEmail=request.form['patEmail']
    appointment = appointment_collection.find({'email':patEmail})

    if appointment:
        appointment_collection.update_one(  {'email': patEmail},
            {'$set': {'doc_appoint': name}})
        return redirect('/doctor')
if __name__ == '__main__':
    app.run(debug=True, port=8080)
