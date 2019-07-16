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
        with open('static/bc/user.json') as users:  
            accounts = json.load(users)
            for account in accounts:
                self.accounts.append(account) 
        
        # print(self.accounts)
        
    
    def add_account(self, user_name, user_password, user_centre):
        
        account = {
            'user_id': len(self.accounts) + 1,
            'user_name': user_name,
            'user_centre': user_centre,
            'user_password': user_password,
            'voted': 0, 
            'user_type': 0
        }

        self.accounts.append(account)
        
        with open('user.json', 'w') as outfile:  
            json.dump(self.accounts, outfile)
        with open('static/bc/user.json', 'w') as outfile:  
            json.dump(self.accounts, outfile)
    
    def update_voted(self, user_name):
        
        index = 0
        for account in self.accounts:
            if(account['user_name'] == user_name):
                self.accounts[index]['voted'] = 1
                with open('user.json', 'w') as outfile:  
                    json.dump(self.accounts, outfile)
                return
            index += 1

    def validate_user(self):
        username = curr_user.user_name
        user_password = curr_user.password
        user_centre = curr_user.user_centre
        print(username)
        print(user_password)
        print(user_centre)
        for account in self.accounts:
            if( account['user_name'] == username and account['user_password'] == user_password and account['user_centre'] == user_centre ):
                curr_user.set_user_type(account['user_type'])
                curr_user.set_voted(account['voted'])
                return True
        return False




class Candidate:

    def __init__(self):
        self.candidates = []
        self.load_candidate()


    def load_candidate(self):
        with open('static/bc/candidate.json') as candidates:  
            all_candidate = json.load(candidates)
            for candidate in all_candidate:
                self.candidates.append(candidate) 
        
        # print(self.candidates)

    
    def add_candidate(self, candidate_name, candidate_centre):   
        candidate = {
            'candidate_id': len(self.candidates) + 1,
            'candidate_name': candidate_name,
            'candidate_centre': candidate_centre,
            'vote_count': 0
        }

        self.candidates.append(candidate)
        
        # print(self.candidates)

        with open('candidate.json', 'w') as outfile:  
            json.dump(self.candidates, outfile)
        with open('static/bc/candidate.json', 'w') as outfile:  
            json.dump(self.candidates, outfile)

    def update_candidate(self, cand_id, cand_centre):
        index = 0
        # print("hi")
        cand_id = int(cand_id)
        cand_name = self.candidates[cand_id-1]['candidate_name']
        #print(cand_name)
        #print(cand_centre)
        for candidate in self.candidates:
            # print(type(candidate['candidate_id']))
            if(candidate['candidate_name'] == cand_name):
                if(candidate['candidate_centre'] == cand_centre):
                    # print("yo")
                    self.candidates[index]['vote_count'] += 1
                    # print(self.candidates[index]['candidate_name'])
                    # print(self.candidates[index]['vote_count'])
                    with open('candidate.json', 'w') as outfile:  
                        json.dump(self.candidates, outfile)
                    with open('static/bc/candidate.json', 'w') as outfile:  
                        json.dump(self.candidates, outfile)
                    return
            index += 1


class Current_User():
    def __init__(self, name, password, centre):
        self.user_name = name
        self.password = password
        self.user_centre = centre
        self.user_type = 0
        self.voted = 0

    def update(self, name, password, centre):
        self.user_name = name
        self.user_centre = centre
        self.password = password

    def set_user_type(self, user_type):
        self.user_type = user_type
    
    def set_voted(self, voted):
        self.voted = voted


app = Flask(__name__)
CORS(app)

blockchain = Blockchain()
curr_user = Current_User('Sumnoon', 'sum', 'Chittagong - 2')
all_usr = User()
all_cand = Candidate()
vote_complete = 0
voter_added = 1
app.config['ENV'] = 'development'
app.config['DEBUG'] = True
app.config['TESTING'] = True



@app.route('/')
def index():
    return render_template('./index.html')


@app.route('/signin', methods = ['POST'])
def signin():
    
    curr_user.update(request.form['username'], request.form['password'], request.form['centre'])
    print(request.form['centre'])
    validate = all_usr.validate_user()
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

@app.route('/submit_voter', methods = ['POST'])
def submit_voter():
    user_account = all_usr.accounts
    username = request.form['username']
    centre = request.form['centre']
    for account in user_account:
        if account['user_name'] == username and account['user_centre'] == centre:
            return render_template("error_insertion.html", content = 0)
    all_usr.add_account(request.form['username'], request.form['password'], request.form['centre'])
    return render_template("add_voter.html")


@app.route('/go_back_voter', methods = ['POST'])
def go_back_voter():
    return render_template("add_voter.html")


@app.route('/addcandidate')
def addcandidate():
    return render_template("add_candidate.html")

@app.route('/submit_candidate', methods = ['POST'])
def submit_candidate():
    candidate_account = all_cand.candidates
    username = request.form['username']
    centre = request.form['centre']
    for account in candidate_account:
        if account['candidate_name'] == username and account['candidate_centre'] == centre:
            return render_template("error_insertion.html", content = 1)
    all_cand.add_candidate(request.form['username'],request.form['centre'])
    return render_template("add_candidate.html")


@app.route('/go_back_candidate', methods = ['POST'])
def go_back_candidate():
    return render_template("add_candidate.html")


@app.route('/addvote')
def addvote():
    if(curr_user.voted == 1): return render_template("add_vote.html", content = curr_user) 
    return render_template("add_vote.html", content = all_cand.candidates, content1 = curr_user)

@app.route('/submitvote', methods = ['POST'])
def submit_vote():
    print(request.form['cand_id'])
    # print("name:" + curr_user.user_name + "vote: {}".format(curr_user.voted))
    if(curr_user.voted == 1):
        return render_template("user_dashboard.html")

    blockchain.submit_vote(request.form['cand_id'])
    all_usr.update_voted(curr_user.user_name)
    curr_user.set_voted(1)
    all_cand.update_candidate(request.form['cand_id'],request.form['cand_centre'])

    return render_template("user_dashboard.html")



@app.route('/publish_result', methods = ['POST'])
def publish_result():
    global vote_complete
    vote_complete = 1
    if curr_user.user_type == 1:
        user_account = all_usr.accounts
        for account in user_account:
            account['voted'] = 1
        return render_template("view_results.html", content = all_cand.candidates)
    else:
        return render_template("view_result.html", content = all_cand.candidates)

@app.route('/start_voting')
def begin_voting():
    global vote_complete
    vote_complete = 0
    user_account = all_usr.accounts
    cand_account = all_cand.candidates
    for account in user_account:
        if account['user_type'] == 0:
            account['voted'] = 0
    for account in cand_account:
        account['vote_count'] = 0
    if curr_user.user_type == 1:
        if vote_complete == 0:
            return render_template("view_results.html", content = vote_complete)
        return render_template("view_results.html", content = all_cand.candidates)

@app.route('/view_result')
def vote_result():
    if curr_user.user_type == 1:
        if vote_complete == 0:
            return render_template("view_results.html", content = vote_complete)
        return render_template("view_results.html", content = all_cand.candidates)
    else:
        if vote_complete == 0:
            return render_template("view_result.html", content = vote_complete)
        return render_template("view_result.html", content = all_cand.candidates)



@app.route('/view_voters')
def view_voters():
    if curr_user.user_type == 1:
        return render_template("view_voters.html", content = all_usr.accounts)
    else:
        return render_template("view_voter.html", content = all_usr.accounts)


@app.route('/view_candidates')
def view_candidates():
    if curr_user.user_type == 1:
        return render_template("view_candidates.html", content = all_cand.candidates)
    else:
        return render_template("view_candidate.html", content = all_cand.candidates)





if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port)