import json
from flask import Flask, render_template, request, make_response
import os
from backend.backend import Server
from config_params import DB_NAME, DB_USER, DATA_PATH, DATA_CONFIG, SHOW_RANK, INIT_SURVEY, FINAL_SURVEY, DB_PASS, DB_HOST
from survey_monkey import user_responded_init_survey, user_responded_ending_survey
from collections import defaultdict
import time
import threading
app = Flask(__name__)
backend_server = Server(os.path.abspath(DATA_PATH), DB_NAME, DB_USER, DB_PASS, DB_HOST, DATA_CONFIG, show_rank=SHOW_RANK)

threads_users = defaultdict(list)


from flask import make_response
from functools import wraps, update_wrapper
from datetime import datetime


def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return update_wrapper(no_cache, view)


@app.route("/")
@nocache
def index():
    return render_template("index.html")


@app.route("/survey/<user_id>/<survey>", methods=["GET"])
@nocache
def check_survey(user_id, survey):
    if survey == "init":
        return make_response(json.dumps({'found_survey': user_responded_init_survey(user_id)}), 200)
    else:
        variables = dict(zip(['model', 'interface', 'document_set_id'], survey.split('-')))
        response = {'found_survey': user_responded_ending_survey(user_id, **variables)}
        if response['found_survey']:
            backend_server.get_user(user_id).finish_survey_experiment()
        return make_response(json.dumps(response), 200)


@app.route("/get_user", methods=["POST"])
@nocache
def get_user():
    user_id = request.get_json()["user_id"]
    survey = backend_server.get_init_survey_data(user_id)
    print(survey)
    if survey is not None:  
        return json.dumps({"survey": survey, "link": INIT_SURVEY.format(user_id)}), 200
    return json.dumps({"survey": None}), 404


@app.route('/working_space', methods=['POST'])
@nocache
def load_user():
    # Setear a true el survey. Si llegó aquí es porque ya hizo la encuesta
    user_id = request.form["user-id"]
    backend_server.set_survey_applied(user_id)
    documents, (title, actions, (document_set_id, model, interface, minutes_passed, seconds_passed)) = backend_server.load_experiment(user_id)

    print(len(actions))
    return render_template("working_space.html", document_set_title=title,
                           user_id=user_id, document_set=json.dumps(documents),
                           transformations=backend_server.get_transformations(), actions=json.dumps(actions),
                           document_set_id= document_set_id, model=model, interface=interface, minutes_passed=minutes_passed, seconds_passed=seconds_passed,
                           start_survey=backend_server.do_survey_now(user_id))


@app.route("/send_feedback/<user_id>/<minutes>/<seconds>", methods=["POST"])
@nocache
def send_feedback(user_id, minutes, seconds):
    if backend_server.get_user(user_id) is None:
        return make_response(json.dumps({"documents": []}), 401)
    else:
        data = request.get_json()

        documents = data['documents']
        feedback = data["feedback"]
        user_id = data["user_id"]
        actions = data["actions"]
        documents = backend_server.add_feedback(user_id, documents, feedback, actions)
        print(time.gmtime(), 'sending')

        save_thread(user_id, minutes, seconds)
        if "end" in data and data['end'] == True:
            backend_server.remove_user(user_id)
            return make_response('Sesión terminada', 200)
        print(time.gmtime())
        return json.dumps({'documents': documents}), 200

def save_thread(user_id, minutes, seconds):
    thread = threading.Thread(target=backend_server.save_user, args=(user_id, minutes, seconds))
    thread.start()


@app.route("/change_transformation/<user_id>/<transformation>", methods=["POST"])
@nocache
def change_transformation(user_id, transformation):
    data = request.get_json()
    documents = backend_server.change_transformation(user_id, transformation, data["ids"], data["classes"])
    return json.dumps({'documents': documents}), 200


@app.route("/finish_session/<user_id>/<minutes>/<seconds>", methods=["GET"])
@nocache
def finish_session(user_id, minutes, seconds):
    try:
        backend_server.save_user(user_id, minutes, seconds)
        backend_server.remove_user(user_id)
        return make_response('Sesión terminada', 200)
    except KeyError:
        return make_response('User not active', 404)


@app.route("/get_experiment_survey/<user_id>", methods=["GET"])
@nocache
def get_survey_data(user_id):
    document_set, interface, algorithm = backend_server.get_final_survey_data(user_id)
    experiments_left = backend_server.get_experiments_left(user_id)
    return json.dumps({"link": FINAL_SURVEY[interface].format(document_set, user_id, algorithm, interface), "experiments_left": experiments_left}), 200


@app.route("/finish_experiment/<user_id>/<minutes>/<seconds>", methods=["GET"])
@nocache
def finish_experiment(user_id, minutes, seconds):
    save_thread(user_id, minutes, seconds)
    backend_server.finish_experiment(user_id)
    return make_response('Experimento terminado', 200)


@app.route("/start_experiment/<user_id>", methods=["GET"])
@nocache
def start_experiment(user_id):
    documents, (title, actions, (document_set_id, model, interface, _, _)) = backend_server.start_experiment(user_id)

    return json.dumps({"documents": documents, "document_set_title": title, "document_set_id": document_set_id, "model": model, "interface": interface})


@app.route("/analytics/<user_id>", methods=["POST"])
@nocache
def save_analytics(user_id):
    with open(os.path.join(DATA_PATH, '{}-{}.json'.format(user_id, datetime.now())), 'w+') as f:
        json.dump(request.get_json(), f)
    return make_response('Received', 200)



if __name__ == '__main__':
    app.debug = False
    app.run(threaded=True)
    #server.listen(("0.0.0.0", 5000))
    #server.run(app)
