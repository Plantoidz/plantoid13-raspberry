from web3 import Web3
from eth_account import messages
from eth_abi import encode
import sha3


from pythonosc import udp_client

import os
import time
import json



import requests

import subprocess



#load_dotenv('/home/patch/plantoidz-pi/secrets.env.goerli')

#PLANTOID_ADDR = os.getenv('PLANTOID_ADDR')
#PRIVATE_KEY = os.getenv('PRIVATE_KEY')

PLANTOID_ADDR = 0x35fD9840D5489f748908e2cbd356F768B8534f11


infura_prov = 'https://sepolia.infura.io/v3/cc7ca25d68f246f393d7630842360c47'
infura_websock = 'wss://sepolia.infura.io/ws/v3/cc7ca25d68f246f393d7630842360c47'





def activatePlantoid(amount, tID):
    print('ACTIVATING THE PLANTOID .....................................\n')

    # client = udp_client.SimpleUDPClient('192.168.0.231', 9999)
    # client = udp_client.SimpleUDPClient('127.0.0.1', 9999) 
    client = udp_client.SimpleUDPClient('255.255.255.255', 9999, True)
    client.send_message('/filename', tID)

    
    ### activate the plantooid for a specific amount of time, then create the metadata for the generated seed

    seconds = amount / 100000000000000 # 0.001 eth per second
    client.send_message('/plantoid/255/255/capa/0', 1024)
    print("activated for seconds: " + str(seconds))
    time.sleep(int(seconds))
    client.send_message('/plantoid/255/255/capa/0', 1024)
    print("de-activated")



def handle_event(event, w3):
    print(event.args.tokenId)

    name = str(event.args.tokenId)

    create_metadata(name)





def log_loop(event_filter, poll_interval, w3):


    while(True):

        for event in event_filter.get_new_entries():
            print("NEW DEPOSIT EVENT TTTTTTTTTTT")
            #handle_event(event, w3)
            activatePlantoid(event.args.amount, str(event.args.tokenId))




def main():

   # Local Network
   # local_url = 'http://127.0.0.1:8545'  # Local blockchain address
   # w3 = Web3(Web3.HTTPProvider(local_url))
   # w3 = Web3(Web3.HTTPProvider(infura_prov))
    
    ### WEBSOCKET
    # w3 = Web3(Web3.WebsocketProvider(infura_websock))
    # websocket_prov = Web3.WebsocketProvider(infura_websock,
    #                                    websocket_timeout=10,
    #                                    websocket_kwargs={'timeout': 10}
    # )
    # w3 = Web3(websocket_prov)

    
    ### HTTP
    print("Connecting via HTTP...")
    w3 = Web3(Web3.HTTPProvider(infura_prov))
    
    print(w3)
    print(w3.isConnected())

    abi = '[{"inputs": [ { "internalType": "uint256", "name": "amount", "type": "uint256", "indexed": false }, { "internalType": "address", "name": "sender", "type": "address", "indexed": false }, { "internalType": "uint256", "name": "tokenId", "type": "uint256", "indexed": true } ], "type": "event", "name": "Deposit", "anonymous": false }]'

    address = Web3.toChecksumAddress(PLANTOID_ADDR)

    contract = w3.eth.contract(address=address, abi=abi)
    print(w3.eth.get_balance(address))

    print("----\n")
#    print(w3.eth.account.from_key(PRIVATE_KEY).address)


# event_filter = contract.events.Deposit.createFilter(fromBlock=1, toBlock='latest')
# while True:
# print(event_filter.get_all_entries())
# time.sleep(2)

    print(contract.events.Deposit)

    event_filter = contract.events.Deposit.createFilter(fromBlock=1)

    log_loop(event_filter, 2, w3)


if __name__ == '__main__':
    main()
