import requests
from config_params import SURVEY_MONKEY_TOKEN, INIT_SURVEY_ID, END_SURVEY_ID
import json

s = requests.session()
s.headers.update({
  "Authorization": "Bearer {}".format(SURVEY_MONKEY_TOKEN),
  "Content-Type": "application/json"
})

url_base = "https://api.surveymonkey.net/v3/"


def user_responded_init_survey(user_id, model=None, interface=None, document_set_id=None):
    url = "surveys/{}/responses/bulk".format(INIT_SURVEY_ID)
    a = json.loads(s.get(url_base + url, params={"sort_by": "date_modified",
                                                 "sort_order": "DESC",
                                                 "status": "completed"}).text)
    if model is None:
        for d in a["data"]:
            if d["custom_variables"]["user_id"] == user_id:
                return True
    else:
        for d in a["data"]:
            variables = d["custom_variables"]
            if variables["user_id"] == user_id and variables["model"] == model \
                    and variables['interface'] == interface \
                    and variables['document_set_id'] == document_set_id:
                return True
    return False


def user_responded_ending_survey(user_id, model=None, interface=None, document_set_id=None):
    url = "surveys/{}/responses/bulk".format(END_SURVEY_ID[interface])
    a = json.loads(s.get(url_base + url, params={"sort_by": "date_modified",
                                                 "sort_order": "DESC",
                                                 "status": "completed"}).text)
    if model is None:
        for d in a["data"]:
            if d["custom_variables"]["user_id"] == user_id:
                return True
    else:
        for d in a["data"]:
            variables = d["custom_variables"]
            if variables["user_id"] == user_id and variables["model"] == model \
                    and variables['interface'] == interface \
                    and variables['document_set_id'] == document_set_id:
                return True
    return False


#  print(json.loads(s.get(url_base + "surveys").text))

