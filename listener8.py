from web3 import Web3, EthereumTesterProvider
from eth_account import Account, messages
from eth_abi import encode
import sha3

from dotenv import load_dotenv

from pythonosc import udp_client

import os
import time
import json

from pathlib import Path


import requests

import subprocess

import pin_utils


from indexer_client import IndexerClient, IndexerUnavailable


from pinata import Pinata

def _pinata_pin_file_safe(self, file):
    """Replaces Pinata.pin_file to close the file handle (upstream leak)."""

    if not isinstance(file, str):
        raise NotImplementedError("only path strings are supported")
    if not os.path.exists(file):
        return {'status': 'error', 'message': 'File does not exist'}
    
    with open(file, 'rb') as fh:
        raw = requests.post(
            self.base_url + 'pinning/pinFileToIPFS',
            headers=self.headers,
            files={'file': fh},
        ).json()

    if 'error' in raw:
        return {'status': 'error', 'message': raw['error']['details']}
    return {'status': 'success', 'data': raw}

Pinata.pin_file = _pinata_pin_file_safe



load_dotenv('/home/patch/plantoidz-pi/secrets.env')

INDEXER_URL = os.getenv('INDEXER_URL', 'https://plantoidz-brainz.tail98279f.ts.net')

API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
JWT = os.getenv('JWT')


mainnet_plantoid = PLANTOID_ADDR_mainnet = os.getenv('PLANTOID_ADDR_mainnet')
testnet_plantoid = PLANTOID_ADDR_sepolia = os.getenv('PLANTOID_ADDR_sepolia')

METADATA_ADDR = os.getenv('METADATA_ADDR', '0x580fDc17a820e3c0D17fbcd1137483C5332FCeb6')

PRIVATE_KEY = os.getenv('PRIVATE_KEY')
PUBLIC_ADDRESS = os.getenv('PUBLIC_ADDRESS')

METADATA_DB = os.getenv('METADATA_DB')

INFURA_API_KEY = os.getenv('INFURA_API_KEY')
INFURA_API_KEY = "9269205a29344528bb729dd45a25441a"

pinata = Pinata(API_KEY, API_SECRET, JWT)


#mainnet_plantoid = "0x6949bc5Fb1936407bEDd9F3757DA62147741f2A1"
#testnet_plantoid = "0x35fd9840d5489f748908e2cbd356f768b8534f11"


#mainnet_infura_prov = 'https://mainnet.infura.io/v3/cc7ca25d68f246f393d7630842360c47'
#mainnet_infura_websock = 'wss://mainnet.infura.io/ws/v3/cc7ca25d68f246f393d7630842360c47'

#testnet_infura_prov = 'https://sepolia.infura.io/v3/cc7ca25d68f246f393d7630842360c47'
#testnet_infura_websock = 'wss://sepolia.infura.io/ws/v3/cc7ca25d68f246f393d7630842360c47'


mainnet_infura_prov = 'https://mainnet.infura.io/v3/9269205a29344528bb729dd45a25441a'
mainnet_infura_websock = 'wss://mainnet.infura.io/ws/v3/9269205a29344528bb729dd45a25441a'

testnet_infura_prov = 'https://sepolia.infura.io/v3/9269205a29344528bb729dd45a25441a'
testnet_infura_websock = 'wss://sepolia.infura.io/ws/v3/9269205a29344528bb729dd45a25441a'



failsafe = 0


def activatePlantoid(amount, tID, network):
    print('ACTIVATING THE PLANTOID .....................................\n')

    # client = udp_client.SimpleUDPClient('192.168.0.231', 9999)
    # client = udp_client.SimpleUDPClient('127.0.0.1', 9999) 
    # client = udp_client.SimpleUDPClient('255.255.255.255', 9999, True)
    
    client_lights = udp_client.SimpleUDPClient('192.168.1.162', 9999, True)
    client_local  = udp_client.SimpleUDPClient('127.0.0.1', 9999)

    client_local.send_message('/filename', tID)

    
    ### activate the plantooid for a specific amount of time, then create the metadata for the generated seed
    print("Activating plantoid on network == ", network)
    
    seconds = 0
    if(network == "mainnet"):
        seconds = amount / 500000000000000 # 0.01 eth per 20 seconds on MAINNET
    else:
        seconds = amount / 50000000000000 # 0.001 eth per 20 second on TESTNET
        
    client_local.send_message('/plantoid/255/255/capa/0', 1024)
    client_lights.send_message('/plantoid/255/255/capa/0', 1024)
    print("activated for seconds: " + str(seconds))
    time.sleep(int(seconds))
    client_local.send_message('/plantoid/255/255/capa/0', 1024)
    client_lights.send_message('/plantoid/255/255/capa/0', 1024)
    print("de-activated")

    if(network == "mainnet" or failsafe == 0):
        create_metadata(tID, network)
        enable_seed_reveal(tID, network)

 

path_rec = './recordings/'



def create_pin_animation2(file, network):
    
    file_stats = os.stat(file)
    token_Id = os.path.splitext(os.path.basename(file))[0]
    movie_path = None

    if file_stats.st_size:
    # if filesize is > 0, then create a video out of the music .wav
    
        os.system('python3 ' + '/home/patch/plantoidz-pi/sound_visualisation2.py ' + 
                  file +
                  " -o " + '/home/patch/plantoidz-pi/videos/' + network + "_" + token_Id + ".mp4 " +
                  " --fps 24")
        
        movie_path = '/home/patch/plantoidz-pi/videos/' + network + "_" + token_Id + ".mp4"

    if not movie_path: 
        print("NO MOVIE PATH, file_stats == 0")
        return

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
        qrcode = pin_utils.create_ipfs_qr("https://ipfs.io/ipfs/" + ipfsQmp4)
        pin_utils.print_thermal_txt("Redeem your NFT: https://13.plantoid.org")
        pin_utils.print_thermal_img(qrcode)
        os.remove(file)
    else:
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

    with open(path_meta + network + "_" + tID + '.json', 'w') as outfile:
        json.dump(db, outfile)

    
    ### record in the database that this seed has been processed

    # with open('minted_' + network + '.db', 'a') as outfile:
    #     outfile.write(tID + "\n")


    ### NB: the metadata file will be pinned to IPFS via the node server

    ### ---> actually, NOW WE DO IT VIA PYTHON  :)
    # enable_seed_reveal(tID) ### better to move it outside of the function

    
def get_signer_private_key():
    return PRIVATE_KEY

def get_msg_hash(plantoid_address, ipfs_hash, token_Id):

    token_uri = 'ipfs://' + ipfs_hash

    checksum_address =  Web3.to_checksum_address(plantoid_address)

    msgHash = Web3.solidity_keccak(
        ['uint256', 'string', 'address'],
        [token_Id, token_uri, checksum_address],
    )

    def arrayify_bytes(hbytes):
        return [hbytes[i] for i in range(len(hbytes))]

    msgHashArrayified = arrayify_bytes(msgHash)
  
    # print('message hash: ', msgHash.hex())
    # print('message hash arrayified: ', msgHashArrayified)

    return msgHash, msgHash.hex(), msgHashArrayified

def create_signer_and_sign(msg_hash, private_key):
    prepared_message = messages.defunct_hash_message(primitive=msg_hash)
    hash_signed_message = Account.unsafe_sign_hash(prepared_message, private_key) # '0x' + private key
    sig = hash_signed_message.signature.hex()
    return sig

def encode_function_data(plantoid_address, abi_file_path, token_Id, ipfs_hash, sig):

    w3 = Web3()

    with open(abi_file_path, 'r') as f:
        contract_json = json.load(f)
        abi = contract_json#['abi']

    token_Uri = 'ipfs://' + ipfs_hash

    # Get the contract utility using the ABI
    contract = w3.eth.contract(abi=abi)

    checksum_address =  Web3.to_checksum_address(plantoid_address)

    # Encode the function call
    data = contract.encode_abi("revealMetadata", [checksum_address, int(token_Id), token_Uri, bytes.fromhex(sig.replace('0x', ''))])

    return data


def send_relayer_transaction(metadata_address, data):
    w3_polygon = Web3(Web3.HTTPProvider('https://polygon-mainnet.infura.io/v3/' + INFURA_API_KEY))

    signer_private_key = get_signer_private_key()
    account = Account.from_key(signer_private_key)

    # build the tx
    tx = {
    'to': Web3.to_checksum_address(metadata_address),
    'data': data,
    'chainId': 137, # Polygon
    'gas': 100000,
    #'schedule': 'fast',
    'gasPrice': w3_polygon.eth.gas_price,
    'nonce': w3_polygon.eth.get_transaction_count(account.address),
    }

    signed_tx = w3_polygon.eth.account.sign_transaction(tx, signer_private_key)
    tx_hash = w3_polygon.eth.send_raw_transaction(signed_tx.raw_transaction)

    print('sent transaction on Polygon. tx hash = ', tx_hash.hex())


def enable_seed_reveal(tID, network):
    """ Pin metadata to IPFS and send reveal Metadata tx to Polygon"""
    print("call enable seed reveal")

    # get metadata path based on the token ID
    metadata_path = f'./metadata/{network}_{tID}.json'
    if not os.path.isfile(metadata_path):
        print(f'No metadata for seed {tID}, skipping')
        return

    # Pin metadata to IPFS
    response = pinata.pin_file(metadata_path)
    if not response or not response.get('data'):
        print("Pinata pin failed")
        return

    ipfs_hash = response['data']['IpfsHash']
    token_uri = 'ipfs://' + ipfs_hash
    print(f'Pinned metadata: {ipfs_hash}')

    
    # get private key of the signer
    signer_private_key = get_signer_private_key()

    # Create message hash (same as Node.js version)
    plantoid_address = None

    if(network == "mainnet"):
        plantoid_address = Web3.to_checksum_address(PLANTOID_ADDR_mainnet)
    else:
        plantoid_address = Web3.to_checksum_address(PLANTOID_ADDR_sepolia)

    # get the msg hash
    msg_hash, _, _, = get_msg_hash(plantoid_address, ipfs_hash, int(tID))

    # get the signature
    sig = create_signer_and_sign(msg_hash, signer_private_key)

    # get the encoded function data
    abi_file_path = './abis/plantoidMetadata'
    function_data = encode_function_data(plantoid_address, abi_file_path, int(tID), ipfs_hash, sig)

    # send the transaction via polygon network
    send_relayer_transaction(METADATA_ADDR, function_data)

    # Sign the hash
    # prepared = messages.defunct_hash_message(primitive=msg_hash)
    # signed = Account.signHash(prepared, PRIVATE_KEY)
    
    #signed = Account.unsafe_sign_hash(msg_hash, PRIVATE_KEY)
    #sig = signed.signature.hex()

    # Encode the revealMetadata function call
    # iface_abi =  [{"inputs":[{"name":"plantoid","type":"address"},{"name":"tokenId","type":"uint256"},{"name":"tokenUri","type":"string"},{"name":"signature","type":"bytes"}],"name":"revealMetadata","type":"function"}]

    # w3_polygon = Web3(Web3.HTTPProvider('https://polygon-mainnet.infura.io/v3/' + INFURA_API_KEY))
    # contract = w3_polygon.eth.contract(abi=iface_abi)
    # data = contract.encode_abi("revealMetadata", [
    #     plantoid_address, int(tID), token_uri, bytes.fromhex(sig.replace('0x', ''))
    # ])

    # # Send tx to Polygon
    # account = Account.from_key(PRIVATE_KEY)
    # tx = {
    #         'to': Web3.to_checksum_address(METADATA_ADDR),
    #         'data': data,
    #         'chainId': 137,
    #         'gas':100000,
    #         'gasPrice': w3_polygon.eth.gas_price,
    #         'nonce': w3_polygon.eth.get_transaction_count(account.address),
    #         }
    # signed_tx = w3_polygon.eth.account.sign_transaction(tx, PRIVATE_KEY)
    # tx_hash = w3_polygon.eth.send_raw_transaction(signed_tx.raw_transaction)
    # print(f'Sent reveal tx on Polygon: {tx_hash.hex()}')
    
    with open(f'minted_{network}.db', 'a') as f:
        f.write(str(tID)+'\n')



def handle_event(event, w3):
    print(event.args.tokenId)

    name = str(event.args.tokenId)

    create_metadata(name)



def log_loop(w3main, w3test, main_event_filter, test_event_filter, poll_interval,
               main_indexer=None, test_indexer=None):

    # --- catch-up phase: process any historical seeds not yet in minted_<network>.db ---

    def catch_up(network, indexer, event_filter):
        minted_path = f'minted_{network}.db'
        processed = set()
        if os.path.exists(minted_path):
            with open(minted_path) as f:
                processed = {line.strip() for line in f if line.strip()}

        tokens = None
        if indexer is not None:
            try:
                tokens = indexer.fetch_all_token_ids()
                print(f"[indexer:{network}] fetched {len(tokens)} historical tokenIds")
            except IndexerUnavailable as e:
                print(f"[indexer:{network}] catch-up unavailable, falling back to RPC: {e}")

        if tokens is None:
            try:
                tokens = [str(e.args.tokenId) for e in event_filter.get_all_entries()]
            except Exception as err:
                print(f"[{network}] catch-up RPC failed: {err}")
                return

        print(f"\n=== Processing {network} historical entries ===")
        for tid in tokens:
            if tid in processed:
                continue
            print(f"[{network}] catch-up tokenId: {tid}")
            create_metadata(tid, network)
            enable_seed_reveal(tid, network)

    catch_up("mainnet", main_indexer, main_event_filter)
    catch_up("testnet", test_indexer, test_event_filter)

    # --- realtime phase: poll for new deposits ---

    def poll_one(network, indexer, event_filter):
        
        # try indexer first
        if indexer is not None:
            try:
                deposit = indexer.fetch_oldest_unprocessed_deposit()
                if deposit is not None:
                    indexer.advance_cursor(deposit['tokenId'])
                    print(f"[indexer:{network}] new deposit token={deposit['tokenId']} amount={deposit['amount']}")
                    activatePlantoid(deposit['amount'], deposit['tokenId'], network)
                return
            except IndexerUnavailable as e:
                print(f"[indexer:{network}] unavailable, falling back to RPC: {e}")

        # RPC fallback
        for event in event_filter.get_new_entries():
            print(f"[{network}] new deposit token={event.args.tokenId}")
            activatePlantoid(event.args.amount, str(event.args.tokenId), network)

    while True:
        print("checking deposits on Mainnet...")
        poll_one("mainnet", main_indexer, main_event_filter)

        print("checking deposits on Testnet...")
        poll_one("testnet", test_indexer, test_event_filter)

        time.sleep(poll_interval)





def log_loop_old(w3main, w3test, main_event_filter, test_event_filter, poll_interval):

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
            create_metadata(str(event.args.tokenId), "mainnet")
            enable_seed_reveal(str(event.args.tokenId), "mainnet")

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
        create_metadata(str(event.args.tokenId), "testnet")
        enable_seed_reveal(str(event.args.tokenId), "testnet")
    

    # Monitor for new events on both networks
    
    while(True):

        # MAINNET
        print("checking deposits on Mainnet...\n")
        for event in main_event_filter.get_new_entries():
            print("NEW DEPOSIT EVENT on MAINNET")
            print(f"Mainnet tokenId: {event.args.tokenId}")
            activatePlantoid(event.args.amount, str(event.args.tokenId), "mainnet")
        
        # TESTNET
        print("checking deposits on Testnet...\n")
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
    
    #main_w3 = Web3(Web3.WebsocketProvider(mainnet_infura_websock))
    main_w3 = Web3(Web3.HTTPProvider(mainnet_infura_prov))
    print("mainnet: " , main_w3)
    print(main_w3.is_connected())
    
    #test_w3 = Web3(Web3.WebsocketProvider(testnet_infura_websock))
    test_w3 = Web3(Web3.HTTPProvider(testnet_infura_prov))
    print("testnet: " , test_w3)
    print(test_w3.is_connected())

    
    abi = '[{"inputs": [ { "internalType": "uint256", "name": "amount", "type": "uint256", "indexed": false }, { "internalType": "address", "name": "sender", "type": "address", "indexed": false }, { "internalType": "uint256", "name": "tokenId", "type": "uint256", "indexed": true } ], "type": "event", "name": "Deposit", "anonymous": false }]'

    print("Mainnet address == ", mainnet_plantoid, " and Testnet address = ", testnet_plantoid)
    main_address = Web3.to_checksum_address(mainnet_plantoid)
    test_address = Web3.to_checksum_address(testnet_plantoid)

    main_contract = main_w3.eth.contract(address=main_address, abi=abi)
    # print("Mainnet balance: ", main_w3.eth.get_balance(main_address))
    test_contract = test_w3.eth.contract(address=test_address, abi=abi)
    # print("Testnet balance: ", test_w3.eth.get_balance(test_address))
    

    print("--------------------------------------------------------------------\n")

    main_event_filter = main_contract.events.Deposit.create_filter(from_block=1)
    test_event_filter = test_contract.events.Deposit.create_filter(from_block=1)

    main_indexer = IndexerClient(url=INDEXER_URL, plantoid_address=mainnet_plantoid, minted_db_path='minted_mainnet.db') if INDEXER_URL else None
    test_indexer = IndexerClient(url=INDEXER_URL, plantoid_address=testnet_plantoid, minted_db_path='minted_testnet.db') if INDEXER_URL else None


    log_loop(main_w3, test_w3, main_event_filter, test_event_filter, 7,
            main_indexer=main_indexer, test_indexer=test_indexer)


if __name__ == '__main__':
    main()
