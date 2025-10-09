from web3 import Web3
from eth_account import messages
from eth_abi import encode
import sha3

from dotenv import load_dotenv

from pythonosc import udp_client

import os
import time
import json

from pathlib import Path

from pinata import Pinata

import requests


load_dotenv('secrets.env')

API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
JWT = os.getenv('JWT')

PLANTOID_ADDR = os.getenv('PLANTOID_ADDR')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')

METADATA_DB = os.getenv('METADATA_DB')

INFURA_API_KEY = os.getenv('INFURA_API_KEY')


pinata = Pinata(API_KEY, API_SECRET, JWT)
infura_prov = 'https://goerli.infura.io/v3/cc7ca25d68f246f393d7630842360c47'
infura_websock = 'wss://goerli.infura.io/ws/v3/cc7ca25d68f246f393d7630842360c47'





def activatePlantoid(amount, tID):
    print('ACTIVATING THE PLANTOID .....................................\n')

    client = udp_client.SimpleUDPClient('192.168.0.231', 9999)
    client.send_message('/filename', tID)

    
    ### activate the plantooid for a specific amount of time, then create the metadata for the generated seed

    seconds = amount / 100000000000000 # 0.001 eth per second
    client.send_message('/plantoid/255/255/capa/0', 1024)
    print("activated for seconds: " + str(seconds))
    time.sleep(int(seconds))
    client.send_message('/plantoid/255/255/capa/0', 1024)
    print("de-activated")

    create_metadata(tID)

 




def create_metadata(tID):
    
    # pin the wav file to IPFS

    path_rec = '/home/patch/plantoidz-pi/recordings/'
    file = path_rec + tID + '.wav'

    if not os.path.exists(path_rec):
        os.makedirs(path_rec)

    if not os.path.isfile(file):
        Path(file).touch()
   
    response = pinata.pin_file(file)
    print(response)
    ipfsQwav = response['data']['IpfsHash']

    # create the metadata file

    db = {}
    db['description'] = "Plantoid #13 - Seed #" + tID
    db['external_url'] = "http://plantoid.org"
    db['image'] = "https://gateway.pinata.cloud/ipfs/QmQMna9Y3voEHJEZN4YEn9f35ivmr61sernPTbScRcEZzT" # ipfsQpng
    db['animation_url'] = "ipfs://" + ipfsQwav # ipfsQwav
    db['name'] = tID


    path_meta = './metadata/'
    if not os.path.exists(path_meta):
        os.makedirs(path_meta)

    with open(path_meta + tID + '.json', 'w') as outfile:
        json.dump(db, outfile)

    
    ### record in the database that this seed has been processed

    with open('minted.db', 'a') as outfile:
        outfile.write(tID + "\n")


    ### NB: the metadata file will be pinned to IPFS via the node server



def handle_event(event, w3):
    print(event.args.tokenId)

    name = str(event.args.tokenId)

    create_metadata(name)





def log_loop(event_filter, poll_interval, w3):

    line = ""
    processing = 0


    # if db doesn't exist, nothing has been minted yet
    #
    if (not os.path.exists('minted.db')):
        print('processing is null')
        processing = 1

    # if db exists, skip to the lastely minted item
    #
    else:
        with open('minted.db') as file:
            for line in file:
                pass
            last = line
            print("last line = " + last)


    # loop over all entries to process unprocessed Deposits

    for event in event_filter.get_all_entries():
            print('processing : ' + str(processing))
            print(event)

            if (processing == 0):
                print(str(event.transactionHash.hex()))
                print(last)
                print(str(event.args.tokenId) == last)
                if (str(event.args.tokenId) == last.strip()):
                    processing = 1
                    print('processing is true')
                continue

            print('moving to handling event')
            #handle_event(event, w3)
            create_metadata(str(event.args.tokenId))

    time.sleep(poll_interval)

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
    w3 = Web3(Web3.WebsocketProvider(infura_websock))
    print(w3)
    print(w3.isConnected())

    abi = '[{"inputs": [ { "internalType": "uint256", "name": "amount", "type": "uint256", "indexed": false }, { "internalType": "address", "name": "sender", "type": "address", "indexed": false }, { "internalType": "uint256", "name": "tokenId", "type": "uint256", "indexed": true } ], "type": "event", "name": "Deposit", "anonymous": false }]'

    address = Web3.toChecksumAddress(PLANTOID_ADDR)

    contract = w3.eth.contract(address=address, abi=abi)
    print(w3.eth.get_balance(address))

    print("----\n")
    print(w3.eth.account.from_key(PRIVATE_KEY).address)


# event_filter = contract.events.Deposit.createFilter(fromBlock=1, toBlock='latest')
# while True:
# print(event_filter.get_all_entries())
# time.sleep(2)

    print(contract.events.Deposit)

    event_filter = contract.events.Deposit.createFilter(fromBlock=1)
    print(event_filter, "---")

    log_loop(event_filter, 2, w3)


if __name__ == '__main__':
    main()
