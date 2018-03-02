#---------- INPUT DATA ----------#
DATA_PATH = "" # Path were it will look for user data
DATA_CONFIG = "=0" # sufix of the files. Files are called output_bow_<type>_<data_config>

#-------- DATABASE --------#
DB_USER = ""
DB_PASS = ""
DB_HOST = ""
DB_NAME = ""

#---------- MODEL ----------#
SHOW_RANK = 30 # How many documents will be shown to the user

#---------- OUTPUT ----------#
STUDY_RESULTS_PATH = "" # path where it will put the output files

#--------- SURVEY ------_---#
# Links to surveys in survey monkey

USE_SURVEY=False
SURVEY_MONKEY_TOKEN = "" # You can get one with in the Developer Page

# Surveys' Links
INIT_SURVEY = "https://es.surveymonkey.com/r/<ID>?user_id={}"
FINAL_SURVEY = {'viz': "https://es.surveymonkey.com/r/<ID>?document_set_id={}&user_id={}&model={}&interface={}",
                'noviz':'https://es.surveymonkey.com/r/<ID>?document_set_id={}&user_id={}&model={}&interface={}'}
# IDs of the surveys. Needed to know if a user answered the survey or not.
INIT_SURVEY_ID = "" # ID of the inital survey 
END_SURVEY_ID = {'viz': '', "noviz": ''} # ID of post surveys