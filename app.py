from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey

app = Flask(__name__)
app.config['SECRET_KEY'] = "supersecret"

debug = DebugToolbarExtension(app)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

responses = []
@app.route('/')
def starter_page():
    """Render starting survey page"""
    survey_title = satisfaction_survey.title
    instructions = satisfaction_survey.instructions
    return render_template('title.html', survey_title=survey_title, instructions=instructions)

@app.route('/answer', methods=["POST"])
def add_answer():
    answer = request.form["choice"]
    responses.append(answer)
    if len(responses) == len(satisfaction_survey.questions):
        return redirect("/thanks")
    else:
        return redirect(f"/question/{len(responses)}")

@app.route('/question/<int:q_id>')
def begin(q_id):
    """Render question page"""

    if (responses is None):
        # trying to access question page too soon
        return redirect("/")
    
    if (len(responses) != q_id):
        flash(f"Invalid question id: {q_id}")
        return redirect(f"/question/{len(responses)}")

    q = satisfaction_survey.questions[q_id]
    question = q.question
    choices = q.choices
    return render_template('question.html', question_num=q_id, question=question, choices=choices)

@app.route('/thanks')
def thanks():
    return render_template('thanks.html')
