# Create a cryptocurrency

#pip install Flask
#pip install requests==2.18.4
#on PC install postman for test

#importing libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

#Part 1- Building the blockchain

class Blockchain:
    
    def __init__(self):
        #chain itself
        self.chain  = []
        
        #before create block need to add some transactions
        self.transactions = []
        
        #genisis block defaults & new blocks
        self.create_block(proof = 1, previous_hash = '0')
        
        # nodes in the network transacting
        self.nodes = set()
            
    def create_block(self, proof, previous_hash):
        block = {'index' : len(self.chain) + 1,
                 'timestamp' : str(datetime.datetime.now()),
                 'proof'  : proof,
                 'previous_hash' : previous_hash,
                 'transactions' : self.transactions }
        
        #must empty the transactions after added to the block
        self.transactions = []
        
        #append the new block to the chain
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        #return last index of the chain
        return self.chain[-1]
    

    #define proof of work (generate nonce)
    def proof_of_work(self, previous_proof):
        
        #new proof starts at 1
        new_proof = 1
        
        #Flag for loop
        check_proof = False
        
        #define problem to be mined/solved
        while check_proof is False:
            
            #operation needs to be asymmetrical (hashlib requires encoded string)
            hash_operation =  hashlib.sha256( str(new_proof**2 - previous_proof**2 ).encode() ).hexdigest()  
            
            #check if first 4 characters are 0000 then found a proof (simple target)
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    #hash a block of the blockchain
    def hash(self, block):
        
        #use json mod to make dict into a json string, encode to be used by hashlib
        encoded_block = json.dumps(block, sort_keys= True).encode()
        
        #return hash of the  block
        return hashlib.sha256(encoded_block).hexdigest()
    
    #check if blockchain is valid
    def is_chain_valid(self, chain):
        
        #start at the beginning of the chain
        previous_block = chain[0]
        block_index = 1
        
        #incr thru all blocks
        while block_index < len(chain):
            block = chain[block_index]
            
            #if current block's prev hash not same as prev block's hash
            if block['previous_hash'] != self.hash(previous_block):
                return False
            
            #check if current and prev proof hash to four leading zeros
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation =  hashlib.sha256( str(proof**2 - previous_proof**2 ).encode() ).hexdigest()  
            if hash_operation[:4] != '0000':
                return False
            
            #update blocks
            previous_block = block
            block_index += 1
        
        #chain is valid
        return True
    
    def add_transaction(self, sender, receiver, amount):
        
        #add transactions
        self.transactions.append({'sender':sender,
                                  'receiver': receiver, 
                                  'amount': amount})
        
        #return new block index 
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1
    
    #add node containing address to set of nodes
    def add_node(self, address):
        
        #parse the address of the node
        parsed_url = urlparse(address)
        
        #add to network (netlock returns url with port)
        self.nodes.add(parsed_url.netloc)
    
    #each node will have their own chain instance, so need to 
    #have consensus among all nodes
    def replace_chain(self):
        
        #get all nodes in network
        network = self.nodes
        longest_chain = None
        
        #set max to this node's length
        max_length = len(self.chain)
        
        #check all nodes in network see if any have a larger length
        for node in network:
            
            #use requests library to get chain of other nodes 
            #and their lengths
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                
                #if that node has a longer chain and that chain is valid
                #change max length and update that node as having the longest chain
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
                    
        # if longest chain is not None, then chain was updated
        # update chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False
        
        
#Part 2 - Mining our Blockchain

# Create a Web App
app = Flask(__name__)

# Create an random unique node address on port 5000
node_address = str(uuid4()).replace('-', '')

# Create an instance of blockchain
blockchain = Blockchain()
        
# Mine a new block
@app.route('/mine_block', methods=['GET'])
def mine_block():
    
    #get previous proof
    previous_block = blockchain.get_previous_block()
    previous_proof =  previous_block['proof']
    
    #get new proof
    proof = blockchain.proof_of_work(previous_proof)
    
    #get previous hash
    previous_hash = blockchain.hash(previous_block)
    
    #add transactions with reward for submitting block
    blockchain.add_transaction(sender = node_address, receiver = 'Emma', amount = 1)
    
    #create block
    block = blockchain.create_block( proof, previous_hash )
    
    #save response to display block later 
    response = {'message':'Congratulations, you just mined a block!',
                'index' : block['index'],
                'timestamp' : block['timestamp'],
                'proof'  : block['proof'],
                'previous_hash' : block['previous_hash'],
                'transactions' : block['transactions']}
    
    #return response to GET request
    return jsonify(response), 200

# Getting the full blockchain
@app.route('/get_chain', methods=['GET'])
def get_chain():
    response =  {'chain' : blockchain.chain,
                 'length' : len(blockchain.chain) }
    
    #return response to GET request
    return jsonify(response), 200

# Check if blockchain is valid
@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid =  blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message' : 'All good. Blockhain is valid'}
    else:
        response = {'message' : 'Sorry. Blockchain is not valid'}
    #return response to GET request
    return jsonify(response), 200

# Adding a new transaction to the Blockchain
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    
    #get json file posted in postman
    json = request.get_json()
    
    #make sure all required keys are in the json file
    transaction_keys = ['sender','receiver','amount']  
    if not all ( key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing!', 400
    
    #otherwise add transaction to the next mined block 
    index =  blockchain.add_transaction(json['sender'],
                                        json['receiver'],
                                        json['amount'])
    
    #return created response for POST
    response = {'message' : f'Transaction was added to block #{index}' }
    return jsonify(response), 201
    
    

  
# Part 3 - Decentralizing Breenchain

# Connecting new nodes
@app.route('/connect_node', methods=['POST'])
def connect_node():
    
    
    #get json file posted in postman
    json = request.get_json()
    
    #add all nodes of json file to blockchain network
    nodes = json.get('nodes')
    
    #check valid key
    if nodes is None:
        return "No node", 400
    
    #add nodes one by one
    for node in nodes:
        blockchain.add_node(node)
    
    response = {'message' : 'All the nodes are now connected. The Breen Coin blockchain now contains the following nodes:',
                'total_nodes' : list(blockchain.nodes) }
    
    #return successful response
    return jsonify(response),201


# Replacing the chain by the longest chain (if this chain is not already the longest)
@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    
    #replace the chain if needed
    is_chain_replaced =  blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message' : 'The nodes had difference chains so this chain was replaced with the longest one',
                    'new_chain' : blockchain.chain }
    else:
        response = {'message' : 'All good. This chain is the largest. It does not need to be updated.',
                    'actual_chain' : blockchain.chain }
    #return response to GET request
    return jsonify(response), 200

# Running the app on any public ip
app.run( host='0.0.0.0', port =  5003)
