from api.config import * 
  
def get_mst_price():
    price_0 = get_mst_swapsicle_data()
    price_1 = get_mst_uniswap_data()

    if price_0 is not None and price_1 is not None:
        price = (price_0 + price_1) / 2
        store_data["mst_price"] = round(price, 3)
        store_data["mst_price_30"] = int(price*10**30) 
        return price
    elif price_0 is not None:
        store_data["mst_price"] = round(price_0, 3)
        store_data["mst_price_30"] = int(price_0*10**30) 
        return price_0
    elif price_1 is not None:
        store_data["mst_price"] = round(price_1, 3)
        store_data["mst_price_30"] = int(price_1*10**30) 
        return price_1
    else:
        return None

def fetch_mst_stats():
  w3 = check_provider(config["base"]["rpcs"])
  mstPrice = get_mst_price()
  communityIssuence_contract = w3.eth.contract(address=config["base"]["contracts"]["communityIssuence"], abi=abis.communityIssuence())
  totalLQTYIssued = communityIssuence_contract.functions.totalLQTYIssued().call() 
  totalMSTSupply = INITIAL_MST_SUPPLY + totalLQTYIssued
  mcap = (mstPrice * totalMSTSupply) * 10 ** -18
  store_data["mst_supply"] = int(totalMSTSupply); update_data()
  store_data["mst_mcap"] = int(mcap); update_data()
  return mcap
  

def fetch_trove_count():
    networks = list(config.keys())
    number_of_troves = 0
    for network in networks:
      if config[network]["mint_active"] == True:
        try:
            w3 = check_provider(config[network]["rpcs"])
            trove_manager_contract = w3.eth.contract(address=config[network]["contracts"]["troveManager"], abi=abis.troveManager())
            troves_count = trove_manager_contract.functions.getTroveOwnersCount().call()
            number_of_troves += troves_count
            
        except Exception as e:
            print(f"Error fetching TVL for {network}: {e}")
  
    store_data["number_of_troves"] = int(number_of_troves)
    update_data()
    
def fetch_total_tvl():
    tvl = get_liquidity()
    store_data["total_tvl"] = int(tvl)


def fetch_stability_pool_yield():
    networks = list(config.keys())
    for network in networks:
        w3 = check_provider(config[network]["rpcs"])
        if network in ["telos", "fuse"]:
            stability_pool_deposits = fetch_stability_pool_deposits(w3, network)

            rewards_available = get_rewards_available(w3, network)
            
            if not rewards_available:
                store_data["stability_pool"][network] = int(0)
                update_data()
                print("Rewards are not available")
            else:
                rewards_rate = lqty_rewards_rate(w3, network)
                rewards_per_year = rewards_rate * SECONDS_PER_YEAR * 10 ** -18
                token_price = float(oracle_prices[config[network]["coingecko_id"]]['usd'])
                total_rewards_usd = rewards_per_year * token_price

                if total_rewards_usd != 0:
                    stability_pool_yield = (total_rewards_usd / stability_pool_deposits) * 100
                    store_data["stability_pool"][network] = round(stability_pool_yield, 1)
                    update_data()
                else:
                    print("Rewards are not available")
        if network =="base":
            stability_pool_deposits = fetch_stability_pool_deposits(w3, network)
            mstPrice = get_mst_price()
            stability_pool_yield = calculate_base_stability_pool_apr(mstPrice, stability_pool_deposits)
            store_data["stability_pool"][network] = round(stability_pool_yield, 1)
            update_data()


def check_lending_incentives_end_time():
  networks = list(config.keys())
  
  rewards_end_times = {}
  for network in networks:
    if config[network]["lending_incentives"] == True:
      w3 = check_provider(config[network]["rpcs"])
      pullRewardsIncentivesController = w3.eth.contract(address=config[network]["contracts"]["pullRewardsIncentivesController"], abi=abis.pullRewardsIncentivesController())
      rewards_end_time = pullRewardsIncentivesController.functions.getDistributionEnd().call()
      current_time = time.time()
      time_to_rewards_end = (rewards_end_time - current_time) / ( 60 * 60 * 24 )
      print(round(time_to_rewards_end, 2), network)
      rewards_end_times[network] = round(time_to_rewards_end, 2)
  
  
  store_data["incentives"]["lending"] = rewards_end_times; update_data()

    

def check_mint_incentives_end_time():
  networks = list(config.keys())
  
  rewards_end_times = {}
  for network in networks:
    if config[network]["mint_incentives"] == True:
      w3 = check_provider(config[network]["rpcs"])
      community_issuence = w3.eth.contract(address=config[network]["contracts"]["communityIssuence"], abi=abis.communityIssuence())
      rewards_end_time = community_issuence.functions.rewardsEndTime().call()
      current_time = time.time()
      time_to_rewards_end = (rewards_end_time - current_time) / ( 60 * 60 * 24 )
      print(round(time_to_rewards_end, 2), network)
      rewards_end_times[network] = round(time_to_rewards_end, 2)
    
  store_data["incentives"]["mint"] = rewards_end_times; update_data()
  
  
def update_keepers_data(new_data):
    """Update the 'keepers' data by merging new entries."""
    if "keepers" in store_data:
        store_data["keepers"].update(new_data)  # Merges new data with existing data
    else:
        store_data["keepers"] = new_data
    update_data()  # Save the updated data

def check_keeper_balances():
    networks = list(config.keys())
    account_balances = {}
    for network in networks:
        if config[network].get("staking_keeper"):
            w3 = check_provider(config[network]["rpcs"])
            account = config[network]["contracts"]["staking_keeper"]
            balance_wei = w3.eth.getBalance(account)
            ether_balance = balance_wei * 10 ** -18

            if "staking" not in account_balances:
                account_balances["staking"] = {}

            account_balances["staking"][network] = {
                "value": round(ether_balance, 4),
                "address": account
            }

    if account_balances:
        update_keepers_data(account_balances)

def check_oracle_balances():
    networks = list(config.keys())
    oracle_status = {}
    for network in networks:
        if config[network].get("oracle_maintenance"):
            w3 = check_provider(config[network]["rpcs"])
            account = config[network]["contracts"]["oracle_keeper"]
            balance_wei = w3.eth.getBalance(account)
            ether_balance = balance_wei * 10 ** -18

            if "oracle" not in oracle_status:
                oracle_status["oracle"] = {}

            oracle_status["oracle"][network] = {
                "value": round(ether_balance, 4),
                "address": account
            }

    if oracle_status:
        update_keepers_data(oracle_status)


def update_health_factor():
  
    networks = list(config.keys())
    for network in networks:
      if config[network]["lend_active"] == True:
        w3 = check_provider(config[network]["rpcs"])
        
        # Assuming borrowers.json structure is a list of dicts with at least 'account' and 'network' keys
        lendingPool = w3.eth.contract(address=config[network]["contracts"]["lendingPool"], abi=abis.lendingPool())

        updated_borrowers = []
        for borrower in borrowers:
            if borrower["network"] == network:
                # Fetch the current health factor
                account_data = lendingPool.functions.getUserAccountData(borrower["account"]).call()
                health_factor = round(account_data[5] * 10 ** -18, 5)  # Adjusted for scale

                # Update the borrower's health factor
                borrower["healthFactor"] = health_factor
                updated_borrowers.append(borrower)
            else:
                # Keep borrowers from other networks unchanged
                updated_borrowers.append(borrower)
        
        # Write the updated list back to borrowers.json
        write_to_json(updated_borrowers, "json/borrowers.json")

        print("Health factors updated.")

def update_borrowers():

    update_health_factor()
  
    networks = list(config.keys())
    for network in networks:
      if config[network]["lend_active"] == True:
        w3 = check_provider(config[network]["rpcs"])
        
        last_synced_block = blocks_synced[network]
        lendingPool = w3.eth.contract(address=config[network]["contracts"]["lendingPool"], abi=abis.lendingPool())
        
        all_borrowers = []
        while last_synced_block <= w3.eth.blockNumber:
            print(last_synced_block, "last_synced_block")  # Debugging
            
            # Get borrow events from the lending pool contract
            events = lendingPool.events.Borrow().getLogs(fromBlock=last_synced_block)

            # Extract unique users from events
            unique_users = {event['args']['onBehalfOf'] for event in events}

            # Add unique users to the list of all borrowers
            all_borrowers.extend(user for user in unique_users if user not in all_borrowers)

            # Update last_synced_block based on conditions
            if last_synced_block + BLOCK_INCREMENT < w3.eth.blockNumber:
                last_synced_block += BLOCK_INCREMENT
                
            elif w3.eth.blockNumber - last_synced_block < MIN_BLOCK_DIFF:
                blocks_synced[network] = last_synced_block
                update_synced_block()
                break
            
            else:
                last_synced_block = w3.eth.blockNumber
        
        # Retrieve user positions and store in a list
        user_positions = [{"account": borrower,
                          "healthFactor": lendingPool.functions.getUserAccountData(borrower).call()[5] * 10 ** -18,
                          "network": network} for borrower in all_borrowers]

        write_to_json(user_positions, "json/borrowers.json")


def get_total_borrowed_and_supplied_usd():
  for network in config:
    if not config[network].get("lend_active", False):
        continue
        
    w3 = check_provider(config[network]["rpcs"])
    for asset_symbol in config[network]["lending_tokens"]:
        
        asset = config[network]["lending_tokens"][asset_symbol]["token"]
        decimals = config[network]["lending_tokens"][asset_symbol]["decimals"]
        o_token_address = config[network]["lending_tokens"][asset_symbol]["oToken"]
        debt_token_address = config[network]["lending_tokens"][asset_symbol]["debtToken"]
        
        total_borrow = get_token_supply(w3, debt_token_address)
        total_supply = get_token_supply(w3, o_token_address)
        tokenPrice = fetch_token_prices(network, w3, asset) 

        # Calculate USD values
        lend_yields[network][asset_symbol]["total_borrow_usd"] = total_borrow * tokenPrice * (10 ** -decimals)
        lend_yields[network][asset_symbol]["total_supply_usd"] = total_supply * tokenPrice * (10 ** -decimals)
        lend_yields[network][asset_symbol]["tvl_usd"] = lend_yields[network][asset_symbol]["total_supply_usd"] - lend_yields[network][asset_symbol]["total_borrow_usd"]
        
        update_lending_yields()
        


def update_interest_rates():
  for network in config:
    if not config[network].get("lend_active", False):
        continue
        
    w3 = check_provider(config[network]["rpcs"])
    
    if network not in lend_yields:
        lend_yields[network] = {}

    for asset_symbol in config[network]["lending_tokens"]:
        if asset_symbol not in lend_yields[network]:
            lend_yields[network][asset_symbol] = {"apy_base": 0,
                                                  "apy_base_borrow": 0, 
                                                  "apy_reward": 0, 
                                                  "apy_reward_borrow": 0,
                                                  "total_deposit_yield": 0,
                                                  "total_borrow_yield": 0}

        # Update rates using lending and borrowing base rates
        variable_borrow_rate = update_borrow_rate(w3, network, asset_symbol)
        liquidity_rate = update_liquidity_rate(w3, network, asset_symbol)
        
        # Convert APR to APY for both deposit and borrow rates
        percent_deposit_apy = 100 * ((1 + liquidity_rate / RAY / DAYS_PER_YEAR) ** DAYS_PER_YEAR - 1)
        percent_variable_borrow_apy = 100 * ((1 + variable_borrow_rate / RAY / DAYS_PER_YEAR) ** DAYS_PER_YEAR - 1)
        
        # Store APY as a percentage
        lend_yields[network][asset_symbol]["apy_base"] = percent_deposit_apy
        lend_yields[network][asset_symbol]["apy_base_borrow"] = percent_variable_borrow_apy 
        
        # Reward calculation requires correct decimal adjustment
        reward_token = config[network]["contracts"]["lending_reward_token"]
        reward_token_price = fetch_token_prices(network, w3, reward_token)
        token = config[network]["lending_tokens"][asset_symbol]["token"]
        token_price = fetch_token_prices(network, w3, token)
        token_decimals = config[network]["lending_tokens"][asset_symbol]["decimals"]

        o_token_address = config[network]["lending_tokens"][asset_symbol]["oToken"]
        debt_token_address = config[network]["lending_tokens"][asset_symbol]["debtToken"]
        
        o_token_supply = get_token_supply(w3, o_token_address)
        debt_token_supply = get_token_supply(w3, debt_token_address)

        o_token_emission_per_second = get_rewards_per_second(w3, network, config[network]["lending_tokens"][asset_symbol]["oToken"])
        debt_token_emission_per_second = get_rewards_per_second(w3, network, config[network]["lending_tokens"][asset_symbol]["debtToken"])

        # Applying decimal adjustment to token supply and emission rates
        adjusted_o_token_supply = o_token_supply / (10 ** token_decimals)
        adjusted_debt_token_supply = debt_token_supply / (10 ** token_decimals)

        percentDepositAPR = (o_token_emission_per_second * SECONDS_PER_YEAR * reward_token_price) / (adjusted_o_token_supply * token_price * LEND_ORACLE_PRECISION)
        percentBorrowAPR = (debt_token_emission_per_second * SECONDS_PER_YEAR * reward_token_price) / (adjusted_debt_token_supply * token_price * LEND_ORACLE_PRECISION)

        lend_yields[network][asset_symbol]["apy_reward"] = percentDepositAPR
        lend_yields[network][asset_symbol]["apy_reward_borrow"] = percentBorrowAPR
        
        lend_yields[network][asset_symbol]["total_deposit_yield"] = percentDepositAPR + percent_deposit_apy
        lend_yields[network][asset_symbol]["total_borrow_yield"] = percentBorrowAPR - percent_variable_borrow_apy
        
        update_lending_yields()
        
  
def warnings():

    with open("json/data.json", "r") as jsonFile:
        data = json.load(jsonFile)
        
    # Lending Health Factors
    health_warning_set = False
    for borrower in borrowers:
        if borrower['healthFactor'] < 1:
            health_warning_set = True
            break
    store_data["warnings"]["health_factors"] = health_warning_set
    update_data()

    # Oracle Keeper Balances
    oracle_balances = data["keepers"]["oracle"]
    oracle_warning = oracle_balances["base"]["value"] < 0.005 or \
                     oracle_balances["telos"]["value"] < 20 or \
                     oracle_balances["meter"]["value"] < 5
    store_data["warnings"]["oracle_keepers"] = oracle_warning
    update_data()

    # Staking Keeper Balances
    staking_balances = data["keepers"]["staking"]
    staking_warning = staking_balances["fuse"]["value"] < 20 or \
                      staking_balances["telos"]["value"] < 20 or \
                      staking_balances["meter"]["value"] < 5
    store_data["warnings"]["staking_keepers"] = staking_warning
    update_data()
    

    # Lending Rewards End Times
    lending_rewards = data["incentives"]["lending"]
    lending_warning = lending_rewards["meter"] < 7 or \
                      lending_rewards["telos"] < 7
    store_data["warnings"]["lending_rewards"] = lending_warning
    update_data()

    # Mint Rewards End Times
    mint_rewards = data["incentives"]["mint"]
    mint_warning = mint_rewards["fuse"] < 7 or \
                   mint_rewards["telos"] < 7
    store_data["warnings"]["mint_rewards"] = mint_warning
    update_data()
    
    
    latestBlockNumber = fetchOmniDexBP()
    if latestBlockNumber is None:
        store_data["warnings"]["block_producer"] = True
        update_data()
    else:
        w3 = check_provider(config["telos"]["rpcs"])
        if (w3.eth.blockNumber - latestBlockNumber) > 1000:
            store_data["warnings"]["block_producer"] = True
            update_data()
        else:
            store_data["warnings"]["block_producer"] = False
            update_data()

"""
  Other warnings can be made by reading the state of contracts and validating it's 
  the correct state we expect. E.g staking keeper should not have more than $2 balance
  """

def safe_call(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print(e)
        return None

def updateAllParams():
    safe_call(getAllCoinGeckoPrices)
    safe_call(fetch_trove_count)
    safe_call(fetch_total_tvl)
    safe_call(fetch_mst_stats)
    safe_call(fetch_stability_pool_yield)
    safe_call(check_lending_incentives_end_time)
    safe_call(check_mint_incentives_end_time)
    safe_call(check_keeper_balances)
    safe_call(check_oracle_balances)
    safe_call(update_borrowers)
    safe_call(warnings)
    safe_call(update_interest_rates)
    safe_call(get_total_borrowed_and_supplied_usd)

  

"""
To Do: Add additional checks to staking keeper to ensure rewards are
infact being harvested and sent to the staking contract
"""

"""
Design an oracle that is compatible with Chainlink, Supra, DIA and Pyth
Additionally, it's compatible with Lend, Mint and Trade
Easy to configure and modular design.
"""
