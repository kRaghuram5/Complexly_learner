# ---------------- FLASK & MODULE IMPORTS ---------------- #
from flask import Flask, render_template, request, redirect
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Importing functions from custom modules
from modules.roots_of_unity import get_plot_image
from modules.modulus_argument import compute_mod_arg, create_complex_plot
from modules.de_moivre import visualize_de_moivre
from modules.polar_converter import polar_converter_handler
from modules.operations import perform_complex_operation
from modules.argand_plotter import generate_argand_plot
from modules.quiz import handle_quiz_route
import os
import json
from google.oauth2 import service_account
from dotenv import load_dotenv

load_dotenv()  # Load values from .env

creds_path = os.getenv("GOOGLE_CREDS_FILE")
if not creds_path:
    print("❌ GOOGLE_CREDS_FILE not found in environment.")
else:
    creds = service_account.Credentials.from_service_account_file(creds_path)



# ---------------- FLASK APP SETUP ---------------- #
app = Flask(__name__)
app.secret_key = "raghu123!secret@complex"  # Required for securely managing sessions (used in quiz)

# ---------------- GLOBAL USER INFO ---------------- #
# Dictionary to store the current user's name and class for display and logging
user_info = {"name": "", "class": ""}

# ---------------- GOOGLE SHEETS SETUP ---------------- #
from datetime import datetime

# This function connects to Google Sheets using a service account
# It ensures the sheet has proper headers and returns a reference to the sheet
def init_google_sheets():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    ]
    # Load credentials from service account JSON file
    creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("Login Details").sheet1  # Open the sheet named "Login Details"

    # Insert header row only if it's missing or incorrect
    try:
        headers = sheet.row_values(1)
        if headers != ["Name", "Class", "Timestamp"]:
            sheet.insert_row(["Name", "Class", "Timestamp"], 1)
    except gspread.exceptions.APIError:
        sheet.insert_row(["Name", "Class", "Timestamp"], 1)

    return sheet

# Initialize Google Sheets once when the app starts
sheet = init_google_sheets()

# ---------------- ROUTES ---------------- #

# Route: POST method to /intro (called after login)
# Saves user info to Google Sheet again and redirects to intro.html
@app.route('/intro', methods=['POST'])
def intro_page():
    user_info["name"] = request.form['name']
    user_info["class"] = request.form['class']
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([user_info["name"], user_info["class"], timestamp])
    return render_template('intro.html')


# Route: Home page (login form)
# On POST, captures user details, logs to sheet, and redirects to /home/
@app.route('/', methods=['GET', 'POST'])
def welcome():
    if request.method == 'POST':
        user_info["name"] = request.form['name']
        user_info["class"] = request.form['class']
        print(f"Name: {user_info['name']}")
        print(f"Class: {user_info['class']}")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([user_info["name"], user_info["class"], timestamp])
        return redirect('/home/')
    return render_template('main.html')  # main.html is the login form


# Route: Home dashboard (after login)
@app.route('/home/')
def home_dashboard():
    return render_template('index.html', user=user_info)  # index.html uses user info


# Route: Roots of Unity Visualizer
@app.route('/roots', methods=['GET', 'POST'])
def roots():
    n = 4  # Default value
    plot_url = None
    if request.method == 'POST':
        try:
            n = int(request.form['n'])  # Get number of roots from form
            if n >= 1:
                plot_url = get_plot_image(n)  # Generate image from module
        except ValueError:
            pass  # Ignore invalid input
    return render_template('roots.html', plot_url=plot_url, n=n)


# Route: Modulus & Argument Visualizer
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
    return render_template("modulus.html", a=a, b=b, modulus=modulus, argument=argument, plot_html=plot_html)


# Route: De Moivre's Theorem Visualizer
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
    return render_template('demoivre.html', plot_data=plot_data, result=result, explanation=explanation, n=n)


# Route: Polar-Cartesian Converter with Plot
@app.route('/polar', methods=['GET', 'POST'])
def polar():
    result = plot_html = explanation = ""
    if request.method == 'POST':
        try:
            mode = request.form.get('mode', '')  # Either polar-to-cartesian or reverse
            input1 = request.form.get('input1', '').strip()
            input2 = request.form.get('input2', '').strip()
            if input1 and input2:
                result, plot_html, explanation = polar_converter_handler(mode, input1, input2)
        except ValueError:
            result = "<strong>Error:</strong> Please enter valid numbers."
    return render_template('polar.html', result=result, plot_html=plot_html, explanation=explanation)


# Route: Complex Number Operations (+, -, *, /) with Visualization
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
    return render_template("operations.html", result_str=result_str, plot_url=plot_url)


# Route: Argand Plane Plotter
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
        form_data = {
            'a': a,
            'b': b,
            'show_conj': show_conj,
            'show_modulus': show_modulus,
            'show_arg': show_arg
        }

    return render_template('argand.html', plot_url=plot_url, result=result_data, form_data=form_data)


# Route: Complex Number Quiz (logic handled separately)
@app.route("/quiz", methods=["GET", "POST"])
def quiz_route():
    return handle_quiz_route()  # Calls logic in modules/quiz.py

# ---------------- MAIN ENTRY ---------------- #
if __name__ == '__main__':
    app.run(port=5000, debug=True)  # Start Flask server on http://127.0.0.1:5000
