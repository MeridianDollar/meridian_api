from api.config import *

############################ FUSE TASKON CAMPAIGN #############################

# Task 1: Open a trove
def fetch_trove_status(address):
    address = Web3.toChecksumAddress(address)
    w3 = check_provider(config["fuse"]["rpcs"])
    troveManger = w3.eth.contract(address=config["fuse"]["contracts"]["troveManager"], abi=abis.troveManager())
    troveStatus = troveManger.functions.getTroveStatus(address).call() 
    if troveStatus == 1:
        return True
    else:
        return False 


# Task 2: Stake $150 or more  in stability pool
# Task 1: Open a trove
def fetchStabilityPool_150(address):
    address = Web3.toChecksumAddress(address)
    w3 = check_provider(config["fuse"]["rpcs"])
    stabilityPool = w3.eth.contract(address=config["fuse"]["contracts"]["stabilityPool"], abi=abis.stabilityPool())
    stake_in_wei = stabilityPool.functions.deposits(address).call() 
    stake_in_ether = stake_in_wei[0] / CONVERSION_FACTOR
    if stake_in_ether >= 150:
        return True
    else:
        return False 
    
    
# Task 3: Stake $500 or more  in stability pool
def fetchStabilityPool_500(address):
    address = Web3.toChecksumAddress(address)
    w3 = check_provider(config["fuse"]["rpcs"])
    stabilityPool = w3.eth.contract(address=config["fuse"]["contracts"]["stabilityPool"], abi=abis.stabilityPool())
    stake_in_wei = stabilityPool.functions.deposits(address).call() 
    stake_in_ether = stake_in_wei[0] / CONVERSION_FACTOR
    if stake_in_ether >= 500:
        return True
    else:
        return False 
    
    
# Task 4: Stake $1000 or more  in stability pool
def fetchStabilityPool_1000(address):
    address = Web3.toChecksumAddress(address)
    w3 = check_provider(config["fuse"]["rpcs"])
    stabilityPool = w3.eth.contract(address=config["fuse"]["contracts"]["stabilityPool"], abi=abis.stabilityPool())
    stake_in_wei = stabilityPool.functions.deposits(address).call() 
    stake_in_ether = stake_in_wei[0] / CONVERSION_FACTOR
    if stake_in_ether >= 1000:
        return True
    else:
        return False 
    
    
# Task 5 Stake 1000 MST to earn protocol rewards
def fetchStakingPool_1000(address):
    address = Web3.toChecksumAddress(address)
    w3 = check_provider(config["fuse"]["rpcs"])
    stakingPool = w3.eth.contract(address=config["fuse"]["contracts"]["stakingPool"], abi=abis.stakingPool())
    stake_in_wei = stakingPool.functions.getMstStake(address).call() 
    print(stake_in_wei)
    stake_in_ether = stake_in_wei / CONVERSION_FACTOR
    print(stake_in_ether)
    if stake_in_ether >= 1000:
        return True
    else:
        return False 
    
    
# Task 6 Stake 2500 MST to earn protocol rewards
def fetchStakingPool_2500(address):
    address = Web3.toChecksumAddress(address)
    w3 = check_provider(config["fuse"]["rpcs"])
    stakingPool = w3.eth.contract(address=config["fuse"]["contracts"]["stakingPool"], abi=abis.stakingPool())
    stake_in_wei = stakingPool.functions.getMstStake(address).call() 
    print(stake_in_wei)
    stake_in_ether = stake_in_wei / CONVERSION_FACTOR
    print(stake_in_ether)
    if stake_in_ether >= 2500:
        return True
    else:
        return False 
    
    
# Task 7 Stake 5000 MST to earn protocol rewards
def fetchStakingPool_5000(address):
    address = Web3.toChecksumAddress(address)
    w3 = check_provider(config["fuse"]["rpcs"])
    stakingPool = w3.eth.contract(address=config["fuse"]["contracts"]["stakingPool"], abi=abis.stakingPool())
    stake_in_wei = stakingPool.functions.getMstStake(address).call() 
    print(stake_in_wei)
    stake_in_ether = stake_in_wei / CONVERSION_FACTOR
    print(stake_in_ether)
    if stake_in_ether >= 5000:
        return True
    else:
        return False 


