from flask import Flask, request, render_template, redirect
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

@app.route('/question/<int:q_id>')
def begin(q_id):
    """Render question page"""
    q = satisfaction_survey.questions[q_id]
    question = q.question
    choices = q.choices
    return render_template('question.html', question=question, choices=choices)

@app.route('/answer', methods=["POST"])
def add_answer():
    answer = request.args.get("choice")
    responses.append(answer)
    return redirect("/question/1")
