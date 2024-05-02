import time
from api.eth_calls import *
from api.api_calls import *

SUBGRAPH_URL = 'https://subgraph.meridianfinance.net/subgraphs/name/perpetuals-stats'
BASE = 1.0001
START_STATS_TIMESTAMP = 1691849719
INITIAL_MST_SUPPLY = 7000000*10**18
SECONDS_PER_YEAR = 31536000
DAYS_PER_YEAR = 365
LEND_ORACLE_PRECISION = 100000000
MIN_BLOCK_DIFF = 100
BLOCK_INCREMENT = 10000
CONVERSION_FACTOR =  1 * 10 ** 18
RAY = 10**27
WAD = 10**18


with open("json/data.json", "r") as jsonFile:
    store_data = json.load(jsonFile) 
    
with open("json/config.json", "r") as jsonFile:
    config = json.load(jsonFile) 
     
with open("json/prices.json", "r") as jsonFile:
    oracle_prices = json.load(jsonFile) 

def update_data():
    with open("json/data.json", "w") as jsonFile:
        json.dump(store_data, jsonFile)

with open("json/blocks_synced.json", "r") as jsonFile:
    blocks_synced = json.load(jsonFile) 
    
with open("json/borrowers.json", 'r') as file:
    borrowers = json.load(file)

with open("json/lend_yields.json", 'r') as file:
    lend_yields = json.load(file)

def update_lending_yields():
    with open("json/lend_yields.json", "w") as jsonFile:
        json.dump(lend_yields, jsonFile)
        
def update_synced_block():
    with open("json/blocks_synced.json", "w") as jsonFile:
        json.dump(blocks_synced, jsonFile)
               
    
def write_to_json(new_data, file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []

    # Create a dictionary for easier lookup and update of existing entries
    existing_combinations = {(entry['account'], entry['network']): entry for entry in data}

    # Flag to check if the file needs to be updated
    updated = False

    for new_entry in new_data:
        key = (new_entry['account'], new_entry['network'])
        # Check if the health factor exists and is above 10000; if so, skip the update/addition
        if 'healthFactor' in new_entry and new_entry['healthFactor'] > 10000:
            # If the entry exists and should be removed, mark as updated and remove from the dictionary
            if key in existing_combinations:
                del existing_combinations[key]
                updated = True
            continue  # Skip adding or updating this entry in the data list
        
        if key in existing_combinations:
            # Update existing entry with new data
            for field, value in new_entry.items():
                existing_combinations[key][field] = value
            updated = True
        else:
            # Add new entries only if healthFactor <= 10000, which is already checked above
            data.append(new_entry)
            updated = True

    # Reconstruct the data list from existing_combinations to reflect any removals
    updated_data = list(existing_combinations.values())

    # Sort the list by healthFactor from lowest to highest before writing
    sorted_data = sorted(updated_data, key=lambda x: x.get('healthFactor', float('inf')))

    # Write back to the file if there were any updates
    if updated:
        with open(file_path, 'w') as file:
            json.dump(sorted_data, file, indent=4)
            
            
def get_position_info(address, network):
    w3 = check_provider(config[network]["rpcs"])
    walletBalanceProvider = w3.eth.contract(
        address=config[network]["contracts"]["walletBalanceProvider"],
        abi=abis.walletBalanceProvider()
    )
    lendingTokens = config[network]["lending_tokens"]
    
    # Arrays to hold token data
    oTokens = []
    debtTokens = []
    stableDebtTokens = []
    
    tokenAddresses = {}
    
    # Extract token data and addresses
    for symbol, data in lendingTokens.items():
        oTokens.append(data["oToken"])
        debtTokens.append(data["debtToken"])
        if "stableToken" in data:
            stableDebtTokens.append(data["stableToken"])
        tokenAddresses[data["oToken"]] = {"address": data["token"], "symbol": symbol, "decimals": data["decimals"]}
        tokenAddresses[data["debtToken"]] = {"address": data["token"], "symbol": symbol, "decimals": data["decimals"]}
        if "stableToken" in data:
            tokenAddresses[data["stableToken"]] = {"address": data["token"], "symbol": symbol, "decimals": data["decimals"]}

    # Get balances
    userCollateral = walletBalanceProvider.functions.batchBalanceOf([address], oTokens).call()
    userDebt = walletBalanceProvider.functions.batchBalanceOf([address], debtTokens).call()
    userStableDebt = walletBalanceProvider.functions.batchBalanceOf([address], stableDebtTokens).call()
    
    # Determine non-zero balances
    map_collateral = [index for index, value in enumerate(userCollateral) if value != 0]
    map_debt = [index for index, value in enumerate(userDebt) if value != 0]
    map_stable_debt = [index for index, value in enumerate(userStableDebt) if value != 0]
    
    # Prepare results dictionaries, accounting for token decimals
    token_collateral = {}
    for index in map_collateral:
        token_info = tokenAddresses[oTokens[index]]
        adjusted_amount = userCollateral[index] / (10 ** token_info["decimals"])
        if token_info["address"] not in token_collateral:
            token_collateral[token_info["address"]] = {"symbol": token_info["symbol"], "amount": 0}
        token_collateral[token_info["address"]]["amount"] += adjusted_amount

    token_debt = {}
    all_debts = [(debtTokens, userDebt, map_debt), (stableDebtTokens, userStableDebt, map_stable_debt)]
    for tokens, debts, mappings in all_debts:
        for index in mappings:
            token_info = tokenAddresses[tokens[index]]
            adjusted_amount = debts[index] / (10 ** token_info["decimals"])
            if token_info["address"] not in token_debt:
                token_debt[token_info["address"]] = {"symbol": token_info["symbol"], "amount": 0}
            token_debt[token_info["address"]]["amount"] += adjusted_amount

    return {
        address: {
            "collateral": token_collateral,
            "debt": token_debt
        }
    }


def calculate_base_stability_pool_apr(token_price, stability_pool_deposits):
    
    current_time = time.time()
    deployment_time = config["base"]["communityIssuenceStartTime"]
    years_past = (current_time - deployment_time) / (24 * 60 * 60 * 365)
    mstIssuenceDecayFactor = 3000000 * (1 - 0.5 ** years_past)
    annual_issued_value = mstIssuenceDecayFactor * token_price
    
    if stability_pool_deposits == 0: 
        return 0
    apr = (annual_issued_value / stability_pool_deposits) * 100 
    print(f"The current APR is {apr}%")
    return apr



