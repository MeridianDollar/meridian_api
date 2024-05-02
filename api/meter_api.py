from api.config import *

############################ Meter CAMPAIGN #############################

    
# Task 5 Stake 1000 MST to earn protocol rewards
def meter_staking_pool_1000(address):
    address = Web3.toChecksumAddress(address)
    w3 = check_provider(config["meter"]["rpcs"])
    stakingPool = w3.eth.contract(address=config["meter"]["contracts"]["stakingPool"], abi=abis.stakingPool())
    stake_in_wei = stakingPool.functions.getMstStake(address).call() 
    print(stake_in_wei)
    stake_in_ether = stake_in_wei / CONVERSION_FACTOR
    print(stake_in_ether)
    if stake_in_ether >= 1000:
        return True
    else:
        return False 
    

# Task 6 Stake 2500 MST to earn protocol rewards
def meter_staking_pool_2500(address):
    address = Web3.toChecksumAddress(address)
    w3 = check_provider(config["meter"]["rpcs"])
    stakingPool = w3.eth.contract(address=config["meter"]["contracts"]["stakingPool"], abi=abis.stakingPool())
    stake_in_wei = stakingPool.functions.getMstStake(address).call() 
    print(stake_in_wei)
    stake_in_ether = stake_in_wei / CONVERSION_FACTOR
    print(stake_in_ether)
    if stake_in_ether >= 2500:
        return True
    else:
        return False 
    
    
# Task 7 Stake 5000 MST to earn protocol rewards
def meter_staking_pool_5000(address):
    address = Web3.toChecksumAddress(address)
    w3 = check_provider(config["meter"]["rpcs"])
    otoken = w3.eth.contract(address=config["meter"]["contracts"]["stakingPool"], abi=abis.stakingPool())
    balance_in_wei = otoken.functions.getMstStake(address).call() 
    print(balance_in_wei)
    stake_in_ether = balance_in_wei / CONVERSION_FACTOR
    print(stake_in_ether)
    if stake_in_ether >= 5000:
        return True
    else:
        return False 




# Task 5 Stake 100 MTRG to earn protocol rewards
def meter_lending_mtrg_100(address):
    address = Web3.toChecksumAddress(address)
    w3 = check_provider(config["meter"]["rpcs"])
    otoken = w3.eth.contract(address=config["meter"]["lending_tokens"]["MTRG"]["oToken"], abi=abis.token())
    balance_in_wei = otoken.functions.balanceOf(address).call() 
    balance_in_ether = balance_in_wei / CONVERSION_FACTOR
    print(balance_in_ether)
    if balance_in_ether >= 100:
        return True
    else:
        return False 
    

# Task 6 Stake 250 MTRG to earn protocol rewards
def meter_lending_mtrg_250(address):
    address = Web3.toChecksumAddress(address)
    w3 = check_provider(config["meter"]["rpcs"])
    otoken = w3.eth.contract(address=config["meter"]["lending_tokens"]["MTRG"]["oToken"], abi=abis.token())
    balance_in_wei = otoken.functions.balanceOf(address).call() 
    balance_in_ether = balance_in_wei / CONVERSION_FACTOR
    print(balance_in_ether)
    if balance_in_ether >= 250:
        return True
    else:
        return False 
    

# Task 7 Stake 500 MTRG to earn protocol rewards
def meter_lending_mtrg_500(address):
    address = Web3.toChecksumAddress(address)
    w3 = check_provider(config["meter"]["rpcs"])
    otoken = w3.eth.contract(address=config["meter"]["lending_tokens"]["MTRG"]["oToken"], abi=abis.token())
    balance_in_wei = otoken.functions.balanceOf(address).call() 
    balance_in_ether = balance_in_wei / CONVERSION_FACTOR
    print(balance_in_ether)
    if balance_in_ether >= 500:
        return True
    else:
        return False 