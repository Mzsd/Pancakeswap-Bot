import os
import sys
import json

from web3 import Web3
from typing import Union
from web3.eth import Contract
from .exceptions import InvalidToken
from web3.types import Address, ChecksumAddress
from binance.exceptions import BinanceAPIException
from requests.exceptions import ConnectionError
from binance.client import Client

AddressLike = Union[Address, ChecksumAddress]

#---------------------------Addresses---------------------------#

def get_binance_price(sym_one: str, sym_two: str, config: dict, error=True) -> tuple:

    try:
        client = Client(config['API_KEY'], config['API_SECRET'])

        pair = sym_one + sym_two
        pair_rev = sym_two + sym_one

        try:
            price = str(1 / float(client.get_symbol_ticker(symbol=pair)['price']))
        except BinanceAPIException as e:
            try:
                price = client.get_symbol_ticker(symbol=pair_rev)['price']
            except BinanceAPIException as e:
                price = "-"

        error = True
    except ConnectionError as e:
        if error:
            print("Connection error!")
        
        price = '-'
        error = False
    except BinanceAPIException as e:
        if error:
            print("Binance API error!")
        
        price = '-'
        error = False

    return price, error

#---------------------------Addresses---------------------------#

def _str_to_addr(s: Union[AddressLike, str]) -> Address:
    """Idempotent"""
    if isinstance(s, str):
        if s.startswith("0x"):
            return Address(bytes.fromhex(s[2:]))
        else:
            raise Exception(f"Couldn't convert string '{s}' to AddressLike")
    else:
        return s

def _addr_to_str(a: AddressLike) -> str:
    
    if isinstance(a, str) and a.startswith("0x"):
        addr = Web3.toChecksumAddress(a)
        return addr

    raise InvalidToken(a)

def is_same_address(a1: Union[AddressLike, str], a2: Union[AddressLike, str]) -> bool:
    return _str_to_addr(a1) == _str_to_addr(a2)

def validate_address(a: AddressLike) -> None:
    assert _addr_to_str(a)

#---------------------------Contract---------------------------#

def get_path(dir_names: list) -> str:
    # determine if application is a script file or frozen exe
    if getattr(sys, 'frozen', False):
        path = os.path.dirname(sys.executable)
    elif __file__:
        path = os.path.dirname(__file__)

    # path = os.path.dirname(os.path.abspath(__file__))
    for direct in dir_names:
        path = os.path.join(path, direct)
    return path

def load_contract(w3: Web3, abi_name: str, setting: dict) -> Contract:
    address = Web3.toChecksumAddress(setting[abi_name.upper()])
    return w3.eth.contract(address=address, abi=_load_abi(abi_name, setting['EXCHANGE']))

def load_token_abi(name: str, exchange: str) -> str:
    path = get_path(['assets', exchange, 'abi', 'tokens', f"{name}.abi"])
    return _load_abi(name, exchange, path)

def _load_abi(name: str, exchange: str, path_arg: str=None) -> str:
    path = path_arg if path_arg else get_path(['assets', exchange, 'abi', f"{name}.abi"])
    with open(path) as fp:
        abi: str = json.load(fp)
    
    return abi

def load_setting(exchange: str) -> dict:
    path = get_path(['settings.json'])
    with open(path, 'r') as fp:
        # Getting only provided exchange settings
        setting = list(filter(lambda setting: setting['EXCHANGE'] == exchange, json.load(fp)))[0]
    
    return setting

def get_route(token0: AddressLike, token1: AddressLike):
    return [Web3.toChecksumAddress(token0), Web3.toChecksumAddress(token1)]

def search_token(token_name: str, tokens: list) -> dict:
    return list(filter(lambda token: token['SYMBOL'].lower() == token_name.lower(), tokens))[0]

#---------------------------ParaSwap---------------------------#

def set_route(network: str):
    with open(get_path(['assets', 'paraswap', 'networks.json']), 'r') as fp:
        return json.load(fp)['network']