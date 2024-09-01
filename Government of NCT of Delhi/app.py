from flask import Flask, flash, render_template, request, redirect, url_for,make_response,session,send_file
import os,secrets
from pymongo import MongoClient
import jwt
from functools import wraps
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
import qrcode
import io

#test pull
app = Flask(__name__)
#test push
# app.config['SECRET_KEY']=secrets.token_hex()\
app.secret_key=secrets.token_hex()

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
hospital_discharge_collection=db['discharged']



# def token_required(expected_role):
#     def decorator(f):
#         @wraps(f)
#         def decorated(*args,**kwargs):
#             if expected_role=='user':
#                 token=request.cookies.get('access_token_user')
#             else:
#                 token=request.cookies.get('access_token_admin')
#             if not token:
#                 return redirect('/user_login')

#             try:
#                 data=jwt.decode(token,app.config['SECRET_KEY'],algorithms=["HS256"])
#                 current_user=data['user_username']
#                 role=data.get('role')
#                 print(role)

#                 if role!=expected_role:
#                     return redirect(f'/{expected_role}_login')
#             except jwt.ExpiredSignatureError:
#                 return 'Token has expired',401
            
#             except jwt.InvalidTokenError:
#                 return redirect(f'/{expected_role}_login')
            
#             return f(current_user,*args,**kwargs)
#         return decorated
#     return decorator
def login_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args,**kwargs):
            print(f"Session data: {session}")
            print(f"Checking if username in session: {'username' in session}")
            print(f"Checking if role matches: {session.get('role')} == {role}")
            if 'username' not in session or session.get('role')!=role:
                return redirect(f'/{role}_login')
            return f(*args,**kwargs)
        return decorated_function
    return decorator



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
                # token=jwt.encode({
                #     'user_username':username,
                #     'role':'user',
                #     'exp':datetime.utcnow()+timedelta(hours=1)
                # },app.config['SECRET_KEY'],algorithm="HS256")
                # response=make_response(redirect('/appointment'))
                # response.set_cookie('access_token_user',token,httponly=True)
                # response.set_cookie('user_username',username,httponly=True)
 
                # return response
                session['username']=username
                session['role']='user'
                print(f'user session details:{session}')
                return redirect('/user_app')
            else:
                return 'Wrong password'
        
        return 'User not found'

    return render_template('user_login.html')

@app.route('/user_app',methods=['GET','POST'])
@login_required('user')
def user_app():
    user_info = users_collection.find_one({'username':session.get('username')})
    appointment = appointment_collection.find({'username':session.get('username')})
    return render_template('user_app.html',user = user_info,appointments =appointment)

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


@app.route('/all_doctor')
def all_doc():
    return render_template('doctor.html')


@app.route('/appointment', methods=['POST', 'GET'])
@login_required('user')
def appointment():
    if request.method == 'POST':
        # Extract form data
        name = request.form['name']
        user_name=session.get('username')
        number = request.form['number']
        email = request.form['email']
        address = request.form['Address']
        appointment_date = request.form['dat']
        time_slot = request.form['timeSlot']
        speciality = request.form['diseaseInput']
        disease_description = request.form['diseaseDescription']
        hospital_name = request.form['hospital']
        # total_no_of_appointments=hospital_data_collection.count_documents({"hospital_name":hospital_name})
        # print(total_no_of_appointments)
        appointment_data = {
            'name': name,
            'username':user_name,
            'number': number,
            'email': email,
            'address': address,
            'appointment_date': appointment_date,
            'time_slot': time_slot,
            'speciality': speciality,
            'disease_description': disease_description,
            'hospital_name':hospital_name
        }
        appointment_collection.insert_one(appointment_data)
        
        # After saving or processing, redirect or render a success page
        return redirect('/admin/confirmation')
    # If GET request, just render the appointment form
    hospitals = hospital_data_collection.find()
    hospital_names = [hospital['hospital_name'] for hospital in hospitals]

    return render_template('appointment.html', hospitals=hospital_names)

@app.route('/admin/add_patient',methods=['GET','POST'])
# @token_required('admin')
@login_required('admin')
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

        session['patient_name']=name
        hospital_name_patient=session.get('hospital_name')
        print(hospital_name_patient)
        data = {
            'name':name,
            'dob':dob,
            'gender':gender,
            'address':address,
            'phone':phone,
            'email':email,
            "aadhaar":aadhaar,
            "bed_type":bed_type,
            "bed no":bed_no,
            "hospital_name":hospital_name_patient
        }
        patients_collection.insert_one(data)
        return redirect(url_for('confirmation'))
    return render_template('add patient.html')

@app.route('/admin/confirmation')
def confirmation():
    return render_template('conformation.html', message="Patient successfully added!")


@app.route('/admin/manage_appointment',methods=['GET','POST'])
@login_required('admin')
def manage():
    hospital_name=session.get('hospital_name')
    appointments= appointment_collection.find({"hospital_name":hospital_name})
    return render_template('manage_appointment.html',appointments = appointments)






@app.route('/admin_login',methods=["GET","POST"])
def admin_login():
    if request.method == 'POST':
        username= request.form['username']
        pa = request.form['password']
        password=bcrypt.generate_password_hash(pa).decode('utf-8')
        # print('this is executed')
        
        admin = admin_collection.find_one({'hospital_mail': username})
        if admin:
            # Compare the entered password with the stored hashed password
            if bcrypt.check_password_hash(admin['hospital_password'], pa):
                # print('this is executed')
                # token=jwt.encode({
                #     'user_username':username,
                #     'role':'admin',
                #     'exp':datetime.utcnow()+timedelta(hours=1)
                # },app.config['SECRET_KEY'],algorithm="HS256")

                
                # response=make_response(redirect('/admin'))
                # response.set_cookie('access_token',token,httponly=True)
                # response.set_cookie('user_username',username,httponly=True)
                session['username']=username
                session['role']='admin'
                admin_email=session['username']
                hospital_data=admin_collection.find_one({"hospital_mail":admin_email})
                hospital_name_doctor=hospital_data.get("hospital_name")
                session['hospital_name']=hospital_name_doctor
                print(f'session details:{session}')
                # return response
                return redirect('/admin')
            
            else:
                return 'Wrong password'
        
        return 'User not found'
    return render_template("login_admin.html")

@app.route('/admin/',methods=['GET','POST'])
# @token_required('admin')
@login_required('admin')
def admin():
    hospital_name=session.get('hospital_name')
    print(hospital_name)
    total_appointment = appointment_collection.count_documents({"hospital_name":hospital_name})
    data = hospital_data_collection.find_one({'hospital_name': hospital_name})
    if data:
        beds = data['number_of_general_beds']
        return render_template('admin_dashboard.html',count=total_appointment,beds=beds)
    else:
        return redirect('/admin/add_detail')

@app.route("/admin/contact-us")
def admin_contact_us():
    contacts = contact_collection.find()
    return render_template("manage_appointment.html", contacts=contacts)

@app.route('/admin/add_detail',methods=['GET','POST'])
@login_required('admin')
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
        no_beds = int(request.form['numberOfBeds'])
        occupied_beds=int(request.form['Beds_occupied'])
        no_icu = int(request.form['numberOfICUBeds'])
        occupied_icu = int(request.form['icu_occupied'])
        no_ventilator = int(request.form['numberOfVentilators'])
        occupied_ventilator=int(request.form['ventilator_occupied'])
        emergency_dept = request.form['emergencyDepartment']
        spetialisation = request.form['specialization']
        operating_hour = request.form['hospitalOperatingHours']
        visiting_hour = request.form['visitingHours']
        pharmacy_onsite = request.form['pharmacyOnSite']
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
        "number_of_general_beds": no_beds,
        "occupied_general":occupied_beds,
        "number_of_icu_beds": no_icu,
        "occupied_icu":occupied_icu,
        "number_of_ventilators": no_ventilator,
        "occupied_ventilator":occupied_ventilator,
        "emergency_department": emergency_dept,
        "specialization": spetialisation,
        "hospital_operating_hours": operating_hour,
        "visiting_hours": visiting_hour,
        "pharmacy_on_site": pharmacy_onsite,
        "total_number_of_nurses": no_nurse,
        "administrative_staff_count": no_admin_staff,
        "ambulance_services": ambulance,
        "blood_bank": bload_bank,
        "diagnostic_services": diagonis_services}
    
    # Insert the data into the hospital collection
        hospital_data_collection.insert_one(data)

        return redirect('/admin')
    return render_template('hospital_details.html',)




@app.route('/add_doc',methods=['POST','GET'])
# @token_required('admin')
@login_required('admin')
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
        #Doctor and hospital relation
        session['doctor_name']=name
        admin_email=session['username']
        hospital_data=admin_collection.find_one({"hospital_mail":admin_email})
        hospital_name_doctor=hospital_data.get("hospital_name")
        session['hospital_name']=hospital_name_doctor
        # print(hospital_name_patient)
        doctor_data={
            'name':name,
            'specialization':specialization,
            'qualification':qualification,
            'email':email,
            'username':username,
            'password':hash_password,
            'phone':phone,
            'aadhar':aadhar,
            "hospital_name":hospital_name_doctor
        }
        if doctors_collection.find_one({'username':username}):
            return redirect('/add_doc')
        else:
            doctors_collection.insert_one(doctor_data)
        return render_template('add doc.html')
    return render_template('add doc.html')

@app.route('/doctor_login', methods=['POST', 'GET'])
def doc_login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        
        # Fetch the doctor's details from the database by username
        doctor = doctors_collection.find_one({'username': username})
        # print(username,password)
        if doctor:
            # stored_hash = doctor['password']  # The stored hashed password
            
            # Check if the provided password matches the hashed passwor
            if bcrypt.check_password_hash(doctor['password'],password):
                # Password matches, grant access
                # Store doctor ID in session
                doctor_data=doctors_collection.find_one({'username':username})

                session['username']=username
                session['hospital_name']=doctor_data.get('hospital_name')
                session['specialization']=doctor_data.get('specialization')
                session['role']='doc'
                return redirect('/doctor_app') # Redirect to the doctor app

            else:
                # Password does not match
                # flash('Invalid username or password', 'error')
                return "wrong password"
        else:
            # Username not found
            flash('Invalid username or password', 'error')
            return "Wrong id"

    # Render the login page if GET request
    return render_template('doctor login.html')  # Replace with your login template






@app.route('/doctor_app',methods=["POST","GET"])
@login_required('doc')
def doctor_app():
    appointments=appointment_collection.find({'hospital_name':session.get('hospital_name'),'speciality':session.get('specialization')})
    doc_detail = doctors_collection.find_one({'username':session.get('username')})
    return render_template('doctor_dash.html',appointments=appointments,doctor=doc_detail)

@app.route('/superadmin/', methods=['GET', 'POST'])
@login_required('superadmin')
def superadmin():
    # Count the total number of hospitals, doctors, and active patients
    no_of_hospital = hospital_data_collection.count_documents({})
    total_doctor = doctors_collection.count_documents({})
    active_patient = patients_collection.count_documents({})

    # Aggregate the total number of beds, ICU beds, and ventilators
    total_beds = hospital_data_collection.aggregate([
        {"$group": {"_id": None, "total_beds": {"$sum": "$number_of_beds"}}}
    ]).next()['total_beds']

    total_icu_beds = hospital_data_collection.aggregate([
        {"$group": {"_id": None, "total_icu_beds": {"$sum": "$number_of_icu_beds"}}}
    ]).next()['total_icu_beds']

    total_ventilators = hospital_data_collection.aggregate([
        {"$group": {"_id": None, "total_ventilators": {"$sum": "$number_of_ventilators"}}}
    ]).next()['total_ventilators']

    # Debugging prints (can be removed in production)
    print(total_ventilators, total_beds, total_icu_beds)

    # Render the template with the computed values
    return render_template('super_admin_dash.html', 
                           no_hospital=no_of_hospital, 
                           doctor=total_doctor, 
                           patient=active_patient, 
                           total_beds=total_beds, 
                           total_icu_beds=total_icu_beds, 
                           total_ventilators=total_ventilators)


@app.route("/superadmin_login", methods=['GET', 'POST'])
def superadmin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print('hello')
        # Check if the username and password match an entry in the admin_collection
        if superadmin_collection.find_one({"username": username, "password": password}):
            print('hello')
            session['username']=username
            session['role']='superadmin'
            return redirect('/superadmin')
        else:
            return redirect('/superadmin_login')
    
    return render_template("Super_Admin_login.html")


@app.route('/superadmin/addHospital', methods=['GET', 'POST'])
@login_required('superadmin')
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
    return render_template('super_add_hospital.html')
    
    
@app.route('/superadmin/checkHospitalStatus', methods=['GET', 'POST'])
@login_required('superadmin')
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

@app.route('/admin/discharge',methods=['POST','GET'])
@login_required('admin')
def submit_discharge():
    if request.method=='POST':
    # Extracting form data
        patient_id = request.form.get('patient_id')
        patient_name = request.form.get('patient_name')
        admission_date = request.form.get('admission_date')
        discharge_date = request.form.get('discharge_date')
        diagnosis = request.form.get('diagnosis')
        treatment = request.form.get('treatment')
        doctor_name = request.form.get('doctor_name')
        discharge_summary = request.form.get('discharge_summary')
        follow_up_instructions = request.form.get('follow_up_instructions')
        medications = request.form.get('medications')
        contact_info = request.form.get('contact_info')
        gender=request.form.get('gender')
        address=request.form.get('address')
        data_discharge={
            'patient_id': patient_id,
            'patient_name': patient_name,
            'admission_date': admission_date,
            'discharge_date': discharge_date,
            'diagnosis': diagnosis,
            'treatment': treatment,
            'doctor_name': doctor_name,
            'discharge_summary': discharge_summary,
            'follow_up_instructions': follow_up_instructions,
            'medications': medications,
            'contact_info': contact_info
        }
        hospital_discharge_collection.insert_one(data_discharge)
        # Generate PDF with the provided details
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        #Patient details inside the pdf
        elements = []
        elements.append(Paragraph("Patient ID Card", styles['Title']))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Full Name: {patient_name}", styles['Normal']))
        elements.append(Paragraph(f"Admission Date: {admission_date}", styles['Normal']))
        elements.append(Paragraph(f"Gender: {gender}", styles['Normal']))
        elements.append(Paragraph(f"Address: {address}", styles['Normal']))
        elements.append(Paragraph(f"Phone Number: {contact_info}", styles['Normal']))
        elements.append(Paragraph(f"Diagnosis: {diagnosis}", styles['Normal']))
        elements.append(Paragraph(f"Discharge Summary: {discharge_summary}", styles['Normal']))

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(
            f"Name: {patient_name}\Admission Date: {admission_date}\nPhone: {contact_info}\nDischarge Summary: {diagnosis}")
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        qr_buffer = io.BytesIO()
        img.save(qr_buffer, 'PNG')
        qr_buffer.seek(0)

        # Add QR code to PDF
        elements.append(Spacer(1, 12))
        elements.append(Image(qr_buffer, width=100, height=100))

        doc.build(elements)

        pdf_buffer.seek(0)
        return send_file(pdf_buffer, as_attachment=True, download_name='patient_id_card.pdf', mimetype='application/pdf')
        # return redirect('/admin') 
    return render_template('Patient_discharge.html')
#where is the change


#show
@app.route('/user_logout')
def user_logout():
    session.clear()
    return redirect('/')

@app.route('/admin_logout')
def admin_logout():
    session.clear()
    return redirect('/')
@app.route('/superadmin_logout')
def sueperadmin_logout():
    session.clear()
    return redirect('/')
@app.route('/doc_logout')
def doc_logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run( port=8000,debug=True)