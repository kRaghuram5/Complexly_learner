from flask import Flask, render_template, request, redirect, flash, session, url_for
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from dotenv import load_dotenv
import hashlib

# --- Setup ---
load_dotenv()
app = Flask(__name__)
app.secret_key = "raghu123!secret@complex"  # move to .env for production

# ---------------- GOOGLE SHEETS SETUP ---------------- #
def init_google_sheets():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open("Login Details")

    login_sheet = spreadsheet.sheet1
    try:
        if login_sheet.row_values(1) != ["Gmail", "Name", "Class", "PasswordHash", "Timestamp"]:
            login_sheet.insert_row(["Gmail", "Name", "Class", "PasswordHash", "Timestamp"], 1)
    except:
        login_sheet.insert_row(["Gmail", "Name", "Class", "PasswordHash", "Timestamp"], 1)

    try:
        log_sheet = spreadsheet.worksheet("Login Logs")
    except gspread.exceptions.WorksheetNotFound:
        log_sheet = spreadsheet.add_worksheet(title="Login Logs", rows="1000", cols="5")
        log_sheet.insert_row(["Gmail", "Name", "Class", "Type", "Timestamp"], 1)

    return login_sheet, log_sheet

login_sheet, log_sheet = init_google_sheets()

# ---------------- UTIL ---------------- #
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def log_login(gmail, name, class_, login_type):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_sheet.append_row([gmail, name, class_, login_type, timestamp])

def get_user_from_sheet(gmail):
    all_users = login_sheet.get_all_records()
    for user in all_users:
        if user["Gmail"].strip().lower() == gmail.strip().lower():
            return user
    return None

# ---------------- AUTH ROUTES ---------------- #
@app.route('/', methods=['GET'])
def root_intro():
    user = session.get('user', {})
    return render_template('index.html', user=user)

@app.route('/intro', methods=['GET'])
def intro_page():
    user = session.get('user', {})
    return render_template('intro.html', user=user)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        gmail = request.form['gmail'].strip().lower()
        password = request.form['password']
        password_hash = hash_password(password)

        user = get_user_from_sheet(gmail)
        if user:
            if user["PasswordHash"] == password_hash:
                session['user'] = {"name": user["Name"], "class": user["Class"], "gmail": gmail}
                log_login(gmail, user["Name"], user["Class"], "login")
                flash("Login successful!", "success")
                return redirect(url_for('root_intro'))
            else:
                flash("Invalid credentials. Incorrect password.", "danger")
        else:
            flash("Invalid credentials. User not found.", "danger")
        return redirect(url_for('login_page'))

    return render_template('main.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for('root_intro'))

@app.route('/newlogin', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        gmail = request.form['gmail'].strip().lower()
        name = request.form['name']
        class_ = request.form['class']
        password = request.form['password']
        password_hash = hash_password(password)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if get_user_from_sheet(gmail):
            flash("Account already exists. Please login or use Forgot Password.", "warning")
            return redirect(url_for('login_page'))

        login_sheet.append_row([gmail, name, class_, password_hash, timestamp])
        session['user'] = {"name": name, "class": class_, "gmail": gmail}
        flash("Signup successful! Welcome!", "success")
        return redirect(url_for('root_intro'))

    return render_template('newlogin.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        gmail = request.form['gmail'].strip().lower()
        new_password = request.form['password']
        new_password_hash = hash_password(new_password)

        try:
            cell = login_sheet.find(gmail)
            if cell:
                login_sheet.update_cell(cell.row, 4, new_password_hash)
                flash("Password updated successfully. Please log in.", "success")
                return redirect(url_for('login_page'))
            else:
                flash("Gmail not found. Please sign up.", "warning")
                return redirect(url_for('signup'))
        except Exception:
            flash("Error updating password.", "danger")
            return redirect(url_for('forgot_password'))

    return render_template('forgot_password.html')

# ---------------- IMPORT OTHER ROUTES ---------------- #
from app import register_routes
register_routes(app, session)

# ---------------- RUN ---------------- #
if __name__ == '__main__':
    app.run(port=5000, debug=True)
