from web3 import Web3, contract
from web3.contract import ConciseContract

import web3
from .utils import *
from .exceptions import *
from datetime import datetime

import pandas as pd
import requests
import time
import os

# For now only workable with pancakeswap
class Bot():

    contract = None

    def __init__(self,
                setting,
                version=2,
                address=None,
                private_key=None,
                provider="https://bsc-dataseed1.binance.org:443",
                ):

        self.version = version
        self.address = address if address else None
        self.private_key = private_key if private_key else None
        self.provider = provider
        self.w3 = Web3(Web3.HTTPProvider(provider))
        with open(get_path(['assets', 'pancakeswap', 'tokens.json'])) as fp:
            self.tokens = json.load(fp)
        self.setting = setting
        self.router = load_contract(self.w3, 'router', self.setting) if version == 2 else None   # For now deals with V2 only in PS
        self.factory = load_contract(self.w3, 'factory', self.setting) if version == 2 else None   # For now deals with V2 only in PS
        self.main_token = self.w3.toChecksumAddress(self.router.functions.WETH().call())

    #---------------------------Swap Helper Functions---------------------------#

    # Only pass first token to check if it is some other token not main token
    # for approval
    def token_approval(self, token):
        print(token, self.main_token)
        return token != self.main_token

    # Returns function router function of swapping tokens
    # Check swap_token function to find out tuple and dictionary data
    def _build_swap_function(   self,
                                token0: dict,
                                token1: dict,
                                transact_tup: tuple,
                                transact_dict: dict):

        if token0['ADDRESS'] == self.main_token and token0['MAIN_TOKEN']:
            print('swapExactETHForTokens')
            return self.router.functions.swapExactETHForTokens(*transact_tup[1:]).buildTransaction(transact_dict)

        del transact_dict['value']

        if token1['ADDRESS'] == self.main_token and token1['MAIN_TOKEN']:
            print('swapExactTokensForETH')
            return self.router.functions.swapExactTokensForETH(*transact_tup).buildTransaction(transact_dict)
            
        print('swapExactTokensForTokens')
        return self.router.functions.swapExactTokensForTokens(*transact_tup).buildTransaction(transact_dict)

    #---------------------------END---------------------------#

    def set_address(self, addr, key):
        if not self.w3.isConnected():
            return "Not Connected!"

        if self.w3.isAddress(addr):
            try:
                if self.w3.eth.account.from_key(key).address == addr:
                    self.address = addr
                    self.private_key = key
                    return True
            except Exception as e:
                return str(e)
            return "Key and address does not match!"
        return "Invalid Address!"

    def set_contract_get_price_func(self, token0, token1, route=None):

        if not route:
            try:
                # Moved this to utils function to encourage reusability
                # token0 = list(filter(lambda token: token['SYMBOL'].lower() == token0.lower(), self.tokens))[0]
                # token1 = list(filter(lambda token: token['SYMBOL'].lower() == token1.lower(), self.tokens))[0]

                token0 = search_token(token0, self.tokens)
                token1 = search_token(token1, self.tokens)

            except IndexError as error:
                print("Invalid input token...")
                return None

            # get_route resides in utils.py
            route = get_route(token0["ADDRESS"], token1["ADDRESS"])

        token0_dec = int(token0['DECIMAL'])
        token1_dec = int(token1['DECIMAL'])

        self.contract = [self.router.functions.getAmountsOut(   
                                                                10**token0_dec
                                                                if token0_dec == token1_dec
                                                                else
                                                                10**abs(token0_dec - token1_dec),
                                                                route
                                                            ),
                        token0,
                        token1,
                        ]   # First index is contract other two are tokens info from json

    # Utility function to get tokens name
    def get_tokens(self):
        return [t['SYMBOL'] for t in self.tokens]

    # Two tokens and optional route param
    # Contract should contain contract and two token info
    def get_price(self, contract_list: list=None):

        # Try and except to handle Errors such as Contract reversal error 
        # and max tries error (network down error)
        try: 
            # Separating contract and tokens for better readibility
            contract = self.contract[0] if not contract_list else contract_list[0]
            tokens = self.contract[1:] if not contract_list else contract_list[1:]

            # to handle similar address error set 1 to price_list
            price_list = 1 if all(t['ADDRESS'] == tokens[0]['ADDRESS'] for t in tokens) else contract.call()

            if type(price_list) == list:
                # Logic to give a clean price - Please refer this again
                price_mod = any([True if token['PRICE_MOD'] == "true" else False for token in tokens])
                return price_list[-1] if price_mod else price_list[-1] / price_list[0]
            else:
                return price_list
        except requests.exceptions.ConnectionError as e:
            return "-"

    # Get balance of all tokens stated in tokens.json
    def get_balance(self):

        all_balances = []

        if not self.address:
            return ['-' for t in self.tokens]

        for token in self.tokens:
            path = get_path(['assets', 'pancakeswap', 'abi', 'tokens', token['SYMBOL']+'.abi'])

            # Hardcoding BNB tokens for bsc network (cant find token of bnb in bsc)
            # Need modification
            try:
                if not token['SYMBOL'].lower() == 'bnb':
                    with open(path) as fp:
                        abi = fp.read()

                        contract = self.w3.eth.contract(address=self.w3.toChecksumAddress(token['ADDRESS']), 
                                                        ContractFactoryClass=ConciseContract,
                                                        abi=abi)
                        balance = contract.balanceOf(self.address) / (10 ** contract.decimals())
                        
                        all_balances.append(float(balance))
                else:
                    balance = self.w3.eth.get_balance(self.address) / 10 ** 18
                    all_balances.append(balance)

            except Exception as e:
                all_balances.append('-')

        return all_balances

    # Get transactions from an API - IMROVEMENT NEEDED
    # Not used right now
    def get_transactions(self):

        # Now connecting with covalenthq API
        # In future need to try a better method
        headers = {
            'Content-Type': 'application/json',
        }
        # Set Auth to user defined
        auth = ('ckey_db3fb998258c4825ac9a441cb1f', '')

        response = requests.get(
            f'https://api.covalenthq.com/v1/56/address/{self.address}/transactions_v2/',
            headers=headers, auth=auth)

        raw_data = response.json()

        path = get_path(['assets', 'pancakeswap', 'transactions', self.address + '.csv'])

        # Checks if new transactions are added to this particular address
        # Adds them to csv if any updation
        try:

            self.transactions = pd.read_csv(path, index_col=False)

            if len(self.transactions['tx_hashes']) < len(raw_data['items']):
                raise OutdatedTransactions

        except Exception as e:

            transactions_dict =  {
                        'tx_hashes': [  item['tx_hash']
                                        for item in raw_data['data']['items']],
                        'block_signed_at': [datetime.strptime(item['block_signed_at'], "%Y-%m-%dT%H:%M:%SZ") 
                                            for item in raw_data['data']['items']],
                        'block_height': [   item['block_height'] 
                                            for item in raw_data['data']['items']],
                        'token': [  item['log_events'][0]['decoded']['params'][1]['value']
                                    if item['log_events'] and item['log_events'][0]['decoded']['name'] == 'Approval'
                                    else None
                                    for item in raw_data['data']['items']],
                        'type': [   item['log_events'][0]['decoded']['name'] 
                                    if item['log_events']
                                    else None
                                    for item in raw_data['data']['items']],
                        'success': [item['successful'] for item in raw_data['data']['items']]
                    }

            self.transactions = pd.DataFrame(transactions_dict)
            self.transactions.to_csv(self.address + '.csv', index=False)

    #---------------------------Swapping---------------------------#

    # Deposit or withdraw main token - For pancakeswap it is to wrap bnb to make it WBNB
    def deposit_withdraw(self, amount, token: str, deposit: bool=True):

        abi = load_token_abi(token, self.setting['EXCHANGE'])
        token_contract = self.w3.eth.contract(address=self.main_token, abi=abi)

        transaction_dict =  {
                                'from': self.address,
                                'value': self.w3.toWei(amount, 'ether'), # This is the WBNB amount I want to Swap from
                                'gas': 250000,
                                'gasPrice': self.w3.toWei('10','gwei'),
                                'nonce': self.w3.eth.get_transaction_count(self.address),
                            }

        if deposit:
            transaction = token_contract.functions.deposit().buildTransaction(transaction_dict)
        else:
            del transaction_dict['value']
            transaction = token_contract.functions.withdraw(int(amount * (10 ** 18))).buildTransaction(transaction_dict)

        signed_tx = self.w3.eth.account.signTransaction(transaction, self.private_key)
        tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)

        return self.w3.toHex(tx_hash)


    # Private function - approve a token
    def approve_token(self, token):

        max_amount = self.w3.toWei(2**64-1,'ether')
        nonce = self.w3.eth.getTransactionCount(self.address)

        # path = get_path(['assets', 'pancakeswap', 'abi', 'tokens', token['SYMBOL']+'.abi'])

        # with open(path) as fp:
        #     abi = fp.read()

        abi = load_token_abi(token['SYMBOL'], self.setting['EXCHANGE'])

        token_contract = self.w3.eth.contract(  address=self.w3.toChecksumAddress(token['ADDRESS']),
                                                abi=abi)
        approval_tx = token_contract.functions.approve( self.w3.toChecksumAddress(token['ADDRESS']), 
                                                        max_amount).buildTransaction({
            'from': self.address,
            'nonce': nonce,
        })

        print(approval_tx)
        signed_tx = self.w3.eth.account.signTransaction(approval_tx, self.private_key)
        tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)

        return self.w3.toHex(tx_hash)

    # Swapping Functions incorporating above functions
    # two tokens are passed to swap the 1st token into 2nd token
    def swap_tokens(self, token0: dict, token1: dict, orig_amount: float, slippage: float, price:float=None):
    
        token0_addr = self.w3.toChecksumAddress(token0['ADDRESS'])
        token1_addr = self.w3.toChecksumAddress(token1['ADDRESS'])

        amount = orig_amount * (10 ** 18)
        price = price if price else self.get_price()

        transaction_tuple = (
                                int(amount / price),
                                int(amount * (1 - slippage)),
                                [token0_addr,   # Selling Token
                                token1_addr],   # Purchasing Token
                                self.address,   # self.address
                                int(time.time()) + 100000
                            )

        transaction_dict =  {
                                'from': self.address,
                                'value': self.w3.toWei(orig_amount / price,'ether'), # This is the WBNB amount I want to Swap from
                                'gas': 250000,
                                'gasPrice': self.w3.toWei('10','gwei'),
                                'nonce': self.w3.eth.get_transaction_count(self.address),
                            }
                            
        print('Input Params:\n', transaction_tuple)
        print('Built transaction:\n', transaction_dict)
        transaction = self._build_swap_function(token0, token1, transaction_tuple, transaction_dict)

        print(transaction)

        signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key=self.private_key)
        tx_token = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        return self.w3.toHex(tx_token)

    #---------------------------END---------------------------#

    #---------------------------Transfer---------------------------#

    def transfer(self, token, recipient, amount):

        abi = load_token_abi(token['SYMBOL'], self.setting['EXCHANGE'])
        token_contract = self.w3.eth.contract(address=self.main_token, abi=abi)
        amount = int(amount * 10 ** token['DECIMAL'])

        transfer_tx = token_contract.functions.transfer(recipient, amount)

        signed_tx = self.w3.eth.account.signTransaction(transfer_tx, self.private_key)
        tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)

        return self.w3.toHex(tx_hash)

    #---------------------------END---------------------------#

    def disconnect(self):
        self.address = None
        self.private_key = None