from flask import request, session, redirect, render_template
import os
import random, cmath, gspread
from oauth2client.service_account import ServiceAccountCredentials

# ---------------------------- Google Sheets Setup ----------------------------

# Define the scope of the Google Sheets and Drive API access
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load credentials from the service account JSON file


scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# Render stores secrets at this path
json_key_path = os.getenv("GOOGLE_CREDS_PATH", "service_account.json")
creds = ServiceAccountCredentials.from_json_keyfile_name(json_key_path, scope)


# Authorize the client using the credentials
client = gspread.authorize(creds)

# Open the spreadsheet and select the first sheet
sheet = client.open("quiz").sheet1

# -------------------------- Quiz Question Generator --------------------------

# Function to generate one quiz question
def generate_question():
    r = random.randint(1, 5)  # Random modulus
    theta = random.choice([30, 45, 60, 90, 120])  # Random argument in degrees
    n = random.randint(2, 5)  # Random power

    # Convert polar form to complex number
    z = cmath.rect(r, cmath.pi * theta / 180)

    # Compute z raised to the power n
    z_power_n = z ** n

    # Create question string in polar form
    question = f"Find z^{n} where z = {r}(cos({theta}°) + i·sin({theta}°))"

    # Round and format correct answer to 2 decimal places
    correct = complex(round(z_power_n.real, 2), round(z_power_n.imag, 2))

    return {"question": question, "correct_answer": str(correct)}

# ------------------------ Quiz Evaluation Logic ------------------------

# Evaluate user answers and return summary
def evaluate_quiz(questions, answers):
    correct = 0
    incorrect = 0
    results = []  # To store each question, user's answer, correct answer, and status

    for i in range(10):
        q = questions[i]['question']
        a = answers[i]
        c = questions[i]['correct_answer']
        try:
            # Convert user's answer to complex number (replace i with j for Python)
            user_answer = complex(a.replace("i", "j").replace(" ", ""))
            correct_answer = complex(c)

            # Compare using small tolerance to handle floating-point errors
            if abs(user_answer - correct_answer) < 1e-2:
                status = "Correct"
                correct += 1
            else:
                status = "Incorrect"
                incorrect += 1
        except:
            # If parsing fails, treat answer as incorrect
            status = "Incorrect"
            incorrect += 1

        # Add result to the list
        results.append([q, a, c, status])

    try:
        # Try to save results to Google Sheets
        sheet.append_rows(results)
    except Exception as e:
        print("Google Sheets update failed:", e)

    return correct, incorrect, results

# --------------------------- Quiz Route Handler ---------------------------

# This function handles the /quiz route
def handle_quiz_route():
    # If quiz session doesn't exist or already submitted, reset everything
    if 'questions' not in session or session.get('submitted'):
        session.clear()
        session['questions'] = [generate_question() for _ in range(10)]  # Generate 10 questions
        session['current_index'] = 0  # Track which question user is on
        session['answers'] = [''] * 10  # Initialize empty answers
        session['submitted'] = False  # Mark quiz as not yet submitted

    # Handle form submission (next, prev, reset, submit)
    if request.method == "POST":
        action = request.form.get("action")
        index = session['current_index']
        answer = request.form.get("answer", "").strip()
        session['answers'][index] = answer  # Save the current answer

        if action == "reset":
            # Clear session and restart quiz
            session.clear()
            return redirect("/quiz")
        elif action == "next" and index < 9:
            session['current_index'] += 1  # Go to next question
        elif action == "prev" and index > 0:
            session['current_index'] -= 1  # Go to previous question
        elif action == "submit" and not session.get("submitted", False):
            # Final submission of quiz
            correct, incorrect, results = evaluate_quiz(session['questions'], session['answers'])
            session['submitted'] = True
            session['correct'] = correct
            session['incorrect'] = incorrect

    # Prepare data for current question to render on template
    index = session['current_index']
    question_data = session['questions'][index]
    answer_data = session['answers'][index]

    # Render the quiz template with current state
    return render_template("quiz.html",
                           question=question_data['question'],
                           correct_answer=question_data['correct_answer'],
                           answer=answer_data,
                           index=index,
                           total=10,
                           answers=session['answers'],
                           submitted=session.get('submitted', False),
                           correct=session.get('correct'),
                           incorrect=session.get('incorrect'))
