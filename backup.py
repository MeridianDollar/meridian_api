from api.config import *

def getPerpetualsVolume():
  try:
    startFrom = START_STATS_TIMESTAMP
    end = int(time.time())
    
    totalVolume = f'''
          query {{
        volumeStats(
          first: 1000
          orderDirection: desc
          where: {{period: daily, id_gte: {startFrom}, id_lt: {end}}}
          subgraphError: allow
          orderBy: id
        ) {{
          swap
          mint
          margin
          liquidation
          burn
        }}
      }}
      '''

    headers = {'Content-Type': 'application/json'}
    body = json.dumps({'query': totalVolume})
    
    response = requests.post(SUBGRAPH_URL, headers=headers, data=body)
    data = response.json()['data']['volumeStats']

    totalVolume = 0
    for item in data:
        for key, value in item.items():
            totalVolume = totalVolume + int(value)
            
    formatVolume = int(totalVolume)
    return float(formatVolume)
  
    #store_data["volume_data"]["total_volume"] = str(formatVolume*10**30); update_data()
  except: pass
  

def getDailyVolume():
  try:
    startFrom = START_STATS_TIMESTAMP
    end = int(time.time())
    
    dailyVolume = f'''
      query {{
    volumeStats(
      first: 1
      orderDirection: desc
      where: {{period: daily, id_gte: {startFrom}, id_lt: {end}}}
      subgraphError: allow
      orderBy: id
    ) {{
      swap
      mint
      margin
      liquidation
      burn
    }}
  }}

  '''

    headers = {'Content-Type': 'application/json'}
    body = json.dumps({'query': dailyVolume})
    
    response = requests.post(SUBGRAPH_URL, headers=headers, data=body)
    data = response.json()['data']['volumeStats']

    dailyVolume = 0
    for item in data:
        for key, value in item.items():
            dailyVolume = dailyVolume + int(value)
            
    formatDailyVolume = int(dailyVolume*10**-30)
    
    store_data["volume_data"]["daily_volume"] = str(formatDailyVolume *10**30); update_data()
  except:
    pass



def getFeeStats(): 
  try:
    end = int(time.time())
    startFrom = end - (86400 * 7)
    feesStats = f'''
      query {{
      feeStats(
        first: 1000
        orderBy: id
        orderDirection: desc
        where: {{period: daily, id_gte: {startFrom}, id_lt: {end}}}
        subgraphError: allow
      ) {{
        id
        marginAndLiquidation
        swap
        mint
        burn
      }}
    }}
    '''
    headers = {'Content-Type': 'application/json'}
    body = json.dumps({'query': feesStats})
    
    response = requests.post(SUBGRAPH_URL, headers=headers, data=body)
    data = response.json()['data']['feeStats']
    
    fees = 0
    for item in data:
        for key, value in item.items():
            fees = fees + int(value)
          
          
    perpetualsFees = fees*10**-30
    
    # ammFees = 171394 #getAMMVolume() * 0.0025
    
    totalFees = perpetualsFees
    
    
    store_data["fees_summary"]["totalFees"] = int(totalFees); update_data()
    store_data["fees_summary"]["weeklyFees"] = int(perpetualsFees); update_data()
    store_data["fees_summary"]["lastUpdatedAt"] = startFrom; update_data()
  except:
    pass
  
def getTradingStats():
  try:
    startFrom = START_STATS_TIMESTAMP
    end = int(time.time())
    tradingStats = f'''
      query {{
      tradingStats(
        first: 1
        orderBy: timestamp
        orderDirection: desc
        where: {{period: daily, id_gte: {startFrom} , id_lt: {end}}}
        subgraphError: allow
      ) {{
        timestamp
        profit
        loss
        profitCumulative
        lossCumulative
        longOpenInterest
        shortOpenInterest
      }}
    }}

  '''

    headers = {'Content-Type': 'application/json'}
    body = json.dumps({'query': tradingStats})
    
    response = requests.post(SUBGRAPH_URL, headers=headers, data=body)
    data = response.json()['data']['tradingStats']
    
    result = {
      'profit': 0,
      'loss': 0,
      'profitCumulative': 0,
      'lossCumulative': 0,
      'longOpenInterest': 0,
      'shortOpenInterest': 0
  }

    for d in data:
        result['profit'] += int(d['profit'])
        result['loss'] += int(d['loss'])
        result['profitCumulative'] += int(d['profitCumulative'])
        result['lossCumulative'] += int(d['lossCumulative'])
        result['longOpenInterest'] += int(d['longOpenInterest'])
        result['shortOpenInterest'] += int(d['shortOpenInterest'])

    store_data["position_stats"]["totalLongPositionSizes"] = str(int(result['longOpenInterest'])); update_data()
    store_data["position_stats"]["totalShortPositionSizes"] = str(int(result['shortOpenInterest'])); update_data()
  except:
    pass

def getAMMVolume():
  try:
    Volume = '''
    {
        uniswapFactory(id: "0x7a2A35706f5d1CeE2faa8A254dd6F6D7d7Becc25") {
        id
        untrackedVolumeUSD
        }
    } '''

    headers = {'Content-Type': 'application/json'}
    body = json.dumps({'query': Volume})
    
    response = requests.post(EXCHANGE_SUBGRAPH_URL, headers=headers, data=body)
    
    totalVolume = response.json()["data"]["uniswapFactory"]["untrackedVolumeUSD"]
    
    return float(totalVolume)
    
    #store_data["volume_data"]["amm_volume"] = str(totalVolume *10**30); update_data()
  except:pass

def getAMMUserCount():
  try:
    batch_users = 1000
    unique_user_count = 0
    user_addresses = []
    while True:
        Users = f'''
        query {{
        users(first: {batch_users} skip: {unique_user_count} )  {{
            id
        }}
        }}
        '''
        headers = {'Content-Type': 'application/json'}
        body = json.dumps({'query': Users})
        
        response = requests.post(EXCHANGE_SUBGRAPH_URL, headers=headers, data=body)
        
        data = response.json()['data']["users"]
        
        if not data:
            break
        
     
        address_list = [d['id'] for d in data]
        
        user_addresses= user_addresses + address_list
        unique_user_count += int(len(data))

    return unique_user_count, user_addresses 
  except:
    pass
 
def getPerpetualsUniqueUsers():

  try:
      Users = '''query
      {
      userStat(id: "total") {
        id
        uniqueCount
      }
    }
      '''
      headers = {'Content-Type': 'application/json'}
      body = json.dumps({'query': Users})
      
      response = requests.post(SUBGRAPH_URL, headers=headers, data=body)
      
      data = response.json()['data']["userStat"]["uniqueCount"]
      return data
  except:
    pass


def getTotalUsers():
  try:
    amm_user_count = 2158 #unique_user_count, user_addresses = getAMMUserCount()
    totalUsers = amm_user_count + getPerpetualsUniqueUsers() #+ getAMMUserCount()
    store_data["user_data"]["total_users"] = str(totalUsers *10**30); update_data()

  except:
    totalUsers = getPerpetualsUniqueUsers()
    store_data["user_data"]["total_users"] = str(totalUsers *10**30); update_data()

  
def getTotalVolume():
  try:
    store_data["volume_data"]["total_volume"] = str(int(getPerpetualsVolume())); update_data()
  except: pass


def getTotalUsers():
  try:
    amm_user_count = 2158 #unique_user_count, user_addresses = getAMMUserCount()
    totalUsers = amm_user_count + getPerpetualsUniqueUsers() #+ getAMMUserCount()
    store_data["user_data"]["total_users"] = str(totalUsers *10**30); update_data()

  except:
    totalUsers = getPerpetualsUniqueUsers()
    store_data["user_data"]["total_users"] = str(totalUsers *10**30); update_data()
    
    

def getUSDMPrice():
  networks = list(config.keys())
  
  for network in networks:
    w3 = check_provider(config[network]["rpcs"])

    if network =="telos": 
      nativeToken_contract = w3.eth.contract(address=config[network]["contracts"]["nativeTokenUSDUniV3USDPool"], abi=abis.swapsiclePair())
      USDMTLOS_contract = w3.eth.contract(address=config[network]["contracts"]["nativeTokenUSDMUniV3USDPool"], abi=abis.swapsiclePair())
      nativeToken_slot0 = nativeToken_contract.functions.prevTickGlobal().call()
      nativeToken_value = 1 / (BASE ** nativeToken_slot0) * 10 ** 12
      usdm_slot0 = USDMTLOS_contract.functions.prevTickGlobal().call()
      USDM_value = (BASE ** usdm_slot0) 
      print(USDM_value, "USDM")  
      telos_usdmPrice = nativeToken_value * USDM_value

  store_data["telos_usdm_price"] = telos_usdmPrice 
  update_data()
  
  
def getMSTPoolLiquidity():
  # For this function we will call balanceOf() for the LP of the tokens within the pool
  mst_price = get_mst_price()
  networks = list(config.keys())
  
  for network in networks:
    w3 = check_provider(config[network]["rpcs"])
    
    if network =="base":
      mst_token = w3.eth.contract(address=config[network]["contracts"]["MST"], abi=abis.token())
      weth_token = w3.eth.contract(address=config[network]["contracts"]["WETH"], abi=abis.token())

      mst_balance = mst_token.functions.balanceOf(config[network]["contracts"]["nativeTokenMSTUniV3USDPool"]).call()
      weth_balance = weth_token.functions.balanceOf(config[network]["contracts"]["nativeTokenMSTUniV3USDPool"]).call()

      mst_usd = (mst_balance * 10 ** -18) * mst_price
      weth_usd = (weth_balance * 10 ** -18) * float(oracle_prices[config[network]["coingecko_id"]]['usd'])    
      total_liquidity = mst_usd + weth_usd
      
      store_data["uniswap_base_mst_liquidity"] = total_liquidity; update_data()

    if network == "telos": 
        mst_contract = w3.eth.contract(address=config[network]["contracts"]["MST"], abi=abis.token())
        wtlos_contract = w3.eth.contract(address=config[network]["contracts"]["WTLOS"], abi=abis.token())
        usdm_contract = w3.eth.contract(address=config[network]["contracts"]["USDM"], abi=abis.token())
        usdc_contract = w3.eth.contract(address=config[network]["contracts"]["USDC"], abi=abis.token())

        # Get MST,WTLOS and USDM balances
        mst_balance_mst_pool = mst_contract.functions.balanceOf(config[network]["contracts"]["nativeTokenMSTUniV3USDPool"]).call()
        usdm_balance_usdm_pool = usdm_contract.functions.balanceOf(config[network]["contracts"]["nativeTokenUSDMUniV3USDPool"]).call()
        wtlos_balance_mst_pool = wtlos_contract.functions.balanceOf(config[network]["contracts"]["nativeTokenMSTUniV3USDPool"]).call()
        wtlos_balance_usdm_pool = wtlos_contract.functions.balanceOf(config[network]["contracts"]["nativeTokenUSDMUniV3USDPool"]).call()
        usdc_balance_usdm_usdc_pool = usdc_contract.functions.balanceOf(config[network]["contracts"]["USDCUSDMUniV3USDPool"]).call()
        usdm_balance_usdm_usdc_pool = usdm_contract.functions.balanceOf(config[network]["contracts"]["USDCUSDMUniV3USDPool"]).call()

        # Calculate MST/TLOS liquidity
        wtlos_price = oracle_prices[config[network]["coingecko_id"]]['usd']
        mst_usd = (mst_balance_mst_pool * 10 ** -18) * mst_price
        wtlos_usd_mst_pool = (wtlos_balance_mst_pool * 10 ** -18) * wtlos_price
        total_mst_tlos_liquidity = mst_usd + wtlos_usd_mst_pool

        # Calculate USDM/TLOS liquidity
        wtlos_price = oracle_prices[config[network]["coingecko_id"]]['usd']
        usdm_usd = (usdm_balance_usdm_pool * 10 ** -18)
        wtlos_usd_usdm_pool = (wtlos_balance_usdm_pool * 10 ** -18) * wtlos_price
        total_usdm_tlos_liquidity = usdm_usd + wtlos_usd_usdm_pool
        
        # Calculate USDM/USDC liquidity
        usdm_usd = (usdm_balance_usdm_usdc_pool * 10 ** -18)
        usdc_usd = (usdc_balance_usdm_usdc_pool * 10 ** -6)
        total_usdm_usdc_liquidity = usdm_usd + usdc_usd

        # Store data
        store_data["swapsicle_telos_mst_liquidity"] = total_mst_tlos_liquidity
        store_data["swapsicle_telos_usdm_liquidity"] = total_usdm_tlos_liquidity
        store_data["swapsicle_telos_usdc_usdm_liquidity"] = total_usdm_usdc_liquidity

        # Update data
        update_data()

    if network =="fuse": 
        mst_token = w3.eth.contract(address=config[network]["contracts"]["MST"], abi=abis.token())
        wfuse_token = w3.eth.contract(address=config[network]["contracts"]["WFUSE"], abi=abis.token())
        usdm_token = w3.eth.contract(address=config[network]["contracts"]["USDM"], abi=abis.token())

        mst_balance_mst_pool = mst_token.functions.balanceOf(config[network]["contracts"]["nativeTokenMSTUniV3USDPool"]).call()
        wfuse_balance_mst_pool = wfuse_token.functions.balanceOf(config[network]["contracts"]["nativeTokenMSTUniV3USDPool"]).call()
        usdm_balance_usdm_pool = usdm_token.functions.balanceOf(config[network]["contracts"]["nativeTokenUSDMUniV3USDPool"]).call()
        wfuse_balance_usdm_pool = wfuse_token.functions.balanceOf(config[network]["contracts"]["nativeTokenUSDMUniV3USDPool"]).call()

        # Calculate MST/FUSE liquidity
        mst_usd = (mst_balance_mst_pool * 10 ** -18) * mst_price
        wfuse_usd = (wfuse_balance_mst_pool * 10 ** -18) * float(oracle_prices[config[network]["coingecko_id"]]['usd'])    
        total_mst_fuse_liquidity = mst_usd + wfuse_usd
        
        # Calculate USDM/FUSE liquidity
        usdm_usd = (usdm_balance_usdm_pool * 10 ** -18) 
        wfuse_usd = (wfuse_balance_usdm_pool * 10 ** -18) * float(oracle_prices[config[network]["coingecko_id"]]['usd'])    
        total_usdm_fuse_liquidity = usdm_usd + wfuse_usd
        
        store_data["voltage_fuse_mst_liquidity"] = total_mst_fuse_liquidity; update_data()
        store_data["voltage_fuse_usdm_liquidity"] = total_usdm_fuse_liquidity; update_data()
        
        
    
def check_salaries():
  w3 = check_provider(config["base"]["rpcs"])
  mst_token = w3.eth.contract(address=config["base"]["contracts"]["MST"], abi=abis.token())
  mst_balance = mst_token.functions.balanceOf(config["base"]["contracts"]["salaryDistributor"]).call()
  adjusted_balance = mst_balance * 10 ** -18
  
  mst_balance = {
      "salary_balance": adjusted_balance,
      "timestamp": time.time()
  }
  balance_data["salary_balance"] = mst_balance;  updateMSTBalance()



def fetch_total_tvl():
    getAllCoinGeckoPrices()
    networks = list(config.keys())
    total_tvl_usd = 0
    number_of_troves = 0

    for network in networks:
      if config[network]["mint_active"] == True:
        try:
            w3 = check_provider(config[network]["rpcs"])
            collateral_price = float(oracle_prices[config[network]["coingecko_id"]]['usd'])      
            trove_manager_contract = w3.eth.contract(address=config[network]["contracts"]["troveManager"], abi=abis.troveManager())
            tvl = trove_manager_contract.functions.getEntireSystemColl().call()
            troves_count = trove_manager_contract.functions.getTroveOwnersCount().call()
            tvl_usd = (tvl * 10 ** -18) * collateral_price
            total_tvl_usd += tvl_usd
            number_of_troves += troves_count
            
        except Exception as e:
            print(f"Error fetching TVL for {network}: {e}")
    
    telos_lending_tvl = fetchOTokenUSDSupply()  
    total_tvl_usd = total_tvl_usd + telos_lending_tvl
    store_data["total_tvl"] = int(total_tvl_usd)
    store_data["number_of_troves"] = int(number_of_troves)
    
    update_data()
    
    
def get_mst_price():
  networks = list(config.keys())
  
  mstPrices = []
  for network in networks:
    w3 = check_provider(config[network]["rpcs"])
    
    if network =="base":
      nativeToken_contract = w3.eth.contract(address=config[network]["contracts"]["nativeTokenUSDUniV3USDPool"], abi=abis.uniPair())
      MSTETH_contract = w3.eth.contract(address=config[network]["contracts"]["nativeTokenMSTUniV3USDPool"], abi=abis.uniPair())
      nativeToken_slot0 = nativeToken_contract.functions.slot0().call()
      nativeToken_value = (BASE ** nativeToken_slot0[1]) * 10 ** 12
      mst_slot0 = MSTETH_contract.functions.slot0().call()
      MST_value = 1/ (BASE ** mst_slot0[1])
      base_mstPrice = nativeToken_value/MST_value
      mstPrices.append(base_mstPrice)

    if network =="telos": 
      nativeToken_contract = w3.eth.contract(address=config[network]["contracts"]["nativeTokenUSDUniV3USDPool"], abi=abis.swapsiclePair())
      MSTTLOS_contract = w3.eth.contract(address=config[network]["contracts"]["nativeTokenMSTUniV3USDPool"], abi=abis.swapsiclePair())
      nativeToken_slot0 = nativeToken_contract.functions.prevTickGlobal().call()
      nativeToken_value = 1 / (BASE ** nativeToken_slot0) * 10 ** 12
      mst_slot0 = MSTTLOS_contract.functions.prevTickGlobal().call()
      MST_value = (BASE ** mst_slot0) 
      telos_mstPrice = nativeToken_value * MST_value
      mstPrices.append(telos_mstPrice)

  averageMSTPrice = sum(mstPrices) / len(mstPrices)
  
  store_data["mst_price"] = averageMSTPrice
  store_data["mst_price_30"] = int(averageMSTPrice*10**30)
  
  update_data()
  
  return averageMSTPrice


def fetch_all_o_token_data(w3):
    oTokens = []
    debtTokens =[]
    decimals = []
    lendingPool =  w3.eth.contract(address=config["telos"]["contracts"]["lendingPool"], abi=abis.lendingPool())
    for token_name, token_address in config["telos"]["lending_tokens"].items():      
        reserveData = lendingPool.functions.getReserveData(config["telos"]["lending_tokens"][token_name]["address"]).call()  
        debtTokens.append(reserveData[9])
        oTokens.append(reserveData[7])
        decimals.append(config["telos"]["lending_tokens"][token_name]["decimals"])
    return oTokens, debtTokens, decimals
  
  
def fetchTokenPrices(w3):
    tokenPrices = []
    _meridianOracle =  w3.eth.contract(address=config["telos"]["contracts"]["meridianOracle"], abi=abis.meridianOracle())
    for token_name, token_address in config["telos"]["lending_tokens"].items(): 
        price = _meridianOracle.functions.getAssetPrice(config["telos"]["lending_tokens"][token_name]["address"]).call()  
        tokenPrices.append(price * 10 ** -8)
    return tokenPrices

def fetchAllTokenBalance(w3):
    oTokens, debtTokens, decimals = fetch_all_o_token_data(w3)
    
    oTokenBalances = []
    debtTokenBalances = []
    for index, token in enumerate(oTokens):
        _oToken =  w3.eth.contract(address=token, abi=abis.oToken())
        balance = _oToken.functions.totalSupply().call()  
        oTokenBalances.append(balance * 10 ** - decimals[index])
        
    for index, token in enumerate(debtTokens):
        _debtToken =  w3.eth.contract(address=token, abi=abis.oToken())
        balance = _debtToken.functions.totalSupply().call()  
        debtTokenBalances.append(balance * 10 ** - decimals[index])
        
    return oTokenBalances, debtTokenBalances

def fetchOTokenUSDSupply():
    w3 = check_provider(config["telos"]["rpcs"])
    oTokenSupply, debtTokenSupply = fetchAllTokenBalance(w3)
    tokenPrices = fetchTokenPrices(w3)
    result = [a * b for a, b in zip(oTokenSupply, tokenPrices)]
    return sum(result)

def fetchTokenUSDSupply():
    w3 = check_provider(config["telos"]["rpcs"])
    oTokenSupply, debtTokenSupply = fetchAllTokenBalance(w3)
    tokenPrices = fetchTokenPrices(w3)
    oTokenUSD = [a * b for a, b in zip(oTokenSupply, tokenPrices)]
    debtTokenUSD = [a * b for a, b in zip(debtTokenSupply, tokenPrices)]
    return sum(oTokenUSD) + sum(debtTokenUSD)
  
"""
def getBatchPriceDataFromCoinGecko():
    coinGeckoIDs = []
    for token in config["asset_symbols"]:
        coinGeckoIDs.append(config[token]["coingecko_id"])
    coingeckoApiClient = CoinGeckoAPI()
    assetPrice = coingeckoApiClient.get_price(ids=coinGeckoIDs, vs_currencies='usd')
     
    for token in config["asset_symbols"]:
        parsedAssetPrice = assetPrice[config[token]["coingecko_id"]]["usd"]
        data[token]["tokenPrice"] = parsedAssetPrice; update_data()
        
"""