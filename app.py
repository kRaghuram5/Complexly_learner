from flask import render_template, request, redirect, flash, url_for
import json, random, time
import numpy as np
import re
# --- Import module handlers ---
from modules.roots_of_unity import get_plot_image
from modules.modulus_argument import compute_mod_arg, create_complex_plot
from modules.de_moivre import visualize_de_moivre
from modules.polar_converter import polar_converter_handler
from modules.operations import perform_complex_operation
from modules.argand_plotter import generate_argand_plot
from modules.quiz import handle_quiz_route, render_results_page

def register_routes(app, session):

    @app.route('/roots', methods=['GET', 'POST'])
    def roots():
        n, plot_url, formula, roots_str = 4, None, None, None
        if request.method == 'POST':
            try:
                n = int(request.form['n'])
                if n >= 1:
                    plot_url, formula, roots_str = get_plot_image(n)
            except ValueError:
                pass
        return render_template('roots.html', plot_url=plot_url, formula=formula, roots_str=roots_str, n=n, user=session.get('user', {}))

    @app.route('/modulus', methods=['GET', 'POST'])
    def modulus_argument():
        a = b = 0
        plot_html = ""
        modulus = None
        argument_rad = None
        argument_deg = None
        error_message = None
        if request.method == 'POST':
            try:
                a = float(request.form['real'])
                b = float(request.form['imag'])
                modulus, argument = compute_mod_arg(a, b)
                plot_html = create_complex_plot(a, b)
            except ValueError:
                pass
        return render_template("modulus.html",
        modulus=modulus,
        argument_rad=argument_rad,
        argument_deg=argument_deg,
        error_message=error_message, plot_html = plot_html, a=a, b=b, user=session.get('user',{}))


    @app.route('/demoivre', methods=['GET', 'POST'])
    def demoivre():
        plot_data = result = explanation = polar_result = cartesian_result = ""
        n = None
        input_type = request.form.get('input_type', 'polar')

        if request.method == 'POST':
            try:
                n = int(request.form['n'])
                if input_type == 'polar':
                    r = float(request.form['r'])
                    theta = float(request.form['theta'])  # already degrees
                else:  # cartesian
                    a = float(request.form['a'])
                    b = float(request.form['b'])
                    r = (a**2 + b**2)**0.5
                    theta = np.degrees(np.arctan2(b, a))

            # Call visualizer
                plot_data, result, explanation = visualize_de_moivre(r, theta, n)

            # Polar result
                polar_result = f"{r**n:.2f} ∠ {n*theta:.2f}°"

            # Cartesian result
                z_n = r**n * (np.cos(np.radians(n*theta))) + 1j * r**n * np.sin(np.radians(n*theta))
                cartesian_result = f"{z_n.real:.2f} + {z_n.imag:.2f}i"

            except ValueError:
                pass

        return render_template(
        'demoivre.html',
        plot_data=plot_data,
        result=result,
        polar_result=polar_result,
        cartesian_result=cartesian_result,
        explanation=explanation,
        n=n,
        input_type=input_type,
        user=session.get('user', {})
    )
            
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
        return render_template('polar.html', result=result, 
                               plot_html=plot_html, explanation=explanation, user=session.get('user', {}))

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
    # ---------------- QUIZ ROUTES ---------------- #
    @app.route('/quiz-select', methods=['GET'])
    def quiz_select():
        if 'user' not in session:
            flash("Please log in to take quizzes.", "warning")
            return redirect(url_for('login_page'))
        return render_template("select_module.html", user=session['user'])

    @app.route('/start_quiz', methods=['POST'])
    def start_quiz():
        if 'user' not in session:
            flash("Please log in to take quizzes.", "warning")
            return redirect(url_for('login_page'))

        module = request.form.get("module")
        if not module:
            flash("Please select a module.", "danger")
            return redirect(url_for('quiz_select'))

        try:
            with open("questions.json", "r") as f:
                all_questions = json.load(f)

            if module not in all_questions:
                flash("Invalid module selected.", "danger")
                return redirect(url_for('quiz_select'))

            selected_questions = random.sample(all_questions[module], min(10, len(all_questions[module])))

            user_info = session.get('user')
            session.clear()
            session['user'] = user_info

            session['questions'] = selected_questions
            session['current_index'] = 0
            session['answers'] = [''] * len(selected_questions)
            session['submitted'] = False
            session['module'] = module

            return redirect(url_for("quiz"))
        except Exception as e:
            flash(f"Error loading quiz: {e}", "danger")
            return redirect(url_for('quiz_select'))

    
    @app.route("/quiz", methods=["GET", "POST"])
    def quiz():
        if 'user' not in session:
            flash("Please log in to take quizzes.", "warning")
            return redirect(url_for('login_page'))
        if 'questions' not in session:
            flash("Please start a quiz first.", "danger")
            return redirect(url_for('quiz_select'))

        questions = session['questions']
        current_index = session.get('current_index', 0)
        answers = session.get('answers', [''] * len(questions))

        if request.method == "POST":
            action = request.form.get("action")

            # normalize - store only first alphabetic character as letter answer
            raw_answer = request.form.get("answer", "")
            user_letter = ""
            for ch in raw_answer.strip().lower():
                if ch.isalpha():
                    user_letter = ch
                    break
            answers[current_index] = user_letter
            session['answers'] = answers

            if action == "next" and current_index < len(questions) - 1:
                current_index += 1
            elif action == "prev" and current_index > 0:
                current_index -= 1
            elif action == "jump":
                jump_index = int(request.form.get("jump_to_index", current_index))
                if 0 <= jump_index < len(questions):
                    current_index = jump_index
            elif action == "submit":
                return redirect(url_for('quiz_result'))

            session['current_index'] = current_index

        question = questions[current_index]
        return render_template(
            "quiz.html",
            question=question.get('question'),
            options=question.get('options', []),
            index=current_index,
            total=len(questions),
            answers=answers
        )

    @app.route("/quiz-result")
    def quiz_result():
        if 'user' not in session:
            flash("Please log in to view results.", "warning")
            return redirect(url_for('login_page'))

        if 'questions' not in session or 'answers' not in session:
            flash("No quiz data found. Please take a quiz first.", "danger")
            return redirect(url_for('quiz_select'))

        questions = session['questions']
        answers = session['answers']
        score = 0
        solutions = []

        def extract_letter(s):
            """Return first alphabetical character in s.lower(), or '' if none."""
            if not s:
                return ""
            for ch in s:
                if ch.isalpha():
                    return ch.lower()
            return ""

        def pick_text(letter, options):
            """Return full option string that matches letter (robust to '(a)', 'a)', 'a.' etc.)."""
            if not letter:
                return ""
            target = letter.strip().lower()[0]
            for opt in options:
                if not opt:
                    continue
                # find first alphabetic char in option (covers '(a)', '(a) text', 'a) text', 'a. text', etc.)
                m = re.search(r'[A-Za-z]', opt)
                if m and m.group(0).lower() == target:
                    return opt.strip()
            return letter  # fallback: return letter if no option matched

        for i, q in enumerate(questions):
            correct_letter = extract_letter(q.get('answer', ""))
            options = q.get('options', []) or []

            user_letter = extract_letter(answers[i] or "")
            user_text = pick_text(user_letter, options) if user_letter else "No answer"
            correct_text = pick_text(correct_letter, options)

            is_correct = (user_letter == correct_letter)
            if is_correct:
                score += 1

            solutions.append({
                'question': q.get('question'),
                'user_answer': user_text,
                'correct_answer': correct_text,
                'is_correct': is_correct
            })

        return render_template(
            "quiz_result.html",
            score=score,
            total=len(questions),
            solutions=solutions
        )
