from flask import Flask, render_template, request, redirect
import sqlite3
from flask import jsonify
from flask import make_response
import json
import subprocess
from flask_cors import CORS


# running instructions:
# start the server with: FLASK_APP=routes.py flask run

app = Flask(__name__)
CORS(app)

@app.route('/upload', methods=['POST'])
def upload():
    
    print(request.get_json()['inputCount'])
    run_command = "python3 main.py -n " + str(request.get_json()['inputCount']) + " -m " + str(request.get_json()['inputMessage'])

    print(run_command)

    result = subprocess.run(run_command, shell=True, capture_output=True)
    print(result)

    run_command_zoc = "cd zokratesjs && node index.js && cd .."

    zoc_result = subprocess.run(run_command_zoc, shell=True, capture_output=True)

    print(zoc_result)

    with open('certificate.json') as f:
        data1 = json.load(f)
    
    with open('./zokratesjs/proof.json') as f:
        data2 = json.load(f)

    
    response = jsonify({"data1": data1, "data2": data2})
    response.headers['Content-Type'] = 'application/json'

    return response