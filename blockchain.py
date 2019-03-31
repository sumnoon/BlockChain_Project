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


    def register_node(self, node_url):
        """
        Add a new node to the list of nodes
        """
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
        """
        Add a vote to votes array if the signature verified
        """
        vote = OrderedDict({'candidate_id': candidate_id})

        self.pending_votes.append(vote)
        
        nonce = self.proof_of_work()
        self.create_block(nonce, self.hash(self.chain[-1]))

        return len(self.chain)


    def hash(self, block):
        """
        Create a SHA-256 hash of a block
        """
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        
        return hashlib.sha256(block_string).hexdigest()


    def valid_proof(self, pending_votes, previous_hash, nonce, difficulty=MINING_DIFFICULTY):
        """
        Check if a hash value satisfies the mining conditions. This function is used within the proof_of_work function.
        """
        guess = (str(pending_votes)+str(previous_hash)+str(nonce)).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:difficulty] == '0'*difficulty


    def proof_of_work(self):
        """
        Proof of work algorithm; Calculates nonce
        """
        last_block = self.chain[-1]
        last_hash = self.hash(last_block)

        nonce = 0
        while self.valid_proof(self.pending_votes, last_hash, nonce) is False:
            nonce += 1

        return nonce

    
    def valid_chain(self, chain):
        """
        check if a blockchain is valid
        """
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
        
    
    def add_account(self, user_name, user_password, voted):
        
        account = {
            'user_id': len(self.accounts) + 1,
            'user_name': user_name,
            'user_password': user_password,
            'voted': False, 
            'user_type': 0
        }

        self.accounts.append(account)
        
        with open('user.json', 'w') as outfile:  
            json.dump(self.accounts, outfile)

    
    def update_voted(self, user_id):
        
        index = 0
        for account in self.accounts:
            if(account['user_id'] == user_id):
                self.accounts[index]['voted'] = True
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

    class Candidate:

    def __init__(self):
        self.candidates = []
        self.load_candidate()


    def load_candidate(self):
        with open('candidate.json') as candidates:  
            all_candidate = json.load(candidates)
            for candidate in all_candidate:
                self.candidates.append(candidate) 
        
        print(self.candidates)

    
    def add_candidate(self, candidate_name):
        
        candidate = {
            'candidate_id': len(self.candidates) + 1,
            'candidate_name': candidate_name,
            'vote_count': 0
        }

        self.candidates.append(candidate)
        
        with open('user.json', 'w') as outfile:  
            json.dump(self.candidates, outfile)


class Current_User():
    def __init__(self, name, password):
        self.user_name = name
        self.password = password
        self.user_type = 0

    def update(self, name, password):
        self.user_name = name
        self.password = password

    def set_user_type(self, user_type):
        self.user_type = user_type

