from flask import Flask, render_template, request, redirect, url_for,make_response
import os,secrets
from pymongo import MongoClient
import jwt
from functools import wraps

#test pull
app = Flask(__name__)
#test push
app.config['SECRET_KEY']=secrets.token()

import smtplib
from datetime import datetime,timedelta
my_email = "nicdelhi2024@gmail.com"
code = "zuff vkvx pamt kdor"
from flask_bcrypt import Bcrypt 
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
bcrypt = Bcrypt(app) 
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
superadmin_collection=db['Superadmin']
hospital_data_collection=db['hospital_data']



def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token=request.cookies.get('access_token')

        if not token:
            return redirect('/user_login')

        try:
            data=jwt.decode(token,app.config['SECRET_KEY'],algorithms=["HS256"])
            current_user=data['user_username']
        except jwt.ExpiredSignatureError:
            return 'Token has expired',401
        
        except jwt.InvalidTokenError:
            return redirect('/user_login')
        
        return f(current_user,*args,**kwargs)
    return decorated




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
                token=jwt.encode({
                    'user_username':username,
                    'exp':datetime.utcnow()+timedelta(hours=1)
                },app.config['SECRET_KEY'],algorithm="HS256")
                response=make_response(redirect('/appointment'))
                response.set_cookie('access_token',token,httponly=True)
                response.set_cookie('user_username',username,httponly=True)
                # return redirect('/appointment')
                return response
                # return redirect('/appointment')
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
    hospitals = hospital_data_collection.find()
    hospital_names = [hospital['hospital_name'] for hospital in hospitals]

    return render_template('appointment.html', hospitals=hospital_names)

@app.route('/admin/add_patient',methods=['GET','POST'])
def add_patient():
    if request.method=='POST':
        name = request.form['Name']
        dob =request.form['dob']
        gender = request.form['gender']
        address = request.form['address']
        phone= request.form['phone']
        email=request.form['email']
        aadhaar= request.form['aadhaar']
        bed_type = request.form['bedtype']
        bed_no = request.form['bedno']
        data = {
            'name':name,
            'dob':dob,
            'gender':gender,
            'address':address,
            'phone':phone,
            'email':email,
            "aadhaar":aadhaar,
            "bed_type":bed_type,
            "bed no":bed_no
        }
        patients_collection.insert_one(data)
        return redirect(url_for('confirmation'))
    return render_template('add patient.html')

@app.route('/confirmation')
def confirmation():
    return render_template('conformation.html', message="Patient successfully added!")


@app.route('/manage_appointment',methods=['GET','POST'])
def manage():
    pass






@app.route('/admin_login',methods=["GET","POST"])
def admin_login():
    if request.method == 'POST':
        username= request.form['username']
        pa = request.form['password']
        password=bcrypt.generate_password_hash(pa).decode('utf-8')
        admin = admin_collection.find_one({'hospital_mail': username})
        if admin:
            # Compare the entered password with the stored hashed password
            if bcrypt.check_password_hash(admin['hospital_password'], password):
                return redirect('/admin')
            
            else:
                return 'Wrong password'
        
        return 'User not found'
    return render_template("login_admin.html")

@app.route('/admin/',methods=['GET','POST'])
def admin():
    total_appointment = appointment_collection.count_documents({})

    return render_template('admin_dashboard.html',count=total_appointment)


@app.route("/admin/contact-us")
def admin_contact_us():
    contacts = contact_collection.find()
    return render_template("manage_appointment.html", contacts=contacts)

@app.route('/admin/add_detail',methods=['GET','POST'])
def add_details():
    if request.method=='POST':
        name= request.form['hospitalName']
        ID =request.form['hospitalID']
        address1=request.form['addressLine1']
        city = request.form['city']
        state = request.form['stateProvince']
        postal_code = request.form['postalCode']
        contact_number= request.form['contactNumber']
        emergency=request.form['emergencyContactNumber']
        email = request.form['emailAddress']
        website = request.form['websiteURL']
        no_beds = request.form['numberOfBeds']
        no_icu = request.form['numberOfICUBeds']
        no_ventilator = request.form['numberOfVentilators']
        emergency_dept = request.form['emergencyDepartment']
        spetialisation = request.form['specialization']
        operating_hour = request.form['hospitalOperatingHours']
        visiting_hour = request.form['visitingHours']
        pharmacy_onsite = request.form['pharmacyOnSite']
        no_doctor = request.form['totalNumberOfDoctors']
        no_nurse = request.form['totalNumberOfNurses']
        no_admin_staff = request.form['administrativeStaffCount']
        ambulance = request.form['ambulanceServices']
        bload_bank = request.form['bloodBank']
        diagonis_services = request.form['diagnosticServices']

        data  = {
        "hospital_name": name,
        "hospital_id": ID,
        "address_line1": address1,
        "city": city,
        "state": state,
        "postal_code": postal_code,
        "contact_number": contact_number,
        "emergency_contact_number": emergency,
        "email_address": email,
        "website_url": website,
        "number_of_beds": no_beds,
        "number_of_icu_beds": no_icu,
        "number_of_ventilators": no_ventilator,
        "emergency_department": emergency_dept,
        "specialization": spetialisation,
        "hospital_operating_hours": operating_hour,
        "visiting_hours": visiting_hour,
        "pharmacy_on_site": pharmacy_onsite,
        "total_number_of_doctors": no_doctor,
        "total_number_of_nurses": no_nurse,
        "administrative_staff_count": no_admin_staff,
        "ambulance_services": ambulance,
        "blood_bank": bload_bank,
        "diagnostic_services": diagonis_services}
    
    # Insert the data into the hospital collection
        hospital_data_collection.insert_one(data)
    return render_template('hospital_details.html',)




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

@app.route('/superadmin/', methods=['GET', 'POST'])
def superadmin():
    return render_template('super admin dash.html')


@app.route("/superadmin_login", methods=['GET', 'POST'])
def superadmin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the username and password match an entry in the admin_collection
        if superadmin_collection.find_one({"username": username, "password": password}):
            return redirect('/superadmin')
        else:
            return redirect('/superadmin_login')
    
    return render_template("Super_Admin_login.html")


@app.route('/superadmin/addHospital', methods=['GET', 'POST'])
def add_hospital():
    if request.method == 'POST':
        hospital_name = request.form['hospitalName']
        hospital_mail = request.form['hospitalmail']
        
        pa = request.form['hospitalpass']
        password=bcrypt.generate_password_hash(pa).decode('utf-8')
        # Store the hospital data in the hospital collection
        hospitalData = {
            "hospital_name": hospital_name,
            "hospital_mail": hospital_mail,
            "hospital_password": password
        }
        admin_collection.insert_one(hospitalData)

        
        with smtplib.SMTP("smtp.gmail.com", 587) as connection:
            connection.starttls()
            time = datetime.now()
            connection.login(user=my_email, password=code)
            connection.sendmail(from_addr=my_email,
                                    to_addrs=hospital_mail,
                                    msg=f"""
Dear,
Your Hospital Account (Email ID {hospital_mail}) Password is:{pa}.

(Generated at {time})

********************************
This is an auto-generated email. Do not reply to this email.""")
        return redirect('/superadmin')
    
    
@app.route('/superadmin/checkHospitalStatus', methods=['GET', 'POST'])
def check_hospital():
    if request.method == 'POST':
        hospital_name = request.form.get('hname')
        
        if not hospital_name:
            return "Hospital name is missing", 400  # Bad Request
        
        data = hospital_data_collection.find_one({'hospital_name': hospital_name})
        
        if data:
            return render_template('superadmin_hospital_status.html', data=data)
        else:
            return "No hospital found"
    
    return render_template('superadmin_hospital_status.html')
#where is the change
#show
@app.route('/user_logout')
def user_logout():
    response=make_response(redirect('/user_login'))
    response.delete_cookie('access_token')
    return response

@app.route('/logout')
def admin_logout():
    response=make_response('/admin_login')
    response.delete_cookie('access_token')
    return response


if __name__ == '__main__':
    app.run( port=8000,debug=True)
