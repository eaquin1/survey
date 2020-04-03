from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey

app = Flask(__name__)
app.config['SECRET_KEY'] = "supersecret"

debug = DebugToolbarExtension(app)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# key names will use to store some things in the session;
# put here as constants so we're guaranteed to be consistent in
# our spelling of these
responses_key = "responses"

@app.route('/')
def starter_page():
    """Render starting survey page"""
    survey_title = satisfaction_survey.title
    instructions = satisfaction_survey.instructions
    return render_template('title.html', survey_title=survey_title, instructions=instructions)

@app.route('/session', methods=["POST"])
def set_session():
    """Empty session["responses"}"""
    session[responses_key] = []
    return redirect("/question/0")


@app.route('/answer', methods=["POST"])
def add_answer():
    """Save the response and redirect to the next question"""
    # get the response choice
    answer = request.form["choice"]

    responses = session[responses_key]
    responses.append(answer)
    session[responses_key] = responses
    print(session[responses_key])
    if len(responses) == len(satisfaction_survey.questions):
        return redirect("/thanks")
    else:
        return redirect(f"/question/{len(responses)}")

@app.route('/question/<int:q_id>')
def begin(q_id):
    """Render question page"""
    responses = session.get(responses_key)

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
