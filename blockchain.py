from uuid import uuid4
import json
from urllib.parse import urlparse
import hashlib
from collections import OrderedDict

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField


MINING_DIFFICULTY = 2

class Blockchain:

    def __init__(self):
        
        self.pending_votes=[]
        self.chain = []
        self.network_nodes = set()

        self.node_id = str(uuid4()).replace('-', '')
        self.create_block(0, "00")

    
    def create_block(self, nonce, previous_hash):
        block = {
            'block_number': len(self.chain) + 1,
            'votes': self.pending_votes,
            'nonce': nonce,
            'previous_hash': previous_hash
        }

        self.pending_votes = []

        self.chain.append(block)

        with open('blockchain.json', 'w') as outfile:  
            json.dump(self.chain, outfile)
        with open('static/bc/blockchain.json', 'w') as outfile:  
            json.dump(self.chain, outfile)

    def load_block(self):
        with open('static/bc/blockchain.json') as blockchain:  
            blocks = json.load(blockchain)
            for block in blocks:
                self.chain.append(block) 

    def register_node(self, node_url):
        
        #Checking node_url has valid format
        parsed_url = urlparse(node_url)
        
        if parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.network_nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')
        
        # with open('test.json', 'w') as outfile:  
        #     json.dump(self.network_nodes, outfile)


    def submit_vote(self, candidate_id):
        
    
        vote = OrderedDict({'candidate_id': candidate_id})

        self.pending_votes.append(vote)
        
        nonce = self.proof_of_work()
        self.create_block(nonce, self.hash(self.chain[-1]))

        return len(self.chain)


    def hash(self, block):
        
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        
        return hashlib.sha256(block_string).hexdigest()


    def valid_proof(self, pending_votes, previous_hash, nonce, difficulty=MINING_DIFFICULTY):
        
        guess = (str(pending_votes)+str(previous_hash)+str(nonce)).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:difficulty] == '0'*difficulty


    def proof_of_work(self):
        
        last_block = self.chain[-1]
        last_hash = self.hash(last_block)

        nonce = 0
        while self.valid_proof(self.pending_votes, last_hash, nonce) is False:
            nonce += 1

        return nonce

    
    def valid_chain(self, chain):
        
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]

            if block['previous_hash'] != self.hash(last_block):
                return False

            last_block = block
            current_index += 1

        return True

class User:

    def __init__(self):
        self.accounts = []
        self.load_account()


    def load_account(self):
        with open('user.json') as users:  
            accounts = json.load(users)
            for account in accounts:
                self.accounts.append(account) 
        
        # print(self.accounts)
        
    
    def add_account(self, user_name, user_password):
        
        account = {
            'user_id': len(self.accounts) + 1,
            'user_name': user_name,
            'user_password': user_password,
            'voted': 0, 
            'user_type': 0
        }

        self.accounts.append(account)
        
        with open('user.json', 'w') as outfile:  
            json.dump(self.accounts, outfile)

    
    def update_voted(self, user_id):
        
        index = 0
        for account in self.accounts:
            if(account['user_id'] == user_id):
                self.accounts[index]['voted'] = 1
                with open('user.json', 'w') as outfile:  
                    json.dump(self.accounts, outfile)
                return
            index += 1

    def validate_user(self):
        username = curr_user.user_name
        user_password = curr_user.password
        for account in self.accounts:
            if(account['user_name'] == username):
                if(account['user_password'] == user_password):
                    curr_user.set_user_type(account['user_type'])
                    return True
                return False
        return False 



app = Flask(__name__)
CORS(app)

blockchain = Blockchain()
curr_user = Current_User('test', 'test')

@app.route('/')
def index():
    return render_template('./index.html')


@app.route('/signin', methods = ['POST'])
def signin():
    
    curr_user.update(request.form['username'], request.form['password'])
    
    usr = User()
    
    validate = usr.validate_user()

    if(validate == True):
        if curr_user.user_type == 1:
            return render_template("admin_dashboard.html")
        else:
            return render_template("user_dashboard.html")
    else:
        return render_template("index.html")


@app.route('/dashboard')
def dashboard():
    if curr_user.user_type == 1:
            return render_template("admin_dashboard.html")
    else:
        return render_template("user_dashboard.html")


@app.route('/addvoter')
def addvoter():
    return render_template("add_voter.html")


@app.route('/addcandidate')
def addcandidate():
    return render_template("add_candidate.html")


@app.route('/addvote')
def addvote():
    return render_template("add_vote.html")


@app.route('/view_result')
def vote_result():
    return render_template("view_result.html")


@app.route('/view_voters')
def view_voters():
    return render_template("view_voters.html")


@app.route('/view_candidates')
def view_candidates():
    return render_template("view_candidates.html")



if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port)
