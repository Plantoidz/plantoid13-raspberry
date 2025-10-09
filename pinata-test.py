from pinata import Pinata

import requests

import os

from dotenv import load_dotenv
load_dotenv('secrets.env')

API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
JWT = os.getenv('JWT')


pinata = Pinata(API_KEY, API_SECRET, JWT)


url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
file = "./Plantoid13-left-small.png"

response1 = pinata.pin_file(file)
ipfsQmeta = response1['data']['IpfsHash']

print(ipfsQmeta)
