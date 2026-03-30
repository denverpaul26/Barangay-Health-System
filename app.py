from flask import Flask, render_template, request, redirect, url_for
from database import db
from models import Patient, Staff
from werkzeug.security import generate_password_hash


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = ("mssql+pyodbc://@localhost/BarangayDB?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if user exists in Patient or Staff
        patient = Patient.query.filter_by(email=email).first()
        staff = Staff.query.filter_by(email=email).first()

        # Verify password
        from werkzeug.security import check_password_hash
        if patient and check_password_hash(patient.password, password):
            return redirect(url_for('home'))  # or patient dashboard
        elif staff and check_password_hash(staff.password, password):
            return redirect(url_for('home'))  # or staff dashboard
        else:
            return "Invalid credentials", 401

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        patient = Patient(
            first_name=request.form['first_name'],
            middle_name=request.form.get('middle_name'),
            last_name=request.form['last_name'],
            dob=request.form['dob'],
            gender=request.form['gender'],
            email=request.form['email'],
            password=generate_password_hash(request.form['password'])
        )
        db.session.add(patient)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/register-staff', methods=['GET', 'POST'])
def register_staff():
    if request.method == 'POST':
        staff = Staff(
            first_name=request.form['first_name'],
            middle_name=request.form.get('middle_name'),
            last_name=request.form['last_name'],
            dob=request.form['dob'],
            gender=request.form['gender'],
            email=request.form['email'],
            password=generate_password_hash(request.form['password']),
            staff_id=request.form['staff_id'],
            role=request.form['role']
        )
        db.session.add(staff)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register-staff.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()   # ensures tables are created
    app.run(debug=True)