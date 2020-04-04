from flask import Flask, request, render_template, redirect, flash, session, make_response
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys

app = Flask(__name__)
app.config['SECRET_KEY'] = "supersecret"

debug = DebugToolbarExtension(app)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# key names will use to store some things in the session;
# put here as constants so we're guaranteed to be consistent in
# our spelling of these
responses_key = "responses"
current_survey_key = "current_survey"

@app.route('/')
def starter_page():
    """Render starting survey page"""
    
    return render_template('title.html', surveys = surveys)

@app.route('/', methods=["POST"])
def pick_survey():
    """Select a survey"""
    survey_id = request.form["survey_code"]

    # don't let them re-take a survey until cookie times out
    if request.cookies.get(f"completed_{survey_id}"):
        return render_template("already-done.html")

    survey = surveys[survey_id]
    session[current_survey_key] = survey_id
    
    return render_template("survey_start.html", survey=survey)

@app.route('/begin', methods=["POST"])
def handle_question():
    """save response and redirect to the next question"""
    session[responses_key] = []

    return redirect("/question/0")


@app.route('/answer', methods=["POST"])
def add_answer():
    """Save the response and redirect to the next question"""
    # get the response choice
    answer = request.form["choice"]
    text = request.form.get("text", "")
    
    # add this response to the list of the session
    responses = session[responses_key]
    responses.append({"answer": answer, "text": text})
    
    # add this response to the session
    session[responses_key] = responses
    survey_code = session[current_survey_key]
    survey = surveys[survey_code]

    if len(responses) == len(survey.questions):
        return redirect("/thanks")
    else:
        return redirect(f"/question/{len(responses)}")

@app.route('/question/<int:q_id>')
def begin(q_id):
    """Render question page"""
    responses = session.get(responses_key)
    survey_code = session[current_survey_key]
    survey = surveys[survey_code]
    if (responses is None):
        # trying to access question page too soon
        return redirect("/")
    
    if (len(responses) != q_id):
        flash(f"Invalid question id: {q_id}")
        return redirect(f"/question/{len(responses)}")

    q = survey.questions[q_id]
    question = q.question
    choices = q.choices
    allow_text = q.allow_text
    return render_template('question.html', question_num=q_id, question=question, choices=choices, allow_text=allow_text)

@app.route('/thanks')
def thanks():
    """Thank the user and list responses"""

    survey_id = session[current_survey_key]
    survey = surveys[survey_id]
    responses = session[responses_key]

    html = render_template("thanks.html", survey=survey, responses=responses)
    # Set cookie that this survey is complete so they can't redo it
    response = make_response(html)
    response.set_cookie(f"completed_{survey_id}", "yes", max_age=60)
    return response
