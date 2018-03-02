# EpisteAid

This program was develop during my master at Pontificia Universidad Católica de Chile. We used[Epistemonikos foundation](https://www.epistemonikos.org/)'s dataset.

I worked on this pretty much by own and with limited time so the code is pretty messy and sometime confusing (specially the templates). I'm trying to spend some time refactoring this but I'm working full time so it can be hard to find some time. If you have any suggestions please use the issues! I'm happy to discuss new features and explain the code.

There are two conferences papers and one arxiv paper related to this research.

- [EpistAid: Interactive Interface for Document Filtering in Evidence-based Health Care
](https://arxiv.org/abs/1611.02119) (2016).
- [
EpistAid: An Interactive Intelligent System for Evidence-based Health Care](https://dl.acm.org/citation.cfm?id=3038281). Presented at the Student Consortium in IUI 2017.
- [An Interactive Relevance Feedback Interface for Evidence-Based Health Care](http://dparra.sitios.ing.uc.cl/pdfs/pre-print-EpistAid-IUI-2018.pdf) (2018, preprint).


## How to use this?
0. Install mysql, python3 and pip
1. Get the data: all the data is available [here](https://drive.google.com/drive/folders/1G4grYQp1qGwkY2A-Xir1C6mbqrB0GH0z?usp=sharing). There are two folders:
    - SQL: sql files that need to be loaded into a mysql database.
    - DataFiles: files that need to be put in `DATA_PATH` in order to be accessed by the program.
2. Get the code: clone or download this repo. Copy the file `config_params_example.py` with the name `config_params.py`. In this new file set all the variables. If you are not using a survey, there's no need to set the variables related to the survey.
3. Install the requirements from `requirements.txt`: pip3 install -r requirements.txt
4. Run the command: python3 main.py. This will launch the application. You can access it at `localhost:5000`. 

### Advanced settings

#### Google Analytics

The interface uses google analytics to track users. Google Analytics has a limit of 500 events per session, so I had to add a new endpoint to the program to keep track of the remaining events. We track several events and save everytime: user, model, interface, medical question and time.

In order to use it you have to set the lines 156 of the template `index.html` and 576 of `working_space.html`.

#### SurveyMonkey

I did this application run all the experiments. Users did not have to change windows to answer the survey. To do this I used survey monkey and the API they provide. I had a paid account so I had access to personalized attributes in the url. I used them to know who had answer the survey.

If you have a paid account you have to create your surveys and complete the `config_params.py` file. You also need to set the variable `USE_SURVEY` to `True` in `config_params.py` and in `variables.js`.

## Questions?

- If you have questions about the code please create an issue!
- If you have questions about the research send me an email to indonoso@uc.cl. I'll be happy to answer you.

