from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime
import smtplib

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Use a secure key here

DATABASE = 'database/pharmacy.db'

# --- Helper functions ---

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def send_email(subject, message, to_email):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    sender_email = 'your_email@gmail.com'
    sender_password = 'your_app_password'
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, to_email, f"Subject:{subject}\n\n{message}")
    server.quit()

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        conn.execute('INSERT INTO pharmacists (username, email, password) VALUES (?, ?, ?)',(username, email, password))
        conn.commit()
        conn.close()
        flash('Account created successfully! Please login.')
        return redirect(url_for('login_pharmacist'))
    return render_template('signup.html')

@app.route('/login_pharmacist', methods=['GET', 'POST'])
def login_pharmacist():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        pharmacist = conn.execute('SELECT * FROM pharmacists WHERE email = ? AND password = ?',
                                  (email, password)).fetchone()
        conn.close()

        if pharmacist:
            session['user_type'] = 'pharmacist'
            session['user_id'] = pharmacist['id']
            session['username'] = pharmacist['username']
            flash('Login successful!')

            # Alert Pharmacist about near expiry
            conn = get_db_connection()
            medicine = conn.execute('SELECT * FROM medicines ORDER BY expiry_date ASC LIMIT 1').fetchone()
            conn.close()

            if medicine:
                flash(f"⚠️ Attention! '{medicine['name']}' is expiring on {medicine['expiry_date']}.", 'alert')
            return redirect(url_for('home_pharmacist'))
        else:
            flash('Invalid credentials. Try again!')
    return render_template('login_pharmacist.html')

@app.route('/login_admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'admin123':
            session['user_type'] = 'admin'
            flash('Admin login successful!')
            return redirect(url_for('home_admin'))
        else:
            flash('Invalid admin credentials.')
    return render_template('login_admin.html')

@app.route('/home_pharmacist')
def home_pharmacist():
    if 'user_type' in session and session['user_type'] == 'pharmacist':
        return render_template('home_pharmacist.html')
    else:
        flash('Unauthorized access.')
        return redirect(url_for('index'))

@app.route('/add_medicine', methods=['GET', 'POST'])
def add_medicine():
    if request.method == 'POST':
        name = request.form['name']
        count = request.form['count']
        expiry_date = request.form['expiry_date']

        conn = get_db_connection()
        conn.execute('INSERT INTO medicines (name, count, expiry_date) VALUES (?, ?, ?)',
                     (name, count, expiry_date))
        conn.commit()
        conn.close()
        flash('Medicine added successfully!')
        return redirect(url_for('view_medicines'))
    return render_template('add_medicine.html')

@app.route('/view_medicines')
def view_medicines():
    conn = get_db_connection()
    medicines = conn.execute('SELECT * FROM medicines ORDER BY expiry_date ASC').fetchall()
    conn.close()
    return render_template('view_medicines.html', medicines=medicines)

@app.route('/sort_by_expiry')
def sort_by_expiry():
    conn = get_db_connection()
    medicines = conn.execute('SELECT * FROM medicines ORDER BY expiry_date ASC').fetchall()
    conn.close()
    return render_template('view_medicines.html', medicines=medicines)

@app.route('/donate/<int:id>', methods=['GET', 'POST'])
def donate(id):
    if request.method == 'POST':
        discount = request.form['discount']
        conn = get_db_connection()
        conn.execute('INSERT INTO donation_requests (medicine_id, discount_percent, status) VALUES (?, ?, ?)',
                     (id, discount, 'Pending'))
        conn.commit()
        conn.close()
        flash('Donation request submitted!')
        return redirect(url_for('view_medicines'))
    return render_template('donate.html', id=id)

@app.route('/home_admin')
def home_admin():
    if 'user_type' in session and session['user_type'] == 'admin':
        conn = get_db_connection()
        medicines = conn.execute('SELECT * FROM medicines ORDER BY expiry_date ASC').fetchall()

        # Join to get medicine name with donation request
        requests = conn.execute('''
            SELECT dr.id, dr.medicine_id, dr.discount_percent, dr.status, m.name as medicine_name
            FROM donation_requests dr
            JOIN medicines m ON dr.medicine_id = m.id
            WHERE dr.status = "Pending"
        ''').fetchall()

        conn.close()
        return render_template('home_admin.html', medicines=medicines, requests=requests)
    else:
        flash('Unauthorized access.')
        return redirect(url_for('index'))

@app.route('/edit_medicine/<int:id>', methods=['GET', 'POST'])
def edit_medicine(id):
    conn = get_db_connection()
    medicine = conn.execute('SELECT * FROM medicines WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        name = request.form['name']
        count = request.form['count']
        expiry_date = request.form['expiry_date']

        conn.execute('UPDATE medicines SET name = ?, count = ?, expiry_date = ? WHERE id = ?',
                     (name, count, expiry_date, id))
        conn.commit()
        conn.close()
        flash('Medicine details updated!')
        return redirect(url_for('home_admin'))

    conn.close()
    return render_template('edit_medicine.html', medicine=medicine)

@app.route('/delete_medicine/<int:id>')
def delete_medicine(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM medicines WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Medicine deleted!')
    return redirect(url_for('home_admin'))

@app.route('/accept_request/<int:request_id>')
def accept_request(request_id):
    conn = get_db_connection()
    request_data = conn.execute('SELECT * FROM donation_requests WHERE id = ?', (request_id,)).fetchone()
    if request_data:
        medicine_id = request_data['medicine_id']
        discount_percent = request_data['discount_percent']

        conn.execute('UPDATE medicines SET name = name || " (" || ? || "% OFF)" WHERE id = ?',
                     (discount_percent, medicine_id))
        conn.execute('UPDATE donation_requests SET status = "Accepted" WHERE id = ?', (request_id,))
        conn.commit()
    conn.close()
    flash('Donation request accepted.')
    return redirect(url_for('home_admin'))

@app.route('/decline_request/<int:request_id>')
def decline_request(request_id):
    conn = get_db_connection()
    conn.execute('UPDATE donation_requests SET status = "Declined" WHERE id = ?', (request_id,))
    conn.commit()
    conn.close()
    flash('Donation request declined.')
    return redirect(url_for('home_admin'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.')
    return redirect(url_for('index'))

# --- Main Start ---
if __name__ == '__main__':
    app.run(debug=True)
