from flask import Flask, render_template, request, redirect, url_for, session, abort, flash
from database import db
from models import Patient, Staff, Appointment
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"  # needed for sessions
app.config['SQLALCHEMY_DATABASE_URI'] = (
    "mssql+pyodbc://@localhost/BarangayDB?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def home():
    return render_template('index.html')

from flask import flash

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        patient = Patient.query.filter_by(email=email).first()
        staff = Staff.query.filter_by(email=email).first()

        if patient and check_password_hash(patient.password, password):
            session['user_type'] = 'patient'
            session['user_id'] = patient.id
            return redirect(url_for('patient_dashboard'))
        elif staff and check_password_hash(staff.password, password):
            session['user_type'] = 'staff'
            session['user_id'] = staff.id
            return redirect(url_for('staff_dashboard'))
        else:
            flash("Invalid email or password", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

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

# --------------------------PATIENT-------------------------------
@app.route('/appointment/<int:appt_id>')
def appointment_details(appt_id):
    if 'user_type' not in session or session['user_type'] != 'patient':
        return redirect(url_for('login'))

    patient = Patient.query.get(session['user_id'])
    appointment = db.session.get(Appointment, appt_id)
    if not appointment:
        abort(404)

    return render_template(
        'patient/appointment-details.html',
        patient_name=f"{patient.first_name} {patient.last_name}",
        appointment=appointment
    )

@app.route('/appointments/<int:appointment_id>/cancel', methods=['POST'])
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.status = "Cancelled"
    db.session.commit()
    flash('Appointment cancelled successfully!', 'danger')
    return redirect(url_for('my_appointments'))

@app.route('/appointments/<int:appointment_id>/delete', methods=['POST'])
def delete_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)

    if appointment.status != "Cancelled":
        flash("You can only delete cancelled appointments.", "warning")
        return redirect(url_for('appointment_details', appointment_id=appointment.id))

    db.session.delete(appointment)
    db.session.commit()
    flash("Appointment deleted successfully.", "success")
    return redirect(url_for('my_appointments'))

@app.route('/book-appointment', methods=['GET', 'POST'])
def book_appointment():
    if 'user_type' not in session or session['user_type'] != 'patient':
        return redirect(url_for('login'))

    patient = Patient.query.get(session['user_id'])

    if request.method == 'POST':
        service_type = request.form['service_type']
        date = request.form['date']
        time = request.form['time']
        reason = request.form.get('reason')
        priority = request.form.get('priority')

        new_appt = Appointment(
            patient_id=patient.id,
            service_type=service_type,
            date=date,
            time=time,
            staff_name=None,  # assigned later by staff
            status="Pending",
            reason=reason,
            priority=priority
        )
        db.session.add(new_appt)
        db.session.commit()

        return redirect(url_for('my_appointments'))

    return render_template('patient/book-appointment.html', patient_name=f"{patient.first_name} {patient.last_name}")

@app.route('/my-appointments')
def my_appointments():
    if 'user_type' not in session or session['user_type'] != 'patient':
        return redirect(url_for('login'))

    patient = Patient.query.get(session['user_id'])
    appointments = Appointment.query.filter_by(patient_id=patient.id).all()

    return render_template(
        'patient/my-appointments.html',
        patient_name=f"{patient.first_name} {patient.last_name}",
        appointments=appointments
    )

@app.route('/notifications')
def notifications():
    if 'user_type' not in session or session['user_type'] != 'patient':
        return redirect(url_for('login'))

    patient = Patient.query.get(session['user_id'])

    return render_template(
        'patient/notifications.html',
        patient_name=f"{patient.first_name} {patient.last_name}"
    )

@app.route('/patient-dashboard')
def patient_dashboard():
    if 'user_type' not in session or session['user_type'] != 'patient':
        return redirect(url_for('login'))

    patient = Patient.query.get(session['user_id'])

    return render_template(
        'patient/patient-dashboard.html',
        patient_name=f"{patient.first_name} {patient.last_name}"
    )

@app.route('/profile')
def profile():
    if 'user_type' not in session or session['user_type'] != 'patient':
        return redirect(url_for('login'))

    patient = Patient.query.get(session['user_id'])

    return render_template(
        'patient/profile.html',
        patient_name=f"{patient.first_name} {patient.last_name}"
    )

@app.route('/queue')
def queue():
    if 'user_type' not in session or session['user_type'] != 'patient':
        return redirect(url_for('login'))

    patient = Patient.query.get(session['user_id'])

    return render_template(
        'patient/queue.html',
        patient_name=f"{patient.first_name} {patient.last_name}"
    )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)