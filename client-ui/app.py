from flask import Flask, render_template, json, request
import requests
import os

app = Flask(__name__)

@app.route('/', methods=['POST','GET'])
def index():
    return render_template('home.html')

@app.route('/results', methods=['POST','GET'])
def results():
    resultados = requests.post('http://server_decrypt:90/results').text #request the results of the tally from the server. The server handles the counting of the data encrypted
    # print(resultados)
    return render_template('results.html', lista=resultados)

@app.route("/new", methods=["POST","GET"])
def new():
    #delete the tally from mongodb and fill up a new one with all the stats in zero (encrypted)
    requests.post('http://server_decrypt:90/new').text
    
    return render_template("home.html")

   
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7000, debug=True)
