from flask import Flask, render_template, request, redirect, flash, session, url_for
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from dotenv import load_dotenv
import hashlib
import json
import random
import time

# --- Import module handlers (unchanged) ---
from modules.roots_of_unity import get_plot_image
from modules.modulus_argument import compute_mod_arg, create_complex_plot
from modules.de_moivre import visualize_de_moivre
from modules.polar_converter import polar_converter_handler
from modules.operations import perform_complex_operation
from modules.argand_plotter import generate_argand_plot
from modules.quiz import handle_quiz_route, render_results_page

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
        return redirect(url_for('main_page'))

    return render_template('newlogin.html')

@app.route('/main')
def main_page():
    if 'user' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login_page'))
    return render_template('main.html', user=session['user'])

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

# ---------------- TOPIC ROUTES ---------------- #
@app.route('/home/')
def home_dashboard():
    return render_template('index.html', user=session.get('user', {}))

@app.route('/roots', methods=['GET', 'POST'])
def roots():
    n, plot_url = 4, None
    if request.method == 'POST':
        try:
            n = int(request.form['n'])
            if n >= 1:
                plot_url = get_plot_image(n)
        except ValueError:
            pass
    return render_template('roots.html', plot_url=plot_url, n=n, user=session.get('user', {}))

@app.route('/modulus', methods=['GET', 'POST'])
def modulus_argument():
    a = b = 0
    modulus = argument = 0
    plot_html = ""
    if request.method == 'POST':
        try:
            a = float(request.form['real'])
            b = float(request.form['imag'])
            modulus, argument = compute_mod_arg(a, b)
            plot_html = create_complex_plot(a, b)
        except ValueError:
            pass
    return render_template("modulus.html", a=a, b=b, modulus=modulus, argument=argument, plot_html=plot_html, user=session.get('user', {}))

@app.route('/demoivre', methods=['GET', 'POST'])
def demoivre():
    plot_data = result = explanation = ""
    n = None
    if request.method == 'POST':
        try:
            r = float(request.form['r'])
            theta = float(request.form['theta'])
            n = int(request.form['n'])
            plot_data, result, explanation = visualize_de_moivre(r, theta, n)
        except ValueError:
            pass
    return render_template('demoivre.html', plot_data=plot_data, result=result, explanation=explanation, n=n, user=session.get('user', {}))

@app.route('/polar', methods=['GET', 'POST'])
def polar():
    result = plot_html = explanation = ""
    if request.method == 'POST':
        try:
            mode = request.form.get('mode', '')
            input1 = request.form.get('input1', '').strip()
            input2 = request.form.get('input2', '').strip()
            if input1 and input2:
                result, plot_html, explanation = polar_converter_handler(mode, input1, input2)
        except ValueError:
            result = "<strong>Error:</strong> Please enter valid numbers."
    return render_template('polar.html', result=result, plot_html=plot_html, explanation=explanation, user=session.get('user', {}))

@app.route("/operations", methods=["GET", "POST"])
def operations():
    result_str, plot_url = None, None
    if request.method == "POST":
        a = request.form["a"]
        b = request.form["b"]
        c = request.form["c"]
        d = request.form["d"]
        operation = request.form["operation"]
        result_str, plot_url = perform_complex_operation(a, b, c, d, operation)
    return render_template("operations.html", result_str=result_str, plot_url=plot_url, user=session.get('user', {}))

@app.route('/argand', methods=['GET', 'POST'])
def argand():
    plot_url = ''
    result_data = None
    form_data = {'a': '', 'b': '', 'show_conj': True, 'show_modulus': True, 'show_arg': True}

    if request.method == 'POST':
        a = request.form['real']
        b = request.form['imag']
        show_conj = 'show_conj' in request.form
        show_modulus = 'show_modulus' in request.form
        show_arg = 'show_arg' in request.form
        plot_url, result_data = generate_argand_plot(a, b, show_conj, show_modulus, show_arg)
        form_data = {'a': a, 'b': b, 'show_conj': show_conj, 'show_modulus': show_modulus, 'show_arg': show_arg}

    return render_template('argand.html', plot_url=plot_url, result=result_data, form_data=form_data, user=session.get('user', {}))

# ---------------- QUIZ ROUTES (UPDATED) ---------------- #
# ---------------- QUIZ ROUTES (UPDATED WITH LOGIN FIX) ---------------- #
@app.route('/quiz-select', methods=['GET'])
def quiz_select():
    if 'user' not in session:
        flash("Please log in to take quizzes.", "warning")
        return redirect(url_for('login_page'))
    return render_template("select_difficulty.html", user=session['user'])

@app.route('/start_quiz', methods=['POST'])
def start_quiz():
    if 'user' not in session:
        flash("Please log in to take quizzes.", "warning")
        return redirect(url_for('login_page'))

    difficulty = request.form.get("difficulty")
    if not difficulty:
        flash("Please select a difficulty.", "danger")
        return redirect(url_for('quiz_select'))

    try:
        with open("questions.json", "r") as f:
            all_questions = json.load(f)

        if difficulty not in all_questions:
            flash("Invalid difficulty selected.", "danger")
            return redirect(url_for('quiz_select'))

        selected_questions = random.sample(all_questions[difficulty], min(10, len(all_questions[difficulty])))

        # Preserve login session
        user_info = session.get('user')
        session.clear()
        session['user'] = user_info

        # Store quiz data
        session['questions'] = selected_questions
        session['current_index'] = 0
        session['answers'] = [''] * len(selected_questions)
        session['submitted'] = False
        session['difficulty'] = difficulty

        # Timer setup
        time_limits = {'PU': 1200, 'CET': 600, 'JEE': 1200}
        session['quiz_start_time'] = int(time.time())
        session['quiz_time_limit'] = time_limits.get(difficulty, 1200)

        return redirect(url_for("quiz"))
    except Exception as e:
        flash(f"Error loading quiz: {e}", "danger")
        return redirect(url_for("quiz_select"))

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if 'user' not in session:
        flash("Please log in to take quizzes.", "warning")
        return redirect(url_for('login_page'))
    if 'questions' not in session:
        flash("Please start a quiz first.", "danger")
        return redirect(url_for('quiz_select'))

    now = int(time.time())
    start = session.get('quiz_start_time', now)
    limit = session.get('quiz_time_limit', 1200)
    elapsed = now - start
    remaining = max(0, limit - elapsed)

    return handle_quiz_route(time_remaining=remaining)

@app.route("/quiz-result", methods=["GET"])
def quiz_result():
    if 'user' not in session:
        flash("Please log in to view results.", "warning")
        return redirect(url_for('login_page'))
    return render_results_page()


# ---------------- RUN ---------------- #
if __name__ == '__main__':
    app.run(port=5000, debug=True)
