# -*- coding: utf-8 -*-
"""
Created on Sat Sep  1 05:04:20 2018

@author: srinjoy_chakravarty
"""

#Importing the libraries

import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

# Buildling the Auditchain Blockchain

class Auditchain:
    
    def __init__(self):   
      
        #initializes an blockchain instance
        self.chain = []
        self.transactions = []
        self.produce_block(1,'0')
        self.full_nodes = set()


    def produce_block(self, proof, prev_hash):
        
        #appends a new block to the end of the existing blockchain
        block = {'block_index': len(self.chain) + 1, 
                 'digital_timestamp': str(datetime.datetime.now()), 
                 'proof_of_work': proof,
                 'previous_hash': prev_hash,
                 'transactions': self.transactions 
                 }
        self.transactions = []
        self.chain.append(block)
        
        return block
    
    def get_last_block(self):
        
        #returns the latest block of the blockchain
        return self.chain[-1]
    
    def consensus_algorithm(self, previous_proof):
        nonce_value = 2
        golden_nonce = False
        while golden_nonce is False:
            mathcalc = nonce_value**2 - previous_proof**2
            mathstring = str(mathcalc)
            expected_output = mathstring.encode()
            shater512hash = hashlib.sha256(expected_output)
            sickhexa = shater512hash.hexdigest()
            if sickhexa[:6] == '000000':
                golden_nonce = True   
            else:
                nonce_value += 1 
        return nonce_value
    
    def hash_block(self, block):
        
        #hashes all the data contained within the key-value pairs in a block
        sorted_block = json.dumps(block, sort_keys=True)
        encoded_block = sorted_block.encode()
        hashed_block = hashlib.sha256(encoded_block)
        shater256hexa = hashed_block.hexdigest()
        return shater256hexa


    def blockchain_valid(self, chain):
        
        block_index = 1
        previous_block = chain[0]
        
        while block_index < len(chain):
            current_block = chain[block_index]
            
            #validates each new block contains the hash of the previous block
            if current_block['previous_hash'] != self.hash_block(previous_block):
                return False
            else:
                preceding_proof = previous_block['proof_of_work']
                current_proof = current_block['proof_of_work']
                mcalc = current_proof**2 - preceding_proof**2
                mstring = str(mcalc)
                exoutput = mstring.encode()
                shater256hash = hashlib.sha256(exoutput)
                sichex = shater256hash.hexdigest()
                
                #validates that each block was mined using legitimate proof of work
                if sichex[:6] != '000000':
                    return False
                else:
                    previous_block = current_block
                    block_index += 1
        return True

    def attach_transaction(self, sender, recepient, amount):
        
        self.transactions.append({'seller': sender,
                                  'buyer': recepient,
                                  'tokens': amount})
        last_confirmed_block = self.get_last_block()
        return last_confirmed_block['block_index'] + 1
        
    def add_my_node(self, address): 
        parsed_address = urlparse(address)
        url = parsed_address.netloc
        self.full_nodes.add(url)
        
    def replace_with_dominant_chain(self):
        dcarpe_network = self.full_nodes
        bitmains_superchain = None
        max_chainlen = len(self.chain)
        for full_nodes in dcarpe_network:
            http_response = requests.get(f'http://{full_nodes}/fetch_blockchain')
            if http_response.status_code == 200:
                current_chainlen = http_response.json()['length']
                current_chain =   http_response.json()['chain_link']
                if current_chainlen > max_chainlen and self.blockchain_valid(current_chain):
                    max_chainlen = current_chainlen
                    bitmains_superchain = current_chain
                    if bitmains_superchain:
                        self.chain = bitmains_superchain
                        return True
                    else:
                        return False

#creating the web app to act as nodes for the blockchain
app = Flask(__name__)#instantiating the auditchain blockchain

#creating a random address for the node on port 5000 to reward the miner on
rando = uuid4()
rando_string = str(rando)
genesis_node_address = rando_string.replace('-','')

#creating the blockchain instance
audt_blockchain = Auditchain()

# sub-URL within the flask web app that when called mines a new block
@app.route('/asic_mine', methods=['GET'])

# method called by web-app's sub_URL to create a new block by mining it
def asic_mine():
    past_block = audt_blockchain.get_last_block()
    past_proof = past_block['proof_of_work']
    current_proof = audt_blockchain.consensus_algorithm(past_proof)
    past_hash = audt_blockchain.hash_block(past_block)
    audt_blockchain.attach_transaction(sender=genesis_node_address,recepient='srinjoy', amount=8)
    latest_block = audt_blockchain.produce_block(current_proof, past_hash)
    #dictionary data structure to provide a HTTP response dispplay via Postman 
    response = {'message': 'Congratulations, Block Found! As Non-Federated PoW Miner, your Block Reward is 42.5%',
                'block_index': latest_block['block_index'],
                'timestamp': latest_block['digital_timestamp'],
                'proof': latest_block['proof_of_work'],
                'hash': latest_block['previous_hash'],
                'kept_transactions': latest_block['transactions']
                }
    return jsonify(response), 200

# fetches and displays the entire blockchain along with its current length
@app.route('/fetch_blockchain', methods=['GET'])
def fetch_blockchain():
    response = {'chain_link': audt_blockchain.chain,
                'length': len(audt_blockchain.chain)
                }
    return jsonify(response), 200

#checking to see if all blocks of the chain are valid and follow rules
@app.route('/blockchain_valid', methods=['GET'])
def blockchain_valid():
    validity = audt_blockchain.blockchain_valid(audt_blockchain.chain)
    if validity:
        response = {'message': 'Congratulations, Auditchain is healthy and running'}
    else:
        response = {'message': 'Yikes, Auditchain has hardforked!'}
    return jsonify(response), 200

#adding a new transaction to the blockchain
@app.route('/post_transaction', methods=['POST'])
def post_transaction():
    temp_json_dictionary = request.get_json()
    transaction_keyset = ['sender', 'recepient', 'amount']
    if not all (key in temp_json_dictionary for key in transaction_keyset):
        return 'A critical transation detail is missing', 400
    transaction_index = audt_blockchain.attach_transaction(temp_json_dictionary['sender'], temp_json_dictionary['recepient'], temp_json_dictionary['amount'])
    response = {'message': f'This transaction has been added to the mempool and will be picked up by miners at Block Height {transaction_index}'}
    return jsonify(response), 201

#onboarding new nodes into the dcarpe alliance network of nodes
@app.route('/onboard_node', methods=['POST'])   
def onboard_node():
    temp_json_dic = request.get_json()
    file_of_nodes = temp_json_dic.get('nodes')
    if file_of_nodes is None:
        return "There are no new nodes to be added from your json file", 400
    else:
        node_quan = 0    
        for each_node in file_of_nodes:
            audt_blockchain.add_my_node(each_node)
            node_quan += 1
    response = {'message': f'All {node_quan} nodes are now connected to dcarpe alliance network. Their addresses are:',
                'total_nodeset': list(audt_blockchain.full_nodes)}
    return jsonify(response), 201
    
# replacing shorter chains on the network to prevent soft forks and have one single truth
@app.route('/destroy_softforks', methods=['GET'])
def destroy_softforks():
    is_soft_fork = audt_blockchain.replace_with_dominant_chain()
    if is_soft_fork:
        response = {'message': 'Nodes with shorter chain lengths have been replaced with the dominant chain',
                    'new_dominant_chain': audt_blockchain.chain}
    else:
        response = {'message': 'Dcarpe Alliance blockchain network only has one single truth',
                    'original_dominant_chain': audt_blockchain.chain}
    return jsonify(response), 200


#run the blockchain via Flasks' minimalisti web app
app.run(host='0.0.0.0', port=5004)