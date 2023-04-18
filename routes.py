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
    genCertTime = result.stdout.decode('utf-8').split('\n')[0]

    run_command_zoc = "cd zokratesjs && node index.js && cd .."

    zoc_result = subprocess.run(run_command_zoc, shell=True, capture_output=True)

    compileZokTime = zoc_result.stdout.decode('utf-8').split('\n')[0]
    computeTime = zoc_result.stdout.decode('utf-8').split('\n')[1]
    verifyTime = zoc_result.stdout.decode('utf-8').split('\n')[2]

    print(zoc_result)

    with open('certificate.json') as f:
        data1 = json.load(f)
    
    with open('./zokratesjs/proof.json') as f:
        data2 = json.load(f)


    with open('attest.txt') as f:
        lines = f.read().splitlines()
        data3 = []
        for count, line in enumerate(lines):
            if count < int(request.get_json()['inputCount']):
                public_key, weight = line.split(',')
                data3.append({'public_key': public_key, 'weight': weight})

    
    response = jsonify({"data1": data1, "data2": data2, "data3": data3, "genCertTime": genCertTime, "compileZokTime": compileZokTime, "computeTime": computeTime, "verifyTime": verifyTime})
    response.headers['Content-Type'] = 'application/json'

    return response