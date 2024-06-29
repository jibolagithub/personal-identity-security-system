from flask import Flask, render_template, redirect, request, session
from web3 import Web3, HTTPProvider
from werkzeug.utils import secure_filename
import json
import os
import hashlib
import logging

def hash_file(filename):
    """This function returns the SHA-1 hash of the file passed into it."""
    h = hashlib.sha1()
    with open(filename, 'rb') as file:
        chunk = 0
        while chunk != b'':
            chunk = file.read(1024)
            h.update(chunk)
    return h.hexdigest()

def connect_with_register_blockchain(acc):
    blockchain = 'http://127.0.0.1:7545'
    web3 = Web3(HTTPProvider(blockchain))
    if acc == 0:
        acc = web3.eth.accounts[0]
    web3.eth.defaultAccount = acc

    artifact_path = "../build/contracts/register.json"
    with open(artifact_path) as f:
        contract_json = json.load(f)
        contract_abi = contract_json['abi']
        contract_address = contract_json['networks']['5777']['address']
    
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)
    return contract, web3

def connect_with_file_blockchain(acc):
    blockchain = 'http://127.0.0.1:7545'
    web3 = Web3(HTTPProvider(blockchain))
    if acc == 0:
        acc = web3.eth.accounts[0]
    web3.eth.defaultAccount = acc

    artifact_path = "../build/contracts/fileProtect.json"
    with open(artifact_path) as f:
        contract_json = json.load(f)
        contract_abi = contract_json['abi']
        contract_address = contract_json['networks']['5777']['address']
    
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)
    return contract, web3

app = Flask(__name__)
app.secret_key = 'sacetc1'
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
    logging.info(f"Registering user: {username}, {name}, {email}, {mobile}")

    try:
        contract, web3 = connect_with_register_blockchain(0)
        tx_hash = contract.functions.registerUser(username, name, int(password), email, mobile).transact()
        web3.eth.waitForTransactionReceipt(tx_hash)
        return render_template('index.html', res='Registered Successfully')
    except Exception as e:
        logging.error(f"Error registering user: {e}")
        return render_template('index.html', err='You have already registered')

@app.route('/loginUser', methods=['POST'])
def loginUser():
    username = request.form['username1']
    password = request.form['password1']
    logging.info(f"User login attempt: {username}")

    try:
        contract, web3 = connect_with_register_blockchain(0)
        state = contract.functions.loginUser(username, int(password)).call()
        if state:
            session['username'] = username
            return redirect('/dashboard')
        else:
            return render_template('index.html', err1='Invalid Credentials')
    except Exception as e:
        logging.error(f"Error in loginUser function: {e}")
        return render_template('index.html', err1='An error has occurred. Please try again later.')

@app.route('/dashboard')
def dashboardPage():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    return redirect('/')

@app.route('/uploadFile', methods=['POST'])
def uploadImage():
    if 'username' not in session:
        return redirect('/')
    
    doc = request.files['chooseFile']
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], session['username'])
    if not os.path.exists(user_folder):
        os.mkdir(user_folder)
    
    doc1 = secure_filename(doc.filename)
    doc_path = os.path.join(user_folder, doc1)
    doc.save(doc_path)
    hashid = hash_file(doc_path)
    logging.info(f"File uploaded: {doc1}, Hash: {hashid}")

    try:
        contract, web3 = connect_with_file_blockchain(0)
        tx_hash = contract.functions.addFile(session['username'], doc_path, hashid).transact()
        web3.eth.waitForTransactionReceipt(tx_hash)
        return render_template('dashboard.html', res='File uploaded')
    except Exception as e:
        logging.error(f"Error uploading file: {e}")
        return render_template('dashboard.html', err='File already uploaded')

@app.route('/myFiles')
def myFiles():
    if 'username' not in session:
        return redirect('/')

    try:
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], session['username'])
        files = os.listdir(user_folder)
        data = [[os.path.join(user_folder, file)] for file in files]
    except Exception as e:
        logging.error(f"Error retrieving files: {e}")
        data = []
    
    return render_template('myFiles.html', dashboard_data=data, len=len(data))

@app.route('/shareFile')
def shareImage():
    if 'username' not in session:
        return redirect('/')
    
    data = []
    data1 = []
    try:
        contract, web3 = connect_with_register_blockchain(0)
        _usernames, _names, _passwords, _emails, _mobiles = contract.functions.viewUsers().call()
        for i in range(len(_usernames)):
            if _usernames[i] != session['username']:
                data.append([_usernames[i]])
        
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], session['username'])
        files = os.listdir(user_folder)
        for file in files:
            data1.append([os.path.join(user_folder, file)])
    except Exception as e:
        logging.error(f"Error sharing file: {e}")

    return render_template('sharefile.html', dashboard_data=data, dashboard_data1=data1, len=len(data), len1=len(data1))

@app.route('/toShareBuddy', methods=['POST'])
def toShareBuddy():
    if 'username' not in session:
        return redirect('/')
    
    userId = request.form['userId']
    docId = request.form['docID']
    logging.info(f"Sharing file: {docId} with user: {userId}")

    try:
        hashid = hash_file(docId)
        contract, web3 = connect_with_file_blockchain(0)
        _users, _names, _files, _tokens = contract.functions.viewFiles().call()

        flag = 0
        for i in range(len(_files)):
            if hashid == _files[i] and userId in _tokens[i]:
                flag = 1
                break
        
        if flag == 0:
            tx_hash = contract.functions.addToken(hashid, userId).transact()
            web3.eth.waitForTransactionReceipt(tx_hash)

        data, data1 = [], []
        _usernames, _names, _passwords, _emails, _mobiles = contract.functions.viewUsers().call()
        for i in range(len(_users)):
            if _users[i] != session['username']:
                data.append([_users[i]])

        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], session['username'])
        files = os.listdir(user_folder)
        for file in files:
            data1.append([os.path.join(user_folder, file)])

        if flag == 1:
            return render_template('sharefile.html', err='Already Shared', dashboard_data=data, dashboard_data1=data1, len=len(data), len1=len(data1))
        else:
            return render_template('sharefile.html', res='Shared to Buddy', dashboard_data=data, dashboard_data1=data1, len=len(data), len1=len(data1))
    except Exception as e:
        logging.error(f"Error sharing file to buddy: {e}")
        return redirect('/shareFile')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route('/sharedFiles')
def sharedFiles():
    if 'username' not in session:
        return redirect('/')

    data = []
    try:
        contract, web3 = connect_with_file_blockchain(0)
        _users, _names, _files, _tokens = contract.functions.viewFiles().call()
        for i in range(len(_names)):
            if session['username'] in _tokens[i][1:]:
                data.append([_tokens[i][0], _names[i]])
    except Exception as e:
        logging.error(f"Error retrieving shared files: {e}")
    
    return render_template('sharedfiles.html', dashboard_data=data, len=len(data))

@app.route('/mysharedfiles')
def mysharedfiles():
    if 'username' not in session:
        return redirect('/')
    
    data = []
    try:
        contract, web3 = connect_with_file_blockchain(0)
        _users, _names, _files, _tokens = contract.functions.viewFiles().call()
        for i in range(len(_names)):
            if _users[i] == session['username']:
                for j in _tokens[i]:
                    if j != session['username'] and j != '0x0000000000000000000000000000000000000000':
                        data.append([_names[i], j])
    except Exception as e:
        logging.error(f"Error retrieving my shared files: {e}")

    return render_template('mysharedfiles.html', dashboard_data=data, len=len(data))

@app.route('/cancel/static/uploads/<id1>/<id2>/<id3>')
def cancelImage(id1, id2, id3):
    if 'username' not in session:
        return redirect('/')
    
    logging.info(f"Cancelling share of file: {id2} with user: {id3}")
    try:
        hashid = hash_file(os.path.join(app.config['UPLOAD_FOLDER'], id1, id2))
        contract, web3 = connect_with_file_blockchain(0)
        tx_hash = contract.functions.removeToken(hashid, id3).transact()
        web3.eth.waitForTransactionReceipt(tx_hash)
    except Exception as e:
        logging.error(f"Error cancelling shared file: {e}")

    return redirect('/mysharedfiles')

if __name__ == "__main__":
    app.run(port=5001, host='0.0.0.0', debug=True)

