from flask import Flask, render_template, request, redirect
import sqlite3
from flask import jsonify
from flask import make_response
import json
import subprocess
from flask_cors import CORS

#

app = Flask(__name__)
CORS(app)

@app.route('/upload', methods=['POST'])
def upload():
    file1 = request.files.get('file1')
    file2 = request.files.get('file2')

    # you now have access to the csv files uploaded and can do whatever you want with them
    print(file1.filename, file2.filename)


    subprocess.call(['python3', 'main.py'])
    
    
    return jsonify({'status': 'success'})












