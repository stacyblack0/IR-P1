# IR-P1
authors: Amifa Raj, Stacy Black, Devan Karsann

## Requirements
* Python 3.6+

## Installation

Use a package manager such as [pip](https://pip.pypa.io/en/stable/) to install the following python libraries:

```bash
pip install color
pip install datetime
pip install flask
pip install IPython
pip install json
pip install nltk
pip install numpy
pip install operator
pip install pandas
pip install pickle
pip install re
pip install sklearn
```

## Website Files

From this repository, the following files are needed to run our project website:
* flask_app.py
* query.py
* querysuggestions.py

Additional processed data files which are needed for the website can be found on our team drive folder, available on special request. Other files in this repository were used to process the data to prepare it for use in the final implementation.

## Running the project

```bash
flask run
```
Troubleshooting: if you see the following error, try running the suggested command:

Error: Could not locate a Flask application. You did not provide the "FLASK_APP" environment variable, and a "wsgi.py" or "app.py" module was not found in the current directory.

* suggested command: export FLASK_APP="flask_app.py"
