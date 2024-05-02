
from web3 import Web3
import api.abis as abis
import json

with open("json/config.json", "r") as jsonFile:
    config = json.load(jsonFile) 
    
def check_provider(network_providers):
    for provider in network_providers:
        if network_provider := Web3(Web3.HTTPProvider(provider)):
            return network_provider
        

def update_borrow_rate(w3, network, asset_symbol):
    dataProviderAddress = config[network]["contracts"]["MeridianProtocolDataProvider"]
    dataProviderABI = abis.MeridianProtocolDataProvider()
    dataProviderContract = w3.eth.contract(address=dataProviderAddress, abi=dataProviderABI)
    token = config[network]["lending_tokens"][asset_symbol]["token"]
    print("token", token)
    assetData = dataProviderContract.functions.getReserveData(token).call()
    return assetData[4] 


def update_liquidity_rate(w3, network, asset_symbol):
    dataProviderAddress = config[network]["contracts"]["MeridianProtocolDataProvider"]
    dataProviderABI = abis.MeridianProtocolDataProvider()
    dataProviderContract = w3.eth.contract(address=dataProviderAddress, abi=dataProviderABI)
    assetData = dataProviderContract.functions.getReserveData(config[network]["lending_tokens"][asset_symbol]["token"]).call()
    return assetData[3] 


def get_token_supply(w3, token):
    oTokenContract = w3.eth.contract(address=token, abi=abis.token())
    return oTokenContract.functions.totalSupply().call()


def get_rewards_available(w3, network):
    communityIssuence_contract = w3.eth.contract(address=config[network]["contracts"]["communityIssuence"], abi=abis.communityIssuence())
    return communityIssuence_contract.functions.rewardsAvailable().call()


def lqty_rewards_rate(w3, network):
    communityIssuence_contract = w3.eth.contract(address=config[network]["contracts"]["communityIssuence"], abi=abis.communityIssuence())
    return communityIssuence_contract.functions.rewardsPerSecond().call()


def fetch_stability_pool_deposits(w3, network):
  stability_pool_contract = w3.eth.contract(address=config[network]["contracts"]["stabilityPool"], abi=abis.stabilityPool())
  stability_pool_deposits = stability_pool_contract.functions.getTotalLUSDDeposits().call() 
  return stability_pool_deposits * 10 ** - 18


def get_rewards_per_second(w3, network, address):
    token_contract = w3.eth.contract(address=config[network]["contracts"]["pullRewardsIncentivesController"], abi=abis.pullRewardsIncentivesController())
    rewards_per_second = token_contract.functions.getAssetData(address).call()
    return rewards_per_second[1] * 10 ** -8


def fetch_token_prices(network, w3, asset):
    lend_oracle =  w3.eth.contract(address=config[network]["contracts"]["lend_oracle"], abi=abis.lend_oracle())
    return lend_oracle.functions.getAssetPrice(asset).call() * 10 ** -8
 