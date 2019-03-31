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
