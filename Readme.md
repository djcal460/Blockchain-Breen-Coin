# Breen Coin Blockchain

### Demo Blockchain 

This project aim was to create a proof-of-work blockchain that uses the made up Breen Coin protocol. Miners are rewarded with 1 Breen Coin for each block mined. Target difficulty is easy at 0000 to mine each block.  The project uses Flask module for the web framework with the API described below. The three modules each act as standalone projects in their own regard but build upon each other. 

* Module 1 - Proof of work blockchain 
* Module 2 - Builds upon module 1 - Adds the Breen Coin protocol
* Module 3 - Builds upon module 1 & 2 - Adds smart contracts using solidity.

# Module 1
There are no coins in this module, builds a single minable blockchain using proof of work algorithm, the ability to verify the blockchain by checking hashes, and view the blockchain.

### Run the Blockchain
```
python blockchain.py
```
* /get_chain - Builds the genisis block on the node and views the chain
* /mine_block - execute transactions by mining block 
* /verify_chain - verify hashes are linked up correctly

# Module 2

### Run the Nodes on the Blockchain
Breen Coin protocol is added to this module. Earn 1 Breen coin per block mined. Transactions get added to the mempool and are added to the mined blocks. There are three nodes provided as scripts to test the blockchain. Run the three nodes and use the connect_node API to connect each node to the other nodes in the network. Wallets are not yet implemented, so can send any amount of Breen Coin per node. Nodes call replace_chain to see if they have the most up to date version of the blockchain and if not they are updated accordingly. 

```
$ python breencoin_node_5001.py
$ python breencoin_node_5002.py
$ python breencoin_node_5003.py
```

### The API
You can use Postman as REST API client to connect your node to the blockchain.
* GET - /get_chain - Builds the genisis block on the node and views the chain
* GET - /mine_block - execute transactions by mining block  
* GET - /replace_chain - update the chain on the current node
* GET - /verify_chain - verify hashes are linked up correctly
* POST - /connect_node - For each node, connect to all other nodes 
   - use json file in API request
      ```
      {
        "nodes": ["http://127.0.0.1:5002",
                "http://127.0.0.1:5003"]
      }
      ```
* POST - /add_transaction -  Add transaction to the mempool
   - use json file in API request
      ```
        {
            'sender': "Bob",
            'receiver': "Anna",
            'amount': 1000
        }
      ```

# Module 3
      
*TO DO*