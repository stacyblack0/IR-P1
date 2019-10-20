from flask import Flask, request, render_template, Response
import pickle as pkl
import pandas as pd
import numpy as np
from nltk.stem import PorterStemmer
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from IPython.display import display
import operator
import re
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
import color
from flask import jsonify
import json

#ranked documents with titles, snippets, scores
from query import getTop5
#top five suggestions give a query
from querysuggestions import get_top_5_simple

app = Flask(__name__)

#global variables for documents, snippets, scores
tf_idf_test = None
token_2_index = None
docs_content = None
tokenizer = None
stop_words = None
ps = None
results = None

#global variables for query suggestions
df = None
frequencies = None
search = None

form = """
<div class="container">
    <form .justify-content-center method="POST">
        <input class="input-large search-query form-control form-control-lg" type="text" placeholder="enter search query..." name="text">
        <input type="hidden">
    </form><br>
</div>"""

form2 = """
<div class="container">
    <form .justify-content-center method="POST">
        <input class="input-large search-query form-control form-control-lg" type="text" id="ajax" list="json-datalist" placeholder="enter search query..." name="text">
        <datalist id="json-datalist"></datalist>
    </form><br>
</div>"""

top = """
<!DOCTYPE html>
<head>
    <title>search engine yo</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
</head>
<body style="background-color:WhiteSmoke;">
    <div class="jumbotron jumbotron-fluid" style="background-color:transparent !important;">
        <div class="container">
            <h1 class="display-4">Wikipedia Article Search Engine</h1>
            <p class="lead">project by Amifa, Devan, Stacy</p>
        </div>"""

def setup_app(app):
    global tf_idf_test, token_2_index, docs_content, tokenizer, stop_words, ps, results, form, top, df, frequencies, search
    tf_idf_test = pkl.load(open('tf_idf_test.pkl', 'rb'))
    print('tf_idf loaded')
    token_2_index = pkl.load(open('token_2_index.pkl', 'rb'))
    print('token_2_index loaded')
    docs_content = pd.read_csv('docs_content.csv')
    docs_content.drop(columns=['Unnamed: 0', 'id'], inplace=True)
    print('docs_content loaded')
    tokenizer = RegexpTokenizer(r'\w+')
    print('tokenizer set')
    stop_words = set(stopwords.words('english'))
    print('stop_words set')
    ps = PorterStemmer()
    print('ps set')
    df = pkl.load(open('suggestions_df.pkl', 'rb'))
    print('df loaded for suggestions')
    frequencies = pkl.load(open('frequencies.pkl', 'rb'))
    print('frequencies loaded for suggestions')
    print('setup is complete')

setup_app(app)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)

@app.route('/')
def my_form():
    global tf_idf_test, token_2_index, docs_content, tokenizer, stop_words, ps, results, form, top, df, frequencies, search
    return top + form + """
    </div>
    </body>
    """

@app.route('/2')
def my_form_2():
    global tf_idf_test, token_2_index, docs_content, tokenizer, stop_words, ps, results, form, top, df, frequencies, search, form2
    return top + form2 + """
    </div>
    <script type="text/javascript">

    // Get the <datalist> and <input> elements.
    var dataList = document.getElementById('json-datalist');
    var input = document.getElementById('ajax');//.replace(" ", "%");

    // Create a new XMLHttpRequest.
    var request = new XMLHttpRequest();

    $(window).keypress(function (e) {
      if (e.key === ' ' || e.key === 'Spacebar') {
         console.log('javascript --> space pressed');
         input = document.getElementById('ajax');

         //request.open('GET', 'http://127.0.0.1:5000/suggestions?input=' + (input.value).split(" ").join("%"), true);
         //request.send();
         //if (request.readyState === 4) {
         //  if (request.status === 200) {

         var spaceCount = (String(input.value).split(" ").length - 1);
         var inputParam = String(input.value);

         var i;
         for (i = 0; i < spaceCount; i++) {
           inputParam.replace(" ", "%");
         }

         console.log("javascript --> input:");
         // var mystring = "this,is,a,test"
         // var newchar = '|'
         // mystring = mystring.split(',').join(newchar);
         console.log(inputParam);//replace(" ", "%"));

             request = new XMLHttpRequest();
             request.open('GET', String('http://127.0.0.1:5000/suggestions?input=' + inputParam), false);
             request.send();

             // Parse the JSON
             console.log("javascript --> request.responseText:");
             console.log(request.responseText);
             var jsonOptions = JSON.parse(request.responseText);
             console.log("javascript --> jsonOptions");
             console.log("javascript --> " + jsonOptions);

             dataList.innerHTML = '';

             // Loop over the JSON array.
             jsonOptions.forEach(function(item) {
               // Create a new <option> element.
               var option = document.createElement('option');
               // Set the value using the item in the JSON array.
               option.value = item;
               // Add the <option> element to the <datalist>.
               dataList.appendChild(option);
             });

             // Update the placeholder text.
             //input.placeholder = "e.g. datalist";
           } else {
             // An error occured :(
             input.placeholder = "Couldn't load datalist options :(";
           }
         //}
      //}
    });

    // Update the placeholder text.
    //input.placeholder = "Loading options...";

    // Set up and make the request.
    //request.open('GET', String('http://127.0.0.1:5000/suggestions?input=' + String(input.value).replace(" ", "%")), true);
    //request.send();


    </script>
    </body>
    """

def populate_results(row):
    global results
    results += """<div style="background-color:white">""" + """
    <h3>""" + row['title'] + """</h3>
    <p style="background-color:white">""" + row['snippet'] + """</p>
    <p style="background-color:white">score: """ + str(row['score'])[0:5] + """</p></div>"""

@app.route('/', methods=['POST'])
def my_form_post():
    global tf_idf_test, token_2_index, docs_content, tokenizer, stop_words, ps, results, form, top, df, frequencies, search
    text = request.form['text']
    best_results = getTop5(text, ps, stop_words, tokenizer, docs_content, token_2_index, tf_idf_test)

    #suggestions = get_top_5_simple(df, frequencies, text)
    results = ''
    #results += """<div style="background-color:white"><h2>Suggestions</h2>"""
    #results += """<p style="background-color:white">""" + str(suggestions.tolist()) + """</p></div>"""

    for index, row in best_results.iterrows():
        results += """<div style="background-color:white">""" + """
        <h4>""" + row['title'] + """</h4>
        <p style="background-color:white">""" + row['snippet'] + """</p>
        <p style="background-color:white">score: """ + str(row['score'])[0:5] + """</p></div>"""

    processed_output = """<div class="container justify-content-center">""" + results + """</div>"""
    return top + form + """
    <div id = "processed_text">
    """ + processed_output + """
    </div>
    </body>
    """

########
@app.route('/2', methods=['POST'])
def my_form_post_2():
    global tf_idf_test, token_2_index, docs_content, tokenizer, stop_words, ps, results, form, top, df, frequencies, search, form2
    text = request.form['text']
    print('@app.route("/2", methods=["POST"] ==> text = ' + str(text))
    best_results = getTop5(text, ps, stop_words, tokenizer, docs_content, token_2_index, tf_idf_test)

    #suggestions = get_top_5_simple(df, frequencies, text)
    results = ''
    #results += """<div style="background-color:white"><h2>Suggestions</h2>"""
    #results += """<p style="background-color:white">""" + str(suggestions.tolist()) + """</p></div>"""

    for index, row in best_results.iterrows():
        results += """<div style="background-color:white">""" + """
        <h4>""" + row['title'] + """</h4>
        <p style="background-color:white">""" + row['snippet'] + """</p>
        <p style="background-color:white">score: """ + str(row['score'])[0:5] + """</p></div>"""

    processed_output = """<div class="container justify-content-center">""" + results + """</div>"""
    return top + form2 + """
    <div id = "processed_text">
    """ + processed_output + """
    </div>
    <script type="text/javascript">

    // Get the <datalist> and <input> elements.
    var dataList = document.getElementById('json-datalist');
    var input = document.getElementById('ajax');//.replace(" ", "%");

    // Create a new XMLHttpRequest.
    var request = new XMLHttpRequest();

    $(window).keypress(function (e) {
      if (e.key === ' ' || e.key === 'Spacebar') {
         console.log('javascript --> space pressed');
         input = document.getElementById('ajax');

         //request.open('GET', 'http://127.0.0.1:5000/suggestions?input=' + (input.value).split(" ").join("%"), true);
         //request.send();
         //if (request.readyState === 4) {
         //  if (request.status === 200) {

         var spaceCount = (String(input.value).split(" ").length - 1);
         var inputParam = String(input.value);

         var i;
         for (i = 0; i < spaceCount; i++) {
           inputParam.replace(" ", "%");
         }

         console.log("javascript --> input:");
         // var mystring = "this,is,a,test"
         // var newchar = '|'
         // mystring = mystring.split(',').join(newchar);
         console.log(inputParam);//replace(" ", "%"));

             request = new XMLHttpRequest();
             request.open('GET', String('http://127.0.0.1:5000/suggestions?input=' + inputParam), false);
             request.send();

             // Parse the JSON
             console.log("javascript --> request.responseText:");
             console.log(request.responseText);
             var jsonOptions = JSON.parse(request.responseText);
             console.log("javascript --> jsonOptions");
             console.log("javascript --> " + jsonOptions);

             dataList.innerHTML = '';

             // Loop over the JSON array.
             jsonOptions.forEach(function(item) {
               // Create a new <option> element.
               var option = document.createElement('option');
               // Set the value using the item in the JSON array.
               option.value = item;
               // Add the <option> element to the <datalist>.
               dataList.appendChild(option);
             });

             // Update the placeholder text.
             //input.placeholder = "e.g. datalist";
           } else {
             // An error occured :(
             input.placeholder = "Couldn't load datalist options :(";
           }
         //}
      //}
    });

    // Update the placeholder text.
    //input.placeholder = "Loading options...";

    // Set up and make the request.
    //request.open('GET', String('http://127.0.0.1:5000/suggestions?input=' + String(input.value).replace(" ", "%")), true);
    //request.send();


    </script>
    </body>
    """
########

#@app.route('/_get_content/')
#def _get_content():
#    global tf_idf_test, token_2_index, docs_content, tokenizer, stop_words, ps, results, form, top, df, frequencies, search
#    option_id = request.form['option_id']
#    all_options = models.Content.query.filter_by(id=option_id)
#    return jsonify({'data': all_options})

@app.route('/auto')
def auto():
    global tf_idf_test, token_2_index, docs_content, tokenizer, stop_words, ps, results, form, top, df, frequencies, search
    return render_template('auto.html')

@app.route('/suggestions', methods=['GET'])
def ajaxSuggestions():
    global tf_idf_test, token_2_index, docs_content, tokenizer, stop_words, ps, results, form, top, df, frequencies, search
    input = request.args.get("input")
    print('/suggestions --> request.args.get("input") = ' + input)
    input = input.replace("%", " ")
    print('/suggestions --> with spaces: ' + input)
    try:
        suggestions = get_top_5_simple(df, frequencies, input)
        print('/suggestions --> suggestions = ' + str(suggestions.tolist()))
        suggestions_json = json.dumps(suggestions.tolist())
        print('/suggestions --> suggestions_json = ' + suggestions_json)
        return suggestions_json
    except:
        return ""

@app.route('/auto2')
def auto2():
    global tf_idf_test, token_2_index, docs_content, tokenizer, stop_words, ps, results, form, top, df, frequencies, search
    return render_template('auto2.html')
