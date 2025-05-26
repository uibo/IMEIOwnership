import os
from pathlib import Path
import json

from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account

BASE_DIR = Path(__file__).parent.resolve()
load_dotenv(BASE_DIR/".env")

SERVER_PRIVATE_KEY = os.getenv("SERVER_PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
RPC_URL = os.getenv("RPC_URL")

with open(BASE_DIR/"IMEIOwnership.abi.json", 'r') as f:
    ABI = json.load(f)

w3 = Web3(Web3.HTTPProvider(RPC_URL))
server_account = Account.from_key(SERVER_PRIVATE_KEY)
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)