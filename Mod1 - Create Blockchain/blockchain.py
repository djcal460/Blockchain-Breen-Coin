#Module 1 - Create a blockchain

#importing libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify

#Part 1- Building the blockchain

class Breenchain:
    
    def __init__(self):
        #chain itself
        self.chain  = []
        #genisis block defaults & new blocks
        self.create_block(proof = 1, previous_hash = '0')
            
    def create_block(self, proof, previous_hash):
        block = {'index' : len(self.chain) + 1,
                 'timestamp' : str(datetime.datetime.now()),
                 'proof'  : proof,
                 'previous_hash' : previous_hash }
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
        
#Part 2 - Mining our Blockchain

# Create a Web App
app = Flask(__name__)

# Create an instance of blockchain
breenchain = Breenchain()
        
# Mine a new block
@app.route('/mine_block', methods=['GET'])
def mine_block():
    
    #get previous proof
    previous_block = breenchain.get_previous_block()
    previous_proof =  previous_block['proof']
    
    #get new proof
    proof = breenchain.proof_of_work(previous_proof)
    
    #get previous hash
    previous_hash = breenchain.hash(previous_block)
    
    #create block
    block = breenchain.create_block( proof, previous_hash )
    
    #save response to display block later 
    response = {'message':'Congratulations, you just mined a block!',
                'index' : block['index'],
                'timestamp' : block['timestamp'],
                'proof'  : block['proof'],
                'previous_hash' : block['previous_hash']}
    
    #return response to GET request
    return jsonify(response), 200

# Getting the full blockchain
@app.route('/get_chain', methods=['GET'])
def get_chain():
    response =  {'chain' : breenchain.chain,
                 'length' : len(breenchain.chain) }
    
    #return response to GET request
    return jsonify(response), 200

# Check if blockchain is valid
@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid =  breenchain.is_chain_valid(breenchain.chain)
    if is_valid:
        response = {'message' : 'All good. Breenchain is valid'}
    else:
        response = {'message' : 'Sorry. Breenchain is not valid'}
    #return response to GET request
    return jsonify(response), 200
    
# Running the app on any public ip
app.run( host='0.0.0.0', port =  5000)
  
    
    
    
    
    


