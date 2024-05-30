from flask import Flask, render_template, redirect, request, session
from web3 import Web3
from werkzeug.utils import secure_filename
import json
import os
import hashlib

def hash_file(filename):
    h = hashlib.sha1()
    with open(filename, 'rb') as file:
        chunk = 0
        while chunk != b'':
            chunk = file.read(1024)
            h.update(chunk)
    return h.hexdigest()

def connect_to_blockchain(contract_name, acc=0):
    blockchain = os.getenv('BLOCKCHAIN_URL', 'http://127.0.0.1:7545')
    web3 = Web3(Web3.HTTPProvider(blockchain))
    if acc == 0:
        acc = web3.eth.accounts[0]
    web3.eth.defaultAccount = acc
    artifact_path = f"./build/contracts/{contract_name}.json"
    with open(artifact_path) as f:
        contract_json = json.load(f)
        contract_abi = contract_json['abi']
        contract_address = contract_json['networks']['5777']['address']
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)
    return contract, web3

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'sacetc1')
app.config["UPLOAD_FOLDER"] = "static/uploads/"

@app.route('/')
def homePage():
    return render_template('index.html')

@app.route('/registerUser', methods=['POST'])
def registerUser():
    username = request.form['username']
    name = request.form['name']
    password = request.form['password']
    email = request.form['email']
    mobile = request.form['mobile']
    try:
        contract, web3 = connect_to_blockchain('register')
        tx_hash = contract.functions.registerUser(username, name, int(password), email, mobile).transact()
        web3.eth.waitForTransactionReceipt(tx_hash)
        return render_template('index.html', res='Registered Successfully')
    except:
        return render_template('index.html', err='You have already registered')

@app.route('/loginUser', methods=['POST'])
def loginUser():
    username = request.form['username1']
    password = request.form['password1']
    try:
        contract, web3 = connect_to_blockchain('register')
        state = contract.functions.loginUser(username, int(password)).call()
        if state:
            session['username'] = username
            return redirect('/dashboard')
        else:
            return render_template('index.html', err1='Invalid Credentials')
    except:
        return render_template('index.html', err1='First register Account')

@app.route('/dashboard')
def dashboardPage():
    return render_template('dashboard.html')

@app.route('/uploadFile', methods=['POST'])
def uploadImage():
    doc = request.files['chooseFile']
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], session['username'])
    os.makedirs(user_folder, exist_ok=True)
    doc_path = os.path.join(user_folder, secure_filename(doc.filename))
    doc.save(doc_path)
    hashid = hash_file(doc_path)
    try:
        contract, web3 = connect_to_blockchain('fileProtect')
        tx_hash = contract.functions.addFile(session['username'], doc_path, hashid).transact()
        web3.eth.waitForTransactionReceipt(tx_hash)
        return render_template('dashboard.html', res='File uploaded')
    except:
        return render_template('dashboard.html', err='File already uploaded')

@app.route('/myFiles')
def myFiles():
    try:
        files = os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], session['username']))
        data = [[os.path.join(app.config['UPLOAD_FOLDER'], session['username'], f)] for f in files]
    except:
        data = []
    return render_template('myFiles.html', dashboard_data=data, len=len(data))

@app.route('/shareFile')
def shareImage():
    contract, web3 = connect_to_blockchain('register')
    users_data = contract.functions.viewUsers().call()
    data = [[user] for user in users_data[0] if user != session['username']]
    
    try:
        files = os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], session['username']))
        data1 = [[os.path.join(app.config['UPLOAD_FOLDER'], session['username'], f)] for f in files]
    except:
        data1 = []
        
    return render_template('sharefile.html', dashboard_data=data, dashboard_data1=data1, len=len(data), len1=len(data1))

@app.route('/toShareBuddy', methods=['POST'])
def toShareBuddy():
    userId = request.form['userId']
    docId = request.form['docID']
    hashid = hash_file(docId)
    contract, web3 = connect_to_blockchain('fileProtect')
    files_data = contract.functions.viewFiles().call()

    flag = any(hashid == file and userId in tokens for file, tokens in zip(files_data[2], files_data[3]))
    if not flag:
        tx_hash = contract.functions.addToken(hashid, userId).transact()
        web3.eth.waitForTransactionReceipt(tx_hash)

    contract, web3 = connect_to_blockchain('register')
    users_data = contract.functions.viewUsers().call()
    data = [[user] for user in users_data[0] if user != session['username']]
    
    files = os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], session['username']))
    data1 = [[os.path.join(app.config['UPLOAD_FOLDER'], session['username'], f)] for f in files]
    
    return render_template('sharefile.html', err='Already Shared' if flag else 'Shared to Buddy', dashboard_data=data, dashboard_data1=data1, len=len(data), len1=len(data1))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route('/sharedFiles')
def sharedFiles():
    contract, web3 = connect_to_blockchain('fileProtect')
    files_data = contract.functions.viewFiles().call()
    data = [[tokens[0], name] for name, tokens in zip(files_data[1], files_data[3]) if session['username'] in tokens[1:]]
    return render_template('sharedfiles.html', dashboard_data=data, len=len(data))

@app.route('/mysharedfiles')
def mysharedfiles():
    contract, web3 = connect_to_blockchain('fileProtect')
    files_data = contract.functions.viewFiles().call()
    data = [[name, token] for name, tokens in zip(files_data[1], files_data[3]) for token in tokens if files_data[0] == session['username'] and token != session['username']]
    return render_template('mysharedfiles.html', dashboard_data=data, len=len(data))

@app.route('/cancel/static/uploads/<id1>/<id2>/<id3>')
def cancelImage(id1, id2, id3):
    hashid = hash_file(os.path.join(app.config['UPLOAD_FOLDER'], id1, id2))
    contract, web3 = connect_to_blockchain('fileProtect')
    tx_hash = contract.functions.removeToken(hashid, id3).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    return redirect('/mysharedfiles')

if __name__ == "__main__":
    app.run(port=5001, host='0.0.0.0', debug=True)

