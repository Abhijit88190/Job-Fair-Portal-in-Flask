from flask import Flask, request, render_template, redirect,  make_response, url_for, flash, jsonify
from flask import Flask, session
import psycopg2
import os
import hashlib
from werkzeug.utils import secure_filename
import uuid
import  pdfkit
from flask import send_from_directory
from flask import send_file
from datetime import timedelta
import random
import string




app = Flask(__name__)
sessions = {}
app.secret_key= 'f6b72e518851ab934ccdecee3e3a5d7b'


# PostgreSQL database configuration
conn = psycopg2.connect(
    dbname="Job_Portal",
    user="postgres",
    password="A1234",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Function to connect to PostgreSQL database
def connect_to_db():
    return psycopg2.connect(
        dbname="Job_Portal",
        user="postgres",
        password="A1234",
        host="localhost",
        port="5432"
    )
    

# Define the upload folder
UPLOAD_FOLDER = 'profile_pictures'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=180)  # Extend session lifetime to 30 minutes


wkhtmltopdf_path = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

# Generate a random captcha string
def generate_captcha():
    characters = string.ascii_letters + string.digits
    captcha = ''.join(random.choice(characters) for i in range(6))
    return captcha

# Function to hash the password using SHA256
# def hash_password(password):
#     return hashlib.sha256(password.encode()).hexdigest()  
def hash_password(password):
    """Hashes the given password using SHA-256."""
    if password is None:
        return None
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password

# Function to generate a salt
def generate_salt():
    return os.urandom(32)

# Function to hash the password using SHA256
def hash_password_salt(password, salt):
    return hashlib.sha256(password.encode() + salt).hexdigest()  


# for open the Home page of the Project #
@app.route('/')
def home():
    return render_template('Home_Page.html')


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form['password']
        confirm_password = request.form['confirmPassword']
        conn = connect_to_db()
        cur = conn.cursor()
        if new_password != confirm_password:
            flash('Passwords do not match.')
        else:
            # Update the password in the database
            try:
                cur.execute("UPDATE jobseeker_register SET password = %s WHERE email = %s", (new_password, email))
                conn.commit()
                flash('Password reset successfully.')
            except psycopg2.Error as e:
                conn.rollback()
                flash('Error resetting password: {}'.format(str(e)))
    return render_template('Forgot_Password.html')



# for register the Employer first time #
@app.route('/employer_register', methods=['GET', 'POST'])
def employer_register():
    if request.method == 'POST':
        try:
            organization_name = request.form['organizationName']
            established_on = request.form['establishedOn']
            about_company = request.form['aboutCompany']
            address = request.form['address']
            mobile = request.form['mobile']
            telephone = request.form['telephone']
            email = request.form['email']
            website = request.form['website']
            password = request.form['password']
            confirm_password = request.form['confirmPassword']

            if password != confirm_password:
                flash('Passwords do not match. Please try again.', 'error')
                return redirect(url_for('employer_register'))

            cursor.execute("INSERT INTO employer_register (organization_name, established_on, about_company, address, mobile, telephone, email, website, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (organization_name, established_on, about_company, address, mobile, telephone, email, website, password))
            conn.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('employer_register'))
        except Exception as e:
            conn.rollback()
            flash(f'Error: {e}', 'error')
            return redirect(url_for('employer_register'))
    return render_template('Employer_register_form.html')


# register for Jobseeker first time #
@app.route('/jobseeker_register', methods=['GET', 'POST'])
def jobseeker_register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password=request.form['confirmPassword']
        
        if password != confirm_password:
                flash('Passwords do not match. Please try again.', 'error')
                return redirect(url_for('jobseeker_register'))
        
        try:
            conn = connect_to_db()
            cur = conn.cursor()
            cur.execute("SELECT * FROM jobseeker_register WHERE email = %s", (email,))
            result = cur.fetchone()

            if result:
                flash('Email ID already registered!', 'error')
            else:
                cur.execute("INSERT INTO jobseeker_register (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
                conn.commit()
                flash('Registration successful!', 'success')
                return redirect(url_for('jobseeker_register'))
        except Exception as e:
            flash('An error occurred. Please try again.', 'error')
        finally:
            cur.close()
            conn.close()
    return render_template('Jobseeker_register_form.html')

    
    
# open the login.html page #
@app.route('/login')
def login_page():
    return render_template('Login.html')

# Function to serve profile pictures
@app.route('/profile_pictures/<filename>')
def profile_picture(filename):
    return send_from_directory('profile_pictures', filename)

#for login all types of users #
@app.route('/login', methods=['GET', 'POST'])
def login():
    
    if request.method == 'POST':
        role=request.form['role']
        email = request.form['email']
        password = request.form['password']
        hashed_pwd = hash_password(password)
        conn = None
        cur = None
        conn = connect_to_db()
        cur = conn.cursor()
        if role =='Jobseeker':
            try:
                conn = connect_to_db()
                cur = conn.cursor()
                cur.execute("SELECT * FROM jobseeker_register WHERE email = %s AND password = %s", (email, password))
                result_jobseeker = cur.fetchone()
                if result_jobseeker :
                    session['email'] = email  # Store the email in the session
                    session['name'] = result_jobseeker[1]
                    # Fetch profile picture path from jobseeker_personal_info table
                    cur.execute("SELECT profile_picture_path FROM jobseeker_personal_info WHERE email = %s", (email,))
                    profile_picture_path = cur.fetchone()[0] if cur.rowcount > 0 else None

                    if profile_picture_path and os.path.exists(profile_picture_path):
                        session['image_url'] = url_for('profile_picture', filename=os.path.basename(profile_picture_path))
                    else:
                        session['image_url'] = None
                    
                    # Redirect to jobseeker dashboard
                    return  redirect(url_for('jobseeker_form'))
                else:
                    flash('Invalid email or password', 'error')
            finally:
                cur.close()
                conn.close()

        elif role == 'Employer':
            try:
                conn = connect_to_db()
                cur = conn.cursor()
                cur.execute("SELECT * FROM employer_register WHERE email = %s AND password = %s", (email, password))
                result_emp = cur.fetchone()
                if result_emp :
                    session['email'] = email  # Store the email in the session
                    session['name'] = result_emp[1]
                    return  redirect(url_for('employer_form'))
                else:
                    flash('Invalid email or password', 'error')
            finally:
                cur.close()
                conn.close()

        elif role == 'DEO':
            try:
                conn = connect_to_db()
                cur = conn.cursor()
                cur.execute("SELECT * FROM deo_info WHERE email = %s AND password = %s", (email, password))
                result_deo = cur.fetchone()
                print(result_deo)
                if result_deo :
                    session['email'] = email  # Store the email in the session
                    session['name'] = result_deo[1]
                    session['designation'] = result_deo[5]
                    return  redirect(url_for('deo_dashboard'))
                else:
                    flash('Invalid email or password', 'error')
            finally:
                cur.close()
                conn.close()
                
                
        elif role == 'PIA':
            try:
                conn = connect_to_db()
                cur = conn.cursor()
                cur.execute("SELECT password FROM pia_info WHERE email = %s;", (email,))
                result_pia = cur.fetchone()
                salt = generate_salt()
                if result_pia :
                    stored_hashed_pwd = hash_password_salt(result_pia[0],salt)
                    print("my DB Password is :",stored_hashed_pwd)
                    # Hash the entered password with the retrieved salt
                    hashed_pwd = hash_password_salt(hashed_pwd, salt)
                    print("Login Password is:",hash_password)
                    

                    cur.execute("SELECT * FROM pia_info WHERE email = %s", (email,))
                    result_pia = cur.fetchone()
                    
                    session['consultancyName'] = result_pia[1]
                    # Debug prints
                    # print("Consultancy Name:", session.get('consultancyName'))
                    # print("Email before setting in session:", session.get('email'))
                    session['email'] = email
                    # print("Email after setting in session:", session.get('email'))


                    if hashed_pwd == stored_hashed_pwd:
                        session['email'] = email  # Store the email in the session 
                        # session['consultancyName'] = result_pia[1]
                        return render_template('change_password.html', role='PIA')
                    else:
                        flash('Invalid email or password')
                        return render_template('PIA_form.html')
                    # if result_pia[4]==password:
                    #     return render_template('change_password.html', role='PIA')
                    # else:
                    #     return render_template('PIA_form.html')
                    
                else:
                    flash('Invalid email or password', 'error')
            finally:
                cur.close()
                conn.close()
    session.modified = True    
    return render_template('login.html')


# for open the DEO dashboard form page #
@app.route('/deo_dashboard')
def deo_dashboard():
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM pia_info")
    pia_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM employer_register")
    employer_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM jobseeker_personal_info")
    jobseeker_count = cur.fetchone()[0]
    
    conn.close()
    return render_template('DEO_Dashboard.html', pia_count=pia_count, employer_count=employer_count, jobseeker_count=jobseeker_count)



@app.route('/deo_profile')
def deo_profile():
    try:
        # Connect to the database
        conn = connect_to_db()
        cursor = conn.cursor()
        # Execute a query to fetch DEO information
        cursor.execute("SELECT name, email, phone FROM deo_info")
        # Fetch all rows from the result set
        deo_info = cursor.fetchall()
        # Close the cursor and connection
        cursor.close()
        conn.close()
        # Render the profile template with the fetched DEO information
        return render_template('DEO_Profile.html', deo_info=deo_info)
    except psycopg2.Error as e:
        # Handle any database errors
        print("Error fetching DEO information:", e)
        # Return an error message or redirect to an error page
        return "Error fetching DEO information", 500  # HTTP status code 500 indicates internal server error
    


    # conn = connect_to_db()
    # cur = conn.cursor()
    # cur.execute("SELECT COUNT(*) FROM pia_info")
    # pia_count = cur.fetchone()[0]
    
    # cur.execute("SELECT COUNT(*) FROM employer_register")
    # employer_count = cur.fetchone()[0]
    
    # cur.execute("SELECT COUNT(*) FROM jobseeker_personal_info")
    # jobseeker_count = cur.fetchone()[0]
    
    # conn.close()
    # return render_template('PIA_form.html', pia_count=pia_count, employer_count=employer_count, jobseeker_count=jobseeker_count)

# @app.route('/pia_register_form')
# def pia_register_form():
#     return render_template('PIA_Register.html')  

# @app.route('/deo_pia_register')
# def deo_pia_register():
#     return render_template('DEO_PIA_Register.html')  

def store_registration_data(consultancy_name, contact_person, email, contact_number, website, address, hashed_pwd):
    conn = connect_to_db()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO pia_info (consultancy_name, contact_person, email, contact_number, website_link, address, password) VALUES (%s, %s, %s, %s, %s, %s, %s)''', (consultancy_name, contact_person, email, contact_number, website, address, hashed_pwd))
            conn.commit()
            print("PIA registered successfully!")
        except psycopg2.Error as e:
            print("Error storing registration data:", e)
        finally:
            cursor.close()
            conn.close()


@app.route('/deo_pia_register', methods=['POST', 'GET'])
def deo_pia_register():
    consultancy_name = request.form.get('consultancyName')
    contact_person = request.form.get('contactPerson')
    email = request.form.get('email')
    contact_number = request.form.get('contactNumber')
    website = request.form.get('website')
    address = request.form.get('address')
    password = request.form.get('password')
    confirm_password = request.form.get('confirmPassword')
    hashed_pwd = hash_password(password)

    # Check if any required fields are missing
    if None in [consultancy_name, contact_person, email, contact_number, website, address, password, confirm_password]:
        flash('Please fill out all required fields.', 'error')
        return render_template('DEO_PIA_Register.html')

    # Check if passwords match
    if password != confirm_password:
        flash('Passwords do not match. Please try again.', 'error')
        return render_template('DEO_PIA_Register.html')

    # Store the registration data in the database
    store_registration_data(consultancy_name, contact_person, email, contact_number, website, address, hashed_pwd)

    # Redirect to the success template
    flash('Registration successful!', 'success')
    return render_template('DEO_PIA_Register.html')

    

@app.route('/change_passwords')
def change_passwords():
    return render_template('Change_Password.html')

@app.route('/change_password', methods=['POST'])
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        # hashed_pwd = hash_password(new_password)
        conn = connect_to_db()
        cursor = conn.cursor()

        try:
            # Retrieve the current user's password from the database
            cursor.execute("SELECT password FROM pia_info WHERE contact_number = %s", (current_password,))
            user_password = cursor.fetchone()

            if not user_password:
                return "Current password is incorrect."

            if new_password == current_password:
                return "New password must be different from the current password."
            elif new_password != confirm_password:
                return "New password and confirm password do not match."

            # Update the password in the database
            cursor.execute("UPDATE pia_info SET password = %s WHERE contact_number = %s", (new_password, current_password))
            conn.commit()
            return render_template('login.html')
        except psycopg2.Error as e:
            print("Error while updating password:", e)
            return "Error occurred while updating password."
        finally:
            if conn:
                cursor.close()
                conn.close()

    return render_template('login.html', role='PIA')

    

# Route for viewing PIA List
@app.route('/pia_list')
def pia_list():
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pia_info")
        pia_data = cursor.fetchall()  # Fetch all rows from the query result
        conn.close()
        return render_template('PIA_List.html', pia_data=pia_data)
    except Exception as e:
        # Handle exceptions (e.g., connection errors, query errors)
        return "An error occurred: " + str(e)



# for open the Employer dashboard form page #
@app.route('/employer_form')
def employer_form():
    if 'email' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in
    
    user_email = session['email']
    
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute('SELECT organization_name, established_on, telephone, website, email FROM employer_register WHERE email = %s', (user_email,))
    employers = cursor.fetchall()
    cursor.close()
    conn.close()
    
    
    return render_template('Employer_form.html', employers=employers)



@app.route('/employers_lists')
def employers_lists():
    return render_template('Employer_Lists.html')

@app.route('/employer_lists')
def employer_lists():
    try:
        cursor.execute("SELECT * FROM employer_register ORDER BY id ASC ")
        data = cursor.fetchall()
        return render_template('Employer_Lists.html', data=data)
    except psycopg2.Error as e:
        flash(f'Error fetching data: {e}', 'error')
        return render_template('Employer_Lists.html', data=[])


@app.route('/employer_list')
def employer_list():
    try:
        cursor.execute("SELECT * FROM employer_register ORDER BY id ASC")
        data = cursor.fetchall()
        return render_template('Employer_List.html', data=data)
    except psycopg2.Error as e:
        flash(f'Error fetching data: {e}', 'error')
        return render_template('Employer_List.html', data=[])
    
    
    
@app.route('/employer_details/<int:employer_id>')
def employer_details(employer_id):
    try:
        cursor.execute("SELECT * FROM employer_register WHERE id = %s", (employer_id,))
        employer_data = cursor.fetchone()
        if employer_data:
            return render_template('Employer_Details.html', employer_data=employer_data)
        else:
            flash('Employer not found.', 'error')
            return redirect(url_for('employer_list'))
    except psycopg2.Error as e:
        flash(f'Error: {e}', 'error')
        return redirect(url_for('employer_list'))
    
@app.route('/employers_details_approve/<int:employer_id>')
def employer_details_approve(employer_id):
    try:
        cursor.execute("SELECT * FROM employer_register WHERE id = %s", (employer_id,))
        employer_data = cursor.fetchone()
        if employer_data:
            return render_template('Employers_Details_Approve.html', employer_data=employer_data)
        else:
            flash('Employer not found.', 'error')
            return redirect(url_for('employer_lists'))
    except psycopg2.Error as e:
        flash(f'Error: {e}', 'error')
        return redirect(url_for('employer_lists'))   

@app.route('/update_flag', methods=['POST'])
def update_flag():
    organization_name = request.form['organization_name']
    flag = request.form['flag']

    try:
        cursor.execute("UPDATE employer_register SET status = %s WHERE organization_name = %s", (flag, organization_name))
        conn.commit()
        
    except psycopg2.Error as e:
        conn.rollback()
        flash(f'Error: {e}', 'error')

    return redirect(url_for('deo_employer_table'))

# for open the Jobseeker dashboard form page #
@app.route('/jobseeker_form')
def jobseeker_form():
    image_url = None  # Initialize image_url to None
    
    try:
        if 'email' in session:
            email = session['email']
            cursor.execute("SELECT name, phone_number, gender, dob, email FROM jobseeker_personal_info WHERE email = %s", (email,))
            jobseeker_details = cursor.fetchone()
            if jobseeker_details:
                name, phone_number, gender, dob, email = jobseeker_details
                
                # Count how many times the candidate's name appears in the jobseeker_personal_info table
                cursor.execute("SELECT COUNT(*) FROM jobseeker_personal_info WHERE name = %s", (name,))
                count = cursor.fetchone()[0]  # Fetch the count value
                print("Applied Count:", count)  # Print the count value

                # Get profile picture URL
                image_url = session.get('image_url')
                print("img_url IS :",image_url)

                # Pass the details, count value, and profile picture URL to the template
                return render_template('jobseeker_form.html',name=name,phone_number=phone_number, gender=gender, dob=dob, email=email,image_url=image_url)
            else:
                flash('Job seeker details not found.', 'error')
        else:
            flash('Session expired. Please log in again.', 'error')
            return redirect(url_for('login'))  # Redirect to login page if session is expired
    except psycopg2.Error as e:
        flash('An error occurred: {}'.format(str(e)), 'error')
        return redirect(url_for('login'))

    # If no jobseeker details found or session expired, render the form with image_url as None
    return render_template('jobseeker_form.html', image_url=session.get('image_url'))


# for open the Jobseeker form fill up page #
@app.route('/jobseeker_personal_form')
def jobseeker_personal_form():
    return render_template('Jobseeker_Personal_Form.html')


# Modify the personal_info route to handle profile picture upload and store the file path
@app.route('/personal_info', methods=['POST'])
def personal_info():
    if request.method == 'POST':
        name = request.form['name']
        gender = request.form['gender']
        dob = request.form['dob']
        email = request.form['email']
        phone_number = request.form['phone_number']
        address = request.form['address']
        if not phone_number.isdigit() or len(phone_number) != 10:
            error_message = 'Phone number must be exactly 10 digits long and contain only numbers.'
            flash(error_message, 'error')
            return redirect(url_for('jobseeker_personal_form'))

        if 'profile_picture' in request.files:
            profile_picture = request.files['profile_picture']
            if profile_picture.filename != '':
                filename = secure_filename(profile_picture.filename)
                profile_picture_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                profile_picture.save(profile_picture_path)
                session['profile_picture_path'] = profile_picture_path
                session['image_url'] = url_for('profile_picture', filename=filename)

        try:
            # Generate unique application ID
            cursor.execute("SELECT MAX(application_id) FROM jobseeker_personal_info")
            max_id = cursor.fetchone()[0]
            if max_id is None:
                application_id = 10000
            else:
                application_id = max_id + 1

            # Store application ID in session
            session['application_id'] = application_id

            # Save the data to PostgreSQL
            cursor.execute("INSERT INTO jobseeker_personal_info (application_id, phone_number, name, gender, dob, email, address, profile_picture_path) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (application_id, phone_number, name, gender, dob, email, address, profile_picture_path))
            conn.commit()

            # Redirect to the academic info form first
            return redirect(url_for('jobseeker_academic_form'))

        except psycopg2.Error as e:
            print("Error inserting personal info:", e)
            flash('An error occurred while saving data.', 'error')
    
    # If the request method is not POST or there is an error, redirect to the personal info form
    return redirect(url_for('jobseeker_personal_form'))

@app.route('/generate_pdf/<int:application_id>')
def generate_pdf_report(application_id):
    try:
        cursor = conn.cursor()
        # Fetch personal information based on application_id
        cursor.execute("SELECT * FROM jobseeker_personal_info WHERE application_id = %s", (application_id,))
        personal_info = cursor.fetchone()

        # Generate HTML content for personal information
        html_content = '<h1>Personal Information</h1>'
        if personal_info is not None:
            html_content += f'<p><strong>Name:</strong> {personal_info[2]}</p>'
            html_content += f'<p><strong>Gender:</strong> {personal_info[3]}</p>'
            html_content += f'<p><strong>Date of Birth:</strong> {personal_info[4]}</p>'
            html_content += f'<p><strong>Email:</strong> {personal_info[5]}</p>'
            html_content += f'<p><strong>Phone Number:</strong> {personal_info[6]}</p>'
            html_content += f'<p><strong>Address:</strong> {personal_info[7]}</p>'
        else:
            html_content += '<p>No personal information available.</p>'
        
        # Generate PDF
        pdfkit.from_string(html_content, f'personal_info_{application_id}.pdf', configuration=config)

        # Serve PDF for download
        return send_file(f'personal_info_{application_id}.pdf', as_attachment=True)
    except psycopg2.Error as e:
        print("Error generating PDF report:", e)
        return "An error occurred while generating the PDF report."
    finally:
        if cursor:
            cursor.close()


@app.route('/jobseeker_academic_form')
def jobseeker_academic_form():
    # Here you can render your Jobseeker_Academic_Form.html template
    return render_template('Jobseeker_Academic_Form.html')

@app.route('/academic_info', methods=['POST'])
def academic_info():
    if request.method == 'POST':
        # Retrieve academic information from the form
        qualifications = request.form.getlist('course[]')  # Get list of courses
        boards = request.form.getlist('board[]')
        years = request.form.getlist('year[]')
        total_marks = request.form.getlist('totalMarks[]')
        secured_marks = request.form.getlist('securedMarks[]')
        percentages = request.form.getlist('percentage[]')
        
        # Retrieve application ID from the session
        application_id = session.get('application_id')
        if not application_id:
            # If application ID is not found in session, redirect to personal_info page
            return redirect('/personal_info')

        # Save academic information to PostgreSQL
        for i in range(len(qualifications)):
            # Convert percentage to float or set to None if empty
            percentage = percentages[i]
            if percentage:
                percentage = float(percentage)
            else:
                percentage = None  # Or any other default value you prefer
            
            # Insert data into the database
            cursor.execute("INSERT INTO jobseeker_academic_info (application_id, qualification, board_university, year_of_passing, total_marks, secured_marks, percentage) VALUES (%s, %s, %s, %s, %s, %s, %s)", (application_id, qualifications[i], boards[i], years[i], total_marks[i], secured_marks[i], percentage))
        conn.commit()

        # After storing academic information, redirect to display the image
        # return redirect(url_for('display_image'))
            
    return redirect(url_for('jobseeker_form'))

# def get_profile_picture_url():
#     # Here, you need to implement the logic to retrieve the profile picture URL
#     # This could involve querying the database or accessing the file system
#     # Return the URL of the profile picture if found, or None if not found
#     # For example:
#     if 'application_id' in session:
#         application_id = session['application_id']
#         cursor.execute("SELECT profile_picture_path FROM jobseeker_personal_info WHERE application_id = %s", (application_id,))
#         profile_picture_path = cursor.fetchone()
#         if profile_picture_path:
#             return url_for('Jobseeker_form.html', filename=profile_picture_path[0])
#     return None


@app.route('/jobseeker_display_data', methods=['GET','POST'])
def jobseeker_display_data():
    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        # Retrieve data from the database
        cursor.execute("SELECT * FROM jobseeker_personal_info")
        jobseeker_personal_info = cursor.fetchall()
        # Render the data in an HTML table
        return render_template('Jobseeker_Display_Data.html', jobseekers=jobseeker_personal_info)
    except Exception as e:
        flash('An error occurred: {}'.format(str(e)), 'error')
        return redirect(url_for('login'))  # Redirect to login page or handle error as needed


    
# Route for profile display page
@app.route('/jobseeker_profile')
def jobseeker_profile():
    # Check if user is logged in
    if 'email' not in session:
        return redirect(url_for('login'))

    # Fetch student's profile info from the database
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT  name, phone_number, email FROM jobseeker_personal_info WHERE email = %s", (session['email'],))
    profile_info = cursor.fetchone()

    return render_template('Jobseeker_Profile.html', profile_info=profile_info)

    
    
@app.route('/jobseeker_edit_profile')
def jobseeker_edit_profile():
    # Fetch student's profile info from the session or database
    # For demonstration, assume profile_info is fetched from the session
    profile_info = session.get('profile_info')

    return render_template('Jobseeker_Edit_Profile.html', profile_info=profile_info)


@app.route('/jobseeker_update_profile', methods=['POST'])
def jobseeker_update_profile():
    # Get form data
    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']

    # Update profile info in the session or database
    # For demonstration, assume profile_info is updated in the session
    profile_info = session.get('profile_info')
    if profile_info is None:
        # Initialize profile_info if it's None
        profile_info = [name, phone, email]
    else:
        # Update existing profile_info
        profile_info[0] = name
        profile_info[1] = phone
        profile_info[2] = email
    session['profile_info'] = profile_info


    # try:
    #     conn = connect_to_db()
    #     cur = conn.cursor()
    #     cur.execute("UPDATE jobseeker_personal_info SET name = %s, phone = %s WHERE email = %s", (name, phone, email))
    #     conn.commit()  # Commit the changes
    #     flash('Profile updated successfully', 'success')
    # except Exception as e:
    #     flash('An error occurred while updating profile. Please try again.', 'error')
    # finally:
    #     cur.close()
    #     conn.close()
    return redirect(url_for('jobseeker_profile'))



@app.route('/PIA_jobseeker_register', methods=['GET', 'POST'])
def PIA_jobseeker_register():
    return render_template('PIA_Jobseeker_register_form.html')



# Route to handle expressing interest
@app.route('/express_interest', methods=['POST'])
def express_interest():
    try:
        # Get jobseeker's email address from the session
        email = session.get('email')
        
        # Ensure email is not empty
        if not email:
            return "Error: Email is missing from session"
        
        # Open a cursor to perform database operations
        cursor = conn.cursor()
        
        # Fetch jobseeker's ID and name from personal info using the email
        cursor.execute("SELECT application_id, name FROM jobseeker_personal_info WHERE email = %s", (email,))
        personal_info = cursor.fetchone()
        # Ensure both personal and academic info exist for the provided email
        if not personal_info :
            return "Error: Jobseeker information not found"
        
        # Extract jobseeker's ID and name from either personal or academic info
        jobseeker_id, jobseeker_name = personal_info 
        
        # Get selected organization IDs from the form data
        selected_organizations = request.form.getlist('selected_organizations[]')
    
        # Insert jobseeker's interest into the table
        for organization_id in selected_organizations:
            # Fetch organization name from the database
            cursor.execute("SELECT organization_name, email FROM employer_register WHERE id = %s", (organization_id,))
            organization_data = cursor.fetchone()

            # Ensure organization data is not empty
            if not organization_data:
                return "Error: Organization information not found"

            # Extract organization name and email
            organization_name, organization_email = organization_data
            # Insert data into jobseeker_interest table
            cursor.execute('''INSERT INTO jobseeker_interest (jobseeker_id, jobseeker_name, organization_id, organization_name,organization_email) VALUES (%s, %s, %s, %s,%s)''', (jobseeker_id, jobseeker_name, organization_id, organization_name,organization_email))
        
        # Commit the transaction
        conn.commit()
        
        # Redirect to a success page or back to the home page
        return render_template('Jobseeker_form.html')
    
    except Exception as e:
        conn.rollback()  # Rollback changes if an exception occurs
        return f"Error: {e}"

    finally:
        if cursor:
            cursor.close()


# Route to handle viewing jobseeker details for a specific employer
@app.route('/employer_jobseeker_details')
def employer_jobseeker_details():
    try:
        # Get employer's email address from the session
        employer_email = session.get('email')
        # Ensure email is not empty
        if not employer_email:
            return "Error: Employer email is missing from session"
        
        # Open a cursor to perform database operations
        cursor = conn.cursor()
        
        # Fetch employer's details including their ID using the email
        cursor.execute("SELECT id FROM employer_register WHERE email = %s", (employer_email,))
        employer_data = cursor.fetchone()
        
        # Ensure employer data is not empty
        if not employer_data:
            return "Error: Employer information not found"
        
        # Extract employer's ID
        employer_id = employer_data[0]
        
        # Fetch jobseeker details associated with the employer from jobseeker_interest table
        cursor.execute("SELECT * FROM jobseeker_interest WHERE organization_email = %s", (employer_email,))
        jobseeker_details = cursor.fetchall()
        
        # Check if any jobseeker details are found
        if not jobseeker_details:
            return "No jobseeker details found for this employer"
        
        # Render a template to display jobseeker details to the employer
        return render_template('Employer_Jobseeker_details.html', jobseeker_details=jobseeker_details)
    
    except Exception as e:
        return f"Error: {e}"

    finally:
        if cursor:
            cursor.close()
            
            
# Route to handle viewing jobseeker academic info
@app.route('/view_academic_info/<int:jobseeker_id>')
def view_academic_info(jobseeker_id):
    try:
        # Open a cursor to perform database operations
        cursor = conn.cursor()

        # Fetch jobseeker's academic info from the database
        cursor.execute("SELECT * FROM jobseeker_academic_info WHERE application_id = %s", (jobseeker_id,))
        academic_infos = cursor.fetchall()
        

        # Render the template with the academic info
        return render_template('jobseeker_academic_info.html', academic_infos=academic_infos)
    
    except Exception as e:
        return f"Error: {e}"

    finally:
        if cursor:
            cursor.close()

# Route to handle updating jobseeker status
@app.route('/update_status_jobseeker', methods=['POST'])
def update_status_jobseeker():
    try:
        # Get employer's email from the session
        employer_email = session.get('email')
        print(employer_email)
        # Ensure email is not empty
        if not employer_email:
            return jsonify({'error': 'Employer email is missing from session'}), 400
        # Get jobseeker ID and status from the request data
        data = request.json
        jobseeker_id = data['jobseekerId']
        status = data['status']
        print(status)

        # Open a cursor to perform database operations
        cursor = conn.cursor()

        # Update jobseeker status in the database
        cursor.execute("UPDATE jobseeker_interest SET status = %s WHERE jobseeker_id = %s AND organization_email= %s", (status, jobseeker_id,employer_email))
        conn.commit()

        # Close the cursor
        cursor.close()

        response = {'message': 'Status updated successfully'}
        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
# Route to handle the AJAX request to update Interview_status
@app.route('/update_interview_status', methods=['POST'])
def update_interview_status():
    try:
        # Get employer's email address from the session
        employer_email = session.get('email')
        
        # Ensure email is not empty
        if not employer_email:
            return jsonify({'message': 'Error: Employer email is missing from session'}), 400
        
        # Extract the interview status from the request data
        interview_status = request.json.get('interviewStatus')
        
        # Open a cursor to perform database operations
        cursor = conn.cursor()
        
        # Update the Interview_status column in employer_register table
        cursor.execute("UPDATE employer_register SET interview_status = %s WHERE email = %s", (interview_status, employer_email))
        
        # Commit the transaction
        conn.commit()
        
        # Close the cursor
        cursor.close()
        
        # Return a success message
        return jsonify({'message': 'Interview status updated successfully'}), 200
    
    except Exception as e:
        # Rollback changes if an exception occurs
        conn.rollback()
        return jsonify({'message': f'Error: {e}'}), 500
    
    
def insert_vacancy(employer_email,post_name, number_of_posts, eligibility, job_description, experience):
    """Insert vacancy data into the PostgreSQL database."""
    try:
        connection = connect_to_db()
        cursor = connection.cursor()

        # Retrieve employer_id based on employer_email from session
        cursor.execute("SELECT id FROM employer_register WHERE email = %s", (employer_email,))
        employer_id = cursor.fetchone()[0]

        # SQL query to insert data into the vacancy table
        sql_query = """
            INSERT INTO vacancy (employer_id, post_name, number_of_posts, eligibility, job_description, experience)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql_query, (employer_id, post_name, number_of_posts, eligibility, job_description, experience))
        
        connection.commit()
        print("Data inserted successfully!")
    except psycopg2.Error as e:
        print("Error inserting data into PostgreSQL database:", e)
    finally:
        cursor.close()
        connection.close()


@app.route('/submit_form', methods=['POST'])
def submit_form():
    """Handle form submission and insert data into the vacancy table."""
    if request.method == 'POST':
        employer_email = session.get('email')
        post_name = request.form.getlist('post_name[]')
        number_of_posts = request.form.getlist('number_of_posts[]')
        eligibility = request.form.getlist('eligibility[]')
        job_description = request.form.getlist('job_description[]')
        experience = request.form.getlist('experience[]')

        # Iterate over each vacancy and insert into the database
        for i in range(len(post_name)):
            insert_vacancy(employer_email,post_name[i], number_of_posts[i], eligibility[i], job_description[i], experience[i])

        return jsonify({'message': 'Vacancy data inserted successfully'})
    else:
        return jsonify({'message': 'Invalid request method'})



    
@app.route('/view_vacancies/<int:employer_id>')
def view_vacancies(employer_id):
    conn = connect_to_db()
    cur = conn.cursor()

# Handle the case where employer with the given email is not found

    # Fetch vacancies associated with the employer_id
    cur.execute("SELECT * FROM vacancy WHERE employer_id = %s", (employer_id,))
    vacancies = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('View_Vacancies.html', vacancies=vacancies)

@app.route('/fetch_jobseeker_data', methods=['GET'])
def fetch_jobseeker_data():
    try:
        employer_email= session.get('email')
        if not employer_email:
            return jsonify ({'message':'error: employer not found'}),400
        
        print(employer_email)
        conn = connect_to_db()
        cur = conn.cursor()
        
        
        # Query to get the count of registered job seekers
        cur.execute("SELECT COUNT(*) FROM jobseeker_register")
        registered_job_seekers_count = cur.fetchone()[0]
        print(registered_job_seekers_count)
        # Query to get the count of job seekers interested in this employer
        cur.execute("SELECT COUNT(*) FROM jobseeker_interest WHERE  organization_email = %s", (str(employer_email),))
        interested_job_seekers_count = cur.fetchone()[0]
        print(interested_job_seekers_count)
        return jsonify({
            'registeredJobSeekers': registered_job_seekers_count,
            'interestedJobSeekers': interested_job_seekers_count
        })
    except psycopg2.Error as e:
        return jsonify({'error': str(e)})
    finally:
        cur.close()

@app.route('/fetch_jobseeker_interest_data', methods=['GET'])
def fetch_jobseeker_interest_data():
    try:
        employer_email= session.get('email')
        if not employer_email:
            return jsonify ({'message':'error: employer not found'}),400
        
        print(employer_email)
        conn = connect_to_db()
        cur = conn.cursor()
        
        # Query to get the count of interested, selected, rejected, and waited job seekers
        cur.execute("SELECT COUNT(*) FROM jobseeker_interest WHERE organization_email = %s ", (str(employer_email),))
        interested_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM jobseeker_interest WHERE organization_email = %s AND status = 'S'", (str(employer_email),))
        selected_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM jobseeker_interest WHERE organization_email = %s AND status = 'R'", (str(employer_email),))
        rejected_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM jobseeker_interest WHERE organization_email = %s AND status = 'W'", (str(employer_email),))
        waited_count = cur.fetchone()[0]

        return jsonify({
            'interested': interested_count,
            'selected': selected_count,
            'rejected': rejected_count,
            'waited': waited_count
        })
    except psycopg2.Error as e:
        return jsonify({'error': str(e)})
    finally:
        cur.close()
        
# for logout the Jobseeker dashboard form page #
@app.route('/logout')
def logout():
    # Permanently invalidate the session
    session.pop('email', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))


@app.route('/templates/top-nav.html')
def top_nav():
    return render_template('top-nav.html')

@app.route('/templates/boxed.html')
def boxed():
    return render_template('boxed.html')

@app.route('/templates/fixed.html')
def fixed():
    return render_template('fixed.html')

@app.route('/templates/collapsed-sidebar.html')
def collapsed_sidebar():
    return render_template('collapsed-sidebar.html')

@app.route('/chartjs')
def chartjs():
    return render_template('chartjs.html')

@app.route('/morris')
def morris():
    return render_template('morris.html')

@app.route('/flot')
def flot():
    return render_template('flot.html')

@app.route('/inline')
def inline():
    return render_template('inline.html')

@app.route('/templates/generalui.html')
def generalui():
    return render_template('generalui.html')

@app.route('/templates/icons.html')
def icons():
    return render_template('icons.html')

@app.route('/templates/buttons.html')
def buttons():
    return render_template('buttons.html')

@app.route('/templates/sliders.html')
def sliders():
    return render_template('sliders.html')

@app.route('/templates/timeline.html')
def timeline():
    return render_template('timeline.html')

@app.route('/templates/modals.html')
def modals():
    return render_template('modals.html')


@app.route('/templates/generalformelements.html')
def general_form_elements():
    return render_template('generalformelements.html')

@app.route('/templates/advanced.html')
def advanced():
    return render_template('advanced.html')

@app.route('/templates/editors.html')
def editors():
    return render_template('editors.html')

@app.route('/templates/simple.html')
def simple():
    return render_template('simple.html')

@app.route('/templates/data.html')
def data():
    return render_template('data.html')


@app.route('/templates/invoice.html')
def invoice():
    return render_template('invoice.html')

@app.route('/templates/profile.html')
def profile():
    return render_template('profile.html')

@app.route('/templates/register.html')
def register():
    return render_template('register.html')

@app.route('/templates/lockscreen.html')
def lockscreen():
    return render_template('lockscreen.html')

@app.route('/templates/404.html')
def error404():
    return render_template('404.html')

@app.route('/templates/500.html')
def error500():
    return render_template('500.html')

@app.route('/templates/blank.html')
def blank():
    return render_template('blank.html')

@app.route('/templates/pace.html')
def pace():
    return render_template('pace.html')

@app.route('/deo_base')
def deo_base():
    return render_template('DEO_Base.html')

@app.route('/mailbox')
def mailbox():
    return render_template('mailbox.html')



@app.route('/deo_jobseeker_table', methods=['GET','POST'])
def deo_jobseeker_table():
    try:
        conn = connect_to_db()
        cursor = conn.cursor()

        # Retrieve data from the database
        cursor.execute("SELECT * FROM jobseeker_personal_info")
        jobseeker_personal_info = cursor.fetchall()
        # Render the data in an HTML table
        return render_template('DEO_Jobseeker_Table.html', jobseekers=jobseeker_personal_info)
    except Exception as e:
        flash('An error occurred: {}'.format(str(e)), 'error')
        return redirect(url_for('login'))  # Redirect to login page or handle error as needed
    
    
# @app.route('/deo_employer_table')
# def deo_employer_table():
#     return render_template('Deo_Employer_Table.html')

@app.route('/deo_employer_table')
def deo_employer_table():
    try:
        cursor.execute("SELECT * FROM employer_register ORDER BY id ASC ")
        data = cursor.fetchall()
        return render_template('Deo_Employer_Table.html', data=data)
    except psycopg2.Error as e:
        flash(f'Error fetching data: {e}', 'error')
        return render_template('Deo_Employer_Table.html', data=[])



@app.route('/deo_pia_table')
def deo_pia_table():
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pia_info")
        pia_data = cursor.fetchall()  # Fetch all rows from the query result
        conn.close()
        return render_template('DEO_PIA_Table.html', pia_data=pia_data)
    except Exception as e:
        # Handle exceptions (e.g., connection errors, query errors)
        return "An error occurred: " + str(e)
    
# @app.route('/deo_pia_register')
# def deo_pia_register():
#     return render_template('DEO_PIA_Register.html')

# def store_registration_data(consultancy_name, contact_person, email, contact_number, website, address, hashed_pwd):
#     conn = connect_to_db()
#     if conn is not None:
#         try:
#             cursor = conn.cursor()
#             cursor.execute('''INSERT INTO pia_info (consultancy_name, contact_person, email, contact_number, website_link, address, password) VALUES (%s, %s, %s, %s, %s, %s, %s)''', (consultancy_name, contact_person, email, contact_number, website, address, hashed_pwd))
#             conn.commit()
#             print("PIA registered successfully!")
#         except psycopg2.Error as e:
#             print("Error storing registration data:", e)
#         finally:
#             cursor.close()
#             conn.close()

# @app.route('/deo_pia_register', methods=['POST','GET'])
# def deo_pia_register():
#     consultancy_name = request.form['consultancyName']
#     contact_person = request.form['contactPerson']
#     email = request.form['email']
#     contact_number = request.form['contactNumber']
#     website = request.form['website']
#     address = request.form['address']
#     password = request.form['password']
#     confirm_password = request.form['confirmPassword']
#     hashed_pwd = hash_password(password)
    

#     # Check if passwords match
#     if password != confirm_password:
#         flash('Passwords do not match. Please try again.', 'error')
#         return render_template('DEO_PIA_Register.html')


@app.route('/deo_employers_details_approve/<int:employer_id>')
def deo_employer_details_approve(employer_id):
    try:
        cursor.execute("SELECT * FROM employer_register WHERE id = %s", (employer_id,))
        employer_data = cursor.fetchone()
        if employer_data:
            return render_template('DEO_Employers_Details_Approve.html', employer_data=employer_data)
        else:
            flash('Employer not found.', 'error')
            return redirect(url_for('deo_employer_table'))
    except psycopg2.Error as e:
        flash(f'Error: {e}', 'error')
        return redirect(url_for('deo_employer_table'))   
    
    
    
@app.route('/jobseeker_dashboard_details')
def jobseeker_dashboard_details():
    try:
        # Open a cursor to perform database operations
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SELECT  * FROM jobseeker_personal_info WHERE email = %s", (session['email'],))
        profile_info = cursor.fetchone()
        id=profile_info[0]

        # Check if profile_info is not None before proceeding
        if profile_info:
            # Fetch jobseeker's academic info from the database using profile_info[0] as application_id
            cursor.execute("SELECT * FROM jobseeker_academic_info WHERE application_id = %s", (id,))
            academic_info = cursor.fetchall()

            # Render the template with the academic info
            return render_template('Jobseeker_Dashboard_Details.html', profile_info=profile_info, academic_info=academic_info)
        else:
            return "Jobseeker not found."

    except Exception as e:
        return f"Error: {e}"

    finally:
        if cursor:
            cursor.close()

# Route to update the jobseeker_personal_info table
@app.route('/update_personal_info', methods=['POST'])
def update_personal_info():
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        
        # Get the updated personal information from the AJAX request
        name = request.json['name']
        phone = request.json['phone']
        gender = request.json['gender']
        dob = request.json['dob']
        address = request.json['address']
        email = session['email']  # Get the email from the session
        
        # Update the jobseeker_personal_info table
        cursor.execute("UPDATE jobseeker_personal_info SET name = %s, phone_number = %s, gender = %s, dob = %s, address = %s WHERE email = %s", (name, phone, gender, dob, address, email))
        
        # Commit the changes
        conn.commit()
        
        # Return a success message
        return jsonify({'message': 'Personal information updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        if cursor:
            cursor.close()
        
        
@app.route('/employer_jobseeker_chart')
def employer_jobseeker_chart():
    return render_template('Employer_Jobseeker_Chart.html')

@app.route('/employer_jobseeker_interest_chart')
def employer_jobseeker_interest_chart():
    return render_template('Employer_Jobseeker_Interest_Chart.html')


@app.route('/pia_form')
def pia_form():
        # Check if user is logged in (you may need to implement session management)
        if 'email' in session:
            email = session['email']
            print(email)
        #     response = make_response(render_template('PIA_form.html', email=email))
        #     response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        #     response.headers['Expires'] = 0
        #     response.headers['Pragma'] = 'no-cache'
        #     return response
        # else:
        #     flash('Please log in first.')
            # return redirect(url_for('login'))
        return render_template('PIA_form.html')
    
    
@app.route('/pia_employer_jobseeker_chart')
def pia_employer_jobseeker_chart():
    return render_template('PIA_Employer_Jobseeker_Chart.html')

@app.route('/pia_employer_jobseeker_interest_chart')
def pia_employer_jobseeker_interest_chart():
    return render_template('PIA_Employer_Jobseeker_Interest_Chart.html')

@app.route('/pia_employer_lists')
def pia_employer_lists():
    try:
        cursor.execute("SELECT * FROM employer_register ORDER BY id ASC ")
        data = cursor.fetchall()
        return render_template('PIA_Employer_Lists.html', data=data)
    except psycopg2.Error as e:
        flash(f'Error fetching data: {e}', 'error')
    return render_template('PIA_Employer_Lists.html')

@app.route('/employer_dashboard_detail')
def employer_dashboard_detail():
    if 'email' in session:
        email = session['email']  # Get the email from the session
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employer_register WHERE email = %s", (email,))
        employer = cursor.fetchone()
        print(employer)
        print(employer[1])
        cursor.close()
        conn.close()
        return render_template('Employer_Dashboard_Details.html',employer=employer)
    
    

    
@app.route('/pia_employer_details/<int:employer_id>')
def pia_employer_details(employer_id):
    try:
        cursor.execute("SELECT * FROM employer_register WHERE id = %s", (employer_id,))
        employer_data = cursor.fetchone()
        if employer_data:
            return render_template('PIA_Employer_Details.html', employer_data=employer_data)
        else:
            flash('Employer not found.', 'error')
            return redirect(url_for('pia_employer_lists'))
    except psycopg2.Error as e:
        flash(f'Error: {e}', 'error')
        return redirect(url_for('pia_employer_lists'))
    
if __name__ == '__main__':
    app.run(debug=True)
