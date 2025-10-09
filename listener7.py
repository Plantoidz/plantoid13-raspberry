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

import subprocess



load_dotenv('/home/patch/plantoidz-pi/secrets.env')

API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
JWT = os.getenv('JWT')

PLANTOID_ADDR = os.getenv('PLANTOID_ADDR')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')

METADATA_DB = os.getenv('METADATA_DB')

INFURA_API_KEY = os.getenv('INFURA_API_KEY')


pinata = Pinata(API_KEY, API_SECRET, JWT)


mainnet_plantoid = "0x6949bc5Fb1936407bEDd9F3757DA62147741f2A1"
testnet_plantoid = "0x35fd9840d5489f748908e2cbd356f768b8534f11"

mainnet_infura_prov = 'https://mainnet.infura.io/v3/cc7ca25d68f246f393d7630842360c47'
mainnet_infura_websock = 'wss://mainnet.infura.io/ws/v3/cc7ca25d68f246f393d7630842360c47'

testnet_infura_prov = 'https://sepolia.infura.io/v3/cc7ca25d68f246f393d7630842360c47'
testnet_infura_websock = 'wss://sepolia.infura.io/ws/v3/cc7ca25d68f246f393d7630842360c47'




def activatePlantoid(amount, tID, network):
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

    create_metadata(tID, network)

 

path_rec = './recordings/'



def create_pin_animation2(file, network):
    
    file_stats = os.stat(file)
    token_Id = os.path.splitext(os.path.basename(file))[0]

    if file_stats.st_size:
    # if filesize is > 0, then create a video out of the music .wav
    
        os.system('python3 ' + '/home/patch/plantoidz-pi/sound_visualisation.py ' + 
                  file +
                  " -o " + '/home/patch/plantoidz-pi/videos/' + network + "_" + token_Id + ".mp4 " +
                  " --size 800 --fps 24")
        
        movie_path = '/home/patch/plantoidz-pi/videos/' + network + "_" + token_Id + ".mp4"

    print("pinning file... " + movie_path)

    response = pinata.pin_file(movie_path)
    
    print(response)   
    if(response):
        ipfsQmp4 = response['data']['IpfsHash']
        return ipfsQmp4
    

# def create_pin_animation(file):

#     file_stats = os.stat(file);

#     if file_stats.st_size:
#     # if filesize is > 0, then create a video out of the music .wav
    
#         # for complex commands, with many args, use string + `shell=True`:
#         cmd_str = "xvfb-run /home/patch/plantoidz-pi/processing/processing-java --sketch=/home/patch/plantoidz-pi/videofile --run ../../" + file
#         print(cmd_str)
#         err = subprocess.run(cmd_str, shell=True) # return 0 if works well
#         print(err)
#         if not err.check_returncode():
#             print("pinning the movie to ipfs")
#             file = "/home/patch/plantoidz-pi/videofile/processing-movie.mp4" 

#     print("pinning file... " + file)

#     response = pinata.pin_file(file)
#     print(response)   
#     if(response):
#         ipfsQmp4 = response['data']['IpfsHash']
#         return ipfsQmp4




def create_metadata(tID, network):
    
    # pin the wav file to IPFS

    file = path_rec + tID + '.wav'

    if not os.path.exists(path_rec):
        os.makedirs(path_rec)

    if not os.path.isfile(file):
        # Path(file).touch()
        return


    # create and pin the video processed from the mp3 to ipfs
    #ipfsQmp4 = create_pin_animation(file)
    
    ipfsQmp4 = create_pin_animation2(file, network)


    #response = pinata.pin_file(file)
    #print(response)
    #if(response):
    #    ipfsQwav = response['data']['IpfsHash']

    if(ipfsQmp4):
        os.remove(file)
    else
        return
        

    # create the metadata file

    db = {}
    db['description'] = "Plantoid #13 - Seed #" + tID
    db['external_url'] = "http://plantoid.org"
    db['image'] = "ipfs://QmcNY71soxdqjNhhwQkfLFDGRx4kaVva7ERFiNWa1ZFk5m" # ipfsQpng
    db['animation_url'] = "ipfs://" + ipfsQmp4 # ipfsQwav
    db['name'] = tID


    path_meta = './metadata/'
    if not os.path.exists(path_meta):
        os.makedirs(path_meta)

    with open(path_meta + tID + '.json', 'w') as outfile:
        json.dump(db, outfile)

    
    ### record in the database that this seed has been processed

    with open('minted_' + network + '.db', 'a') as outfile:
        outfile.write(tID + "\n")


    ### NB: the metadata file will be pinned to IPFS via the node server



def handle_event(event, w3):
    print(event.args.tokenId)

    name = str(event.args.tokenId)

    create_metadata(name)





def log_loop(w3main, w3test, main_event_filter, test_event_filter, poll_interval):

    line = ""
    processing_main = 0
    processing_test = 0

    # Check Mainnet Database
    if (not os.path.exists('minted_mainnet.db')):
        print('MAINNET processing is null')
        processing_main = 1
    else:
        with open('minted_mainnet.db') as file:
            for line in file:
                pass
            last_main = line
            print("Mainnet last tID = " + last_main)

     # Check Testnet Database
    if (not os.path.exists('minted_testnet.db')):
        print('TESTNET processing is null')
        processing_test = 1
    else:
        with open('minted_testnet.db') as file:
            for line in file:
                pass
            last_test = line
            print("Testnet last tID = " + last_test)
            

    # loop over all entries to process unprocessed Deposits

    # MAINNET
    print("\n=== Processing Mainnet Historical Entries ===")
    for event in main_event_filter.get_all_entries():
            print(f"Mainnet tokenId: {event.args.tokenId}")
            print("********")

            if (processing_main == 0):
                print(str(event.transactionHash.hex()))
                print(last_main)
                if (str(event.args.tokenId) == last_main.strip()):
                    processing_main = 1
                    print('Mainnet processing is true :)\n')
                continue
            else:
                print("Mainnet processing is still true ...............\n")

            print('moving to handling mainnet event\n')
            create_metadata(str(event.args.tokenId))

    # TESTNET
    print("\n=== Processing Testnet Historical Entries ===")
    for event in test_event_filter.get_all_entries():
        print(f"Testnet tokenId: {event.args.tokenId}")
        print("********")

        if (processing_test == 0):
            print(str(event.transactionHash.hex()))
            print(last_test)
            if (str(event.args.tokenId) == last_test.strip()):
                processing_test = 1
                print('testnet processing is true :)\n')
            continue
        else:
            print("testnet processing is still true ...............\n")

        print('moving to handling testnet event\n')
        create_metadata(str(event.args.tokenId))

    # Monitor for new events on both networks
    
    while(True):

        # MAINNET
        for event in main_event_filter.get_new_entries():
            print("NEW DEPOSIT EVENT on MAINNET")
            print(f"Mainnet tokenId: {event.args.tokenId}")
            activatePlantoid(event.args.amount, str(event.args.tokenId), "mainnet")
        
        # TESTNET
        for event in test_event_filter.get_new_entries():
            print("NEW TESTNET DEPOSIT EVENT!")
            print(f"Testnet tokenId: {event.args.tokenId}")
            activatePlantoid(event.args.amount, str(event.args.tokenId), "testnet")
            
        time.sleep(poll_interval)

            




def main():

   # Local Network
   # local_url = 'http://127.0.0.1:8545'  # Local blockchain address
   # w3 = Web3(Web3.HTTPProvider(local_url))
   # w3 = Web3(Web3.HTTPProvider(infura_prov))
    main_w3 = Web3(Web3.WebsocketProvider(mainnet_infura_websock))
    print("mainnet: " , main_w3)
    print(main_w3.isConnected())
    
    test_w3 = Web3(Web3.WebsocketProvider(testnet_infura_websock))
    print("mainnet: " , test_w3)
    print(test_w3.isConnected())
    
    
    abi = '[{"inputs": [ { "internalType": "uint256", "name": "amount", "type": "uint256", "indexed": false }, { "internalType": "address", "name": "sender", "type": "address", "indexed": false }, { "internalType": "uint256", "name": "tokenId", "type": "uint256", "indexed": true } ], "type": "event", "name": "Deposit", "anonymous": false }]'

    print("Mainnet address == ", mainnet_plantoid, " and Testnet address = ", testnet_plantoid)
    main_address = Web3.toChecksumAddress(mainnet_plantoid)
    test_address = Web3.toChecksumAddress(testnet_plantoid)

    main_contract = main_w3.eth.contract(address=main_address, abi=abi)
    print("Mainnet balance: ", main_w3.eth.get_balance(main_address))

    test_contract = test_w3.eth.contract(address=test_address, abi=abi)
    print("Testnet balance: ", test_w3.eth.get_balance(main_address))
    
    print("--------------------------------------------------------------------\n")


# event_filter = contract.events.Deposit.createFilter(fromBlock=1, toBlock='latest')
# while True:
# print(event_filter.get_all_entries())
# time.sleep(2)

    # print(contract.events.Deposit)

    main_event_filter = main_contract.events.Deposit.createFilter(fromBlock=1)
    print(main_event_filter, "---mainnet")
    
    test_event_filter = test_contract.events.Deposit.createFilter(fromBlock=1)
    print(test_event_filter, "---testnet")

    log_loop(main_w3, test_w3, main_event_filter, test_event_filter, 5)


if __name__ == '__main__':
    main()
