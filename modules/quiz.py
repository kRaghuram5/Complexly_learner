from flask import request, session, redirect, render_template
import os, random, json, io, base64
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import defaultdict

# ---------------- Google Sheets Setup ----------------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
json_key_path = os.getenv("GOOGLE_CREDS_PATH", "service_account.json")
creds = ServiceAccountCredentials.from_json_keyfile_name(json_key_path, scope)
client = gspread.authorize(creds)
sheet = client.open("quiz").sheet1

# ---------------- Quiz Evaluation ----------------
def evaluate_quiz(questions, answers):
    correct = incorrect = 0
    topic_stats = defaultdict(lambda: {"correct": 0, "incorrect": 0})
    results = []

    for i in range(10):
        q = questions[i]['question']
        a = answers[i]
        c = questions[i]['correct_answer']
        topic = questions[i].get('topic', 'General')

        try:
            user_answer = complex(a.replace("i", "j").replace(" ", ""))
            correct_answer = complex(c.replace("i", "j").replace(" ", ""))
            if abs(user_answer - correct_answer) < 1e-2:
                status = "Correct"
                correct += 1
                topic_stats[topic]["correct"] += 1
            else:
                status = "Incorrect"
                incorrect += 1
                topic_stats[topic]["incorrect"] += 1
        except:
            status = "Incorrect"
            incorrect += 1
            topic_stats[topic]["incorrect"] += 1

        results.append([q, a, c, status, topic])

    try:
        sheet.append_rows(results)
    except Exception as e:
        print("Google Sheets update failed:", e)

    session["topic_stats"] = dict(topic_stats)
    return correct, incorrect, results

# ---------------- Quiz Route ----------------
def handle_quiz_route(time_remaining=None):
    if 'questions' not in session or session.get('submitted'):
        return redirect("/quiz-select")

    if request.method == "POST":
        if time_remaining is not None and time_remaining <= 0 and not session.get('submitted', False):
            correct, incorrect, _ = evaluate_quiz(session['questions'], session['answers'])
            session['submitted'] = True
            session['correct'] = correct
            session['incorrect'] = incorrect

    action = request.form.get("action")
    index = session['current_index']
    answer = request.form.get("answer", "").strip()
    session['answers'][index] = answer

    jump_to_index = request.form.get("jump_to_index")
    if jump_to_index:
        try:
            jump_index = int(jump_to_index)
            if 0 <= jump_index < 10:
                session['current_index'] = jump_index
        except ValueError:
            pass

    if action == "reset":
        session.clear()
        return redirect("/quiz-select")
    elif action == "next" and index < 9:
        session['current_index'] += 1
    elif action == "prev" and index > 0:
        session['current_index'] -= 1
    elif action == "submit" and not session.get("submitted", False):
        correct, incorrect, _ = evaluate_quiz(session['questions'], session['answers'])
        session['submitted'] = True
        session['correct'] = correct
        session['incorrect'] = incorrect

    index = session['current_index']
    q_data = session['questions'][index]
    return render_template(
        "quiz.html",
        question=q_data['question'],
        correct_answer=q_data['correct_answer'],
        answer=session['answers'][index],
        index=index,
        total=10,
        answers=session['answers'],
        submitted=session.get('submitted', False),
        correct=session.get('correct'),
        incorrect=session.get('incorrect'),
        time_remaining=time_remaining
    )

# ---------------- Results Page ----------------
def render_results_page():
    current_correct = session.get('correct', 0)
    current_incorrect = session.get('incorrect', 0)
    topic_stats = session.get("topic_stats", {})

    try:
        all_values = sheet.get_all_values()
        past_topic_stats = defaultdict(lambda: {"correct": 0, "incorrect": 0})
        for row in all_values:
            if len(row) >= 5:
                topic = row[4] or "General"
                if row[3].strip().lower() == "correct":
                    past_topic_stats[topic]["correct"] += 1
                elif row[3].strip().lower() == "incorrect":
                    past_topic_stats[topic]["incorrect"] += 1
    except Exception as e:
        print("Google Sheets read failed:", e)
        past_topic_stats = {}

    # --- Chart 1: Overall Past vs Current ---
    labels = ['Correct', 'Incorrect']
    fig1, ax1 = plt.subplots()
    ax1.bar([0, 1], [sum(t["correct"] for t in past_topic_stats.values()), sum(t["incorrect"] for t in past_topic_stats.values())], width=0.35, label="Past")
    ax1.bar([0.35, 1.35], [current_correct, current_incorrect], width=0.35, label="Current")
    ax1.set_xticks([0.2, 1.2])
    ax1.set_xticklabels(labels)
    ax1.set_title("Overall Performance")
    ax1.legend()
    buf1 = io.BytesIO(); fig1.savefig(buf1, format='png'); buf1.seek(0)
    plot1 = base64.b64encode(buf1.getvalue()).decode(); buf1.close(); plt.close(fig1)

    # --- Chart 2: Current Section-wise ---
    topics = list(topic_stats.keys())
    corr = [topic_stats[t]["correct"] for t in topics]
    incorr = [topic_stats[t]["incorrect"] for t in topics]
    fig2, ax2 = plt.subplots()
    ax2.bar(topics, corr, label="Correct", color="green")
    ax2.bar(topics, incorr, bottom=corr, label="Incorrect", color="red")
    ax2.set_title("Current Quiz - Section-wise Performance")
    ax2.legend()
    plt.xticks(rotation=45)
    buf2 = io.BytesIO(); fig2.savefig(buf2, format='png'); buf2.seek(0)
    plot2 = base64.b64encode(buf2.getvalue()).decode(); buf2.close(); plt.close(fig2)

    # --- Chart 3: Past Section-wise ---
    past_topics = list(past_topic_stats.keys())
    p_corr = [past_topic_stats[t]["correct"] for t in past_topics]
    p_incorr = [past_topic_stats[t]["incorrect"] for t in past_topics]
    fig3, ax3 = plt.subplots()
    ax3.bar(past_topics, p_corr, label="Correct", color="lightgreen")
    ax3.bar(past_topics, p_incorr, bottom=p_corr, label="Incorrect", color="salmon")
    ax3.set_title("Past Quizzes - Section-wise Performance")
    ax3.legend()
    plt.xticks(rotation=45)
    buf3 = io.BytesIO(); fig3.savefig(buf3, format='png'); buf3.seek(0)
    plot3 = base64.b64encode(buf3.getvalue()).decode(); buf3.close(); plt.close(fig3)

    return render_template(
        "quiz_result.html",
        current_correct=current_correct,
        current_incorrect=current_incorrect,
        plot1=plot1,
        plot2=plot2,
        plot3=plot3
    )
